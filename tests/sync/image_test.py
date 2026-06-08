import datetime
from unittest import mock

import pytest
from google.protobuf import timestamp_pb2
from opentelemetry.trace import SpanKind

from xai_sdk import Client
from xai_sdk.cost import USD_PER_TICK
from xai_sdk.image import BaseImageResponse, ImageFormat
from xai_sdk.proto import batch_pb2, image_pb2, usage_pb2

from .. import server


@pytest.fixture(scope="session")
def client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


@pytest.fixture
def image_asset():
    return server.read_image()


def test_base64(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-2-image", image_format="base64")

    with pytest.warns(DeprecationWarning, match="BaseImageResponse.prompt is deprecated"):
        assert response.prompt == ""
    assert image_asset == response.image


def test_url(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-2-image", image_format="url")

    with pytest.warns(DeprecationWarning, match="BaseImageResponse.prompt is deprecated"):
        assert response.prompt == ""
    assert image_asset == response.image


def test_batch(client: Client, image_asset: bytes):
    responses = client.image.sample_batch(prompt="foo", model="grok-2-image", n=2, image_format="base64")

    assert len(responses) == 2

    for r in responses:
        with pytest.warns(DeprecationWarning, match="BaseImageResponse.prompt is deprecated"):
            assert r.prompt == ""
        assert image_asset == r.image


def test_sample_passes_aspect_ratio_and_resolution(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-2-image",
        aspect_ratio="1:1",
        resolution="1k",
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("aspect_ratio")
    assert request.aspect_ratio == image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_1_1
    assert request.HasField("resolution")
    assert request.resolution == image_pb2.ImageResolution.IMG_RESOLUTION_1K


def test_sample_batch_passes_aspect_ratio_and_resolution(client: Client):
    server.clear_last_image_request()

    client.image.sample_batch(
        prompt="foo",
        model="grok-2-image",
        n=2,
        aspect_ratio="16:9",
        resolution="1k",
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("aspect_ratio")
    assert request.aspect_ratio == image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_16_9
    assert request.HasField("resolution")
    assert request.resolution == image_pb2.ImageResolution.IMG_RESOLUTION_1K


def test_sample_passes_image_url(client: Client):
    server.clear_last_image_request()

    input_image_url = "https://example.com/image.jpg"
    client.image.sample(prompt="foo", model="grok-imagine-image", image_url=input_image_url)

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("image")
    assert request.image.image_url == input_image_url
    assert request.image.detail == image_pb2.ImageDetail.DETAIL_AUTO


def test_sample_passes_image_urls(client: Client):
    server.clear_last_image_request()

    input_image_urls = [
        "https://example.com/image1.jpg",
        "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
    ]
    client.image.sample(prompt="foo", model="grok-imagine-image", image_urls=input_image_urls)

    request = server.get_last_image_request()
    assert request is not None
    assert [image.image_url for image in request.images] == input_image_urls
    assert all(image.detail == image_pb2.ImageDetail.DETAIL_AUTO for image in request.images)


def test_sample_batch_passes_image_urls(client: Client):
    server.clear_last_image_request()

    input_image_urls = [
        "https://example.com/image1.jpg",
        "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
    ]
    client.image.sample_batch(prompt="foo", model="grok-imagine-image", n=2, image_urls=input_image_urls)

    request = server.get_last_image_request()
    assert request is not None
    assert [image.image_url for image in request.images] == input_image_urls
    assert all(image.detail == image_pb2.ImageDetail.DETAIL_AUTO for image in request.images)


def test_sample_rejects_both_image_fields(client: Client):
    input_image_url = "https://example.com/image.jpg"
    input_image_urls = ["https://example.com/image1.jpg"]

    with pytest.raises(ValueError, match="image_url/image_file_id or image_urls/image_file_ids"):
        client.image.sample(
            prompt="foo",
            model="grok-imagine-image",
            image_url=input_image_url,
            image_urls=input_image_urls,
        )


def test_sample_batch_rejects_both_image_fields(client: Client):
    input_image_url = "https://example.com/image.jpg"
    input_image_urls = ["https://example.com/image1.jpg"]

    with pytest.raises(ValueError, match="image_url/image_file_id or image_urls/image_file_ids"):
        client.image.sample_batch(
            prompt="foo",
            model="grok-imagine-image",
            n=2,
            image_url=input_image_url,
            image_urls=input_image_urls,
        )


@mock.patch("xai_sdk.sync.image.tracer")
@pytest.mark.parametrize("image_format", ["url", "base64"])
def test_sample_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: Client, image_format: ImageFormat
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    user = "test-user-123"
    response = client.image.sample(
        prompt="A beautiful sunset", model="grok-imagine-image", image_format=image_format, user=user
    )

    expected_request_attributes = {
        "gen_ai.prompt": "A beautiful sunset",
        "gen_ai.operation.name": "generate_image",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "image",
        "gen_ai.request.model": "grok-imagine-image",
        "gen_ai.request.image.format": image_format,
        "gen_ai.request.image.count": 1,
        "user_id": user,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample grok-imagine-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-image",
        "gen_ai.response.image.format": image_format,
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.0.image.respect_moderation": response.respect_moderation,
    }

    if image_format == "url":
        expected_response_attributes["gen_ai.response.0.image.url"] = response.url
    else:
        expected_response_attributes["gen_ai.response.0.image.base64"] = response.base64

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.sync.image.tracer")
@pytest.mark.parametrize("image_format", ["url", "base64"])
def test_sample_creates_span_without_sensitive_attributes_when_disabled(
    mock_tracer: mock.MagicMock, client: Client, image_format: ImageFormat
):
    """Test that sensitive attributes are not included when XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES is set."""
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    user = "test-user-123"
    with mock.patch.dict("os.environ", {"XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES": "1"}):
        client.image.sample(prompt="A beautiful sunset", model="grok-2-image", image_format=image_format, user=user)

    expected_request_attributes = {
        "gen_ai.operation.name": "generate_image",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "image",
        "gen_ai.request.model": "grok-2-image",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample grok-2-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-2-image",
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.sync.image.tracer")
@pytest.mark.parametrize("image_format", ["url", "base64"])
def test_sample_batch_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: Client, image_format: ImageFormat
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    user = "test-user-123"
    responses = client.image.sample_batch(
        prompt="A beautiful sunset", model="grok-imagine-image", n=3, image_format=image_format, user=user
    )

    assert len(responses) == 3

    expected_request_attributes = {
        "gen_ai.prompt": "A beautiful sunset",
        "gen_ai.operation.name": "generate_image",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "image",
        "gen_ai.request.model": "grok-imagine-image",
        "gen_ai.request.image.format": image_format,
        "gen_ai.request.image.count": 3,
        "user_id": user,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample_batch grok-imagine-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-image",
        "gen_ai.response.image.format": image_format,
        "gen_ai.usage.input_tokens": responses[0].usage.prompt_tokens,
        "gen_ai.usage.output_tokens": responses[0].usage.completion_tokens,
        "gen_ai.usage.total_tokens": responses[0].usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": responses[0].usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": responses[0].usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": responses[0].usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": responses[0].usage.prompt_image_tokens,
        "gen_ai.response.0.image.respect_moderation": responses[0].respect_moderation,
        "gen_ai.response.1.image.respect_moderation": responses[1].respect_moderation,
        "gen_ai.response.2.image.respect_moderation": responses[2].respect_moderation,
    }

    if image_format == "url":
        expected_response_attributes["gen_ai.response.0.image.url"] = responses[0].url
        expected_response_attributes["gen_ai.response.1.image.url"] = responses[1].url
        expected_response_attributes["gen_ai.response.2.image.url"] = responses[2].url
    else:
        expected_response_attributes["gen_ai.response.0.image.base64"] = responses[0].base64
        expected_response_attributes["gen_ai.response.1.image.base64"] = responses[1].base64
        expected_response_attributes["gen_ai.response.2.image.base64"] = responses[2].base64

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


# Tests for image.prepare() batch request method


def test_create_returns_batch_request(client: Client):
    """Test that create() returns a BatchRequest proto."""
    batch_req = client.image.prepare(
        prompt="A sunset over mountains",
        model="grok-imagine-image",
        batch_request_id="test_image_1",
    )

    assert isinstance(batch_req, batch_pb2.BatchRequest)
    assert batch_req.batch_request_id == "test_image_1"
    assert batch_req.HasField("image_request")
    assert batch_req.image_request.prompt == "A sunset over mountains"
    assert batch_req.image_request.model == "grok-imagine-image"


def test_create_without_batch_request_id(client: Client):
    """Test that create() works without batch_request_id."""
    batch_req = client.image.prepare(
        prompt="A forest",
        model="grok-imagine-image",
    )

    assert isinstance(batch_req, batch_pb2.BatchRequest)
    assert batch_req.batch_request_id == ""
    assert batch_req.image_request.prompt == "A forest"


def test_create_with_aspect_ratio_and_resolution(client: Client):
    """Test that create() passes aspect_ratio and resolution."""
    batch_req = client.image.prepare(
        prompt="A beach",
        model="grok-imagine-image",
        batch_request_id="beach_1",
        aspect_ratio="16:9",
        resolution="2k",
    )

    assert batch_req.image_request.aspect_ratio == image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_16_9
    assert batch_req.image_request.resolution == image_pb2.ImageResolution.IMG_RESOLUTION_2K


def test_create_with_image_url(client: Client):
    """Test that create() passes image_url."""
    input_image_url = "https://example.com/input.jpg"
    batch_req = client.image.prepare(
        prompt="Edit this image",
        model="grok-imagine-image",
        image_url=input_image_url,
    )

    assert batch_req.image_request.HasField("image")
    assert batch_req.image_request.image.image_url == input_image_url


def test_create_rejects_both_image_fields(client: Client):
    """Test that create() rejects both image_url and image_urls."""
    with pytest.raises(ValueError, match="image_url/image_file_id or image_urls/image_file_ids"):
        client.image.prepare(
            prompt="foo",
            model="grok-imagine-image",
            image_url="https://example.com/image.jpg",
            image_urls=["https://example.com/image1.jpg"],
        )


def test_image_response_cost_usd_returns_dollars_when_set():
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png")],
        usage=usage_pb2.SamplingUsage(cost_in_usd_ticks=12345),
    )
    assert BaseImageResponse(proto, 0).cost_usd == 12345 * USD_PER_TICK


def test_image_response_cost_usd_returns_none_when_unset():
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png")],
        usage=usage_pb2.SamplingUsage(),
    )
    assert BaseImageResponse(proto, 0).cost_usd is None


def test_sample_passes_image_file_id(client: Client):
    server.clear_last_image_request()

    client.image.sample(prompt="foo", model="grok-imagine-image", image_file_id="file_abc")

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("image")
    assert request.image.file_id == "file_abc"
    assert request.image.detail == image_pb2.ImageDetail.DETAIL_AUTO


def test_sample_passes_image_file_ids(client: Client):
    server.clear_last_image_request()

    input_file_ids = ["file_abc", "file_def"]
    client.image.sample(prompt="foo", model="grok-imagine-image", image_file_ids=input_file_ids)

    request = server.get_last_image_request()
    assert request is not None
    assert [image.file_id for image in request.images] == input_file_ids
    assert all(image.detail == image_pb2.ImageDetail.DETAIL_AUTO for image in request.images)


def test_sample_rejects_image_url_and_file_id(client: Client):
    with pytest.raises(ValueError, match="Only one of image_url or image_file_id can be set"):
        client.image.sample(
            prompt="foo",
            model="grok-imagine-image",
            image_url="https://example.com/image.jpg",
            image_file_id="file_abc",
        )


def test_sample_passes_mixed_image_urls_and_file_ids(client: Client):
    """`image_urls` and `image_file_ids` can be combined; file IDs are appended first."""
    server.clear_last_image_request()

    file_ids = ["file_abc", "file_def"]
    urls = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        image_urls=urls,
        image_file_ids=file_ids,
    )

    request = server.get_last_image_request()
    assert request is not None
    assert len(request.images) == 4
    # Documented order: file IDs first, then URLs.
    assert request.images[0].file_id == "file_abc"
    assert request.images[1].file_id == "file_def"
    assert request.images[2].image_url == "https://example.com/image1.jpg"
    assert request.images[3].image_url == "https://example.com/image2.jpg"
    assert all(image.detail == image_pb2.ImageDetail.DETAIL_AUTO for image in request.images)


def test_sample_batch_passes_image_file_ids(client: Client):
    server.clear_last_image_request()

    input_file_ids = ["file_abc", "file_def"]
    client.image.sample_batch(prompt="foo", model="grok-imagine-image", n=2, image_file_ids=input_file_ids)

    request = server.get_last_image_request()
    assert request is not None
    assert [image.file_id for image in request.images] == input_file_ids
    assert all(image.detail == image_pb2.ImageDetail.DETAIL_AUTO for image in request.images)


def test_prepare_passes_image_file_id(client: Client):
    batch_req = client.image.prepare(
        prompt="Edit this image",
        model="grok-imagine-image",
        image_file_id="file_abc",
    )

    assert batch_req.image_request.HasField("image")
    assert batch_req.image_request.image.file_id == "file_abc"


def test_sample_passes_storage_options(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "my-image.png", "expires_after": 3600},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "my-image.png"
    assert request.storage_options.expires_after == 3600


def test_sample_passes_storage_options_timedelta(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "test.png", "expires_after": datetime.timedelta(hours=1)},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.expires_after == 3600


def test_sample_passes_storage_options_proto(client: Client):
    server.clear_last_image_request()

    proto_opts = image_pb2.StorageOptions(filename="proto.png", expires_after=7200)
    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options=proto_opts,
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "proto.png"
    assert request.storage_options.expires_after == 7200


def test_sample_batch_passes_storage_options(client: Client):
    server.clear_last_image_request()

    client.image.sample_batch(
        prompt="foo",
        model="grok-imagine-image",
        n=2,
        storage_options={"filename": "my-image.png", "expires_after": 3600},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "my-image.png"
    assert request.storage_options.expires_after == 3600


def test_sample_passes_storage_options_with_filename_only(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "test.png"},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.png"


def test_sample_omits_storage_options_by_default(client: Client):
    server.clear_last_image_request()

    client.image.sample(prompt="foo", model="grok-imagine-image")

    request = server.get_last_image_request()
    assert request is not None
    assert not request.HasField("storage_options")


def test_image_response_file_output_properties():
    file_output = image_pb2.FileOutput(
        file_id="file-abc123",
        filename="my-image.png",
        expires_at=timestamp_pb2.Timestamp(seconds=1720000000),
    )
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png", file_output=file_output)],
    )
    response = BaseImageResponse(proto, 0)
    assert response.file_output is not None
    assert response.file_output.file_id == "file-abc123"
    assert response.file_output.filename == "my-image.png"
    assert response.file_output.expires_at == timestamp_pb2.Timestamp(seconds=1720000000)
    assert response.storage_error is None


def test_image_response_no_file_output():
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png")],
    )
    response = BaseImageResponse(proto, 0)
    assert response.file_output is None
    assert response.storage_error is None


def test_image_response_storage_error():
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png", storage_error="quota exceeded")],
    )
    response = BaseImageResponse(proto, 0)
    assert response.storage_error == "quota exceeded"


def test_sample_passes_storage_options_with_public_url(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "my-image.png", "public_url": {"expires_after": 86400}},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "my-image.png"
    assert request.storage_options.HasField("public_url")
    assert request.storage_options.public_url.expires_after == 86400


def test_sample_passes_storage_options_with_public_url_true(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "test.png", "public_url": True},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.png"
    assert request.storage_options.HasField("public_url")
    assert not request.storage_options.public_url.HasField("expires_after")


def test_sample_passes_storage_options_with_public_url_false(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "test.png", "public_url": False},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.png"
    assert not request.storage_options.HasField("public_url")


def test_sample_passes_storage_options_with_public_url_timedelta(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
        storage_options={"filename": "test.png", "public_url": {"expires_after": datetime.timedelta(hours=2)}},
    )

    request = server.get_last_image_request()
    assert request is not None
    assert request.storage_options.HasField("public_url")
    assert request.storage_options.public_url.expires_after == 7200


def test_image_response_public_url_properties():
    file_output = image_pb2.FileOutput(
        file_id="file-abc123",
        filename="my-image.png",
        public_url="https://files-cdn.x.ai/tok/file-abc123.png",
    )
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png", file_output=file_output)],
    )
    response = BaseImageResponse(proto, 0)
    assert response.public_url == "https://files-cdn.x.ai/tok/file-abc123.png"
    assert response.public_url_error is None


def test_image_response_public_url_error():
    file_output = image_pb2.FileOutput(
        file_id="file-abc123",
        filename="my-image.png",
        public_url_error="content type not allowed",
    )
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png", file_output=file_output)],
    )
    response = BaseImageResponse(proto, 0)
    assert response.public_url is None
    assert response.public_url_error == "content type not allowed"


def test_image_response_public_url_none_when_no_file_output():
    proto = image_pb2.ImageResponse(
        images=[image_pb2.GeneratedImage(url="https://example.com/i.png")],
    )
    response = BaseImageResponse(proto, 0)
    assert response.public_url is None
    assert response.public_url_error is None
