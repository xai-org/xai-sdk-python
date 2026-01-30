from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client
from xai_sdk.image import ImageFormat
from xai_sdk.proto import image_pb2

from .. import server


@pytest.fixture(scope="session")
def client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


@pytest.fixture
def image_asset():
    return server.read_image()


def test_base64(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-imagine-image", image_format="base64")

    assert response.prompt == "foo"
    assert image_asset == response.image


def test_url(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-imagine-image", image_format="url")

    assert response.prompt == "foo"
    assert image_asset == response.image


def test_batch(client: Client, image_asset: bytes):
    responses = client.image.sample_batch(prompt="foo", model="grok-imagine-image", n=2, image_format="base64")

    assert len(responses) == 2

    for r in responses:
        assert r.prompt == "foo"
        assert image_asset == r.image


def test_sample_passes_aspect_ratio_and_resolution(client: Client):
    server.clear_last_image_request()

    client.image.sample(
        prompt="foo",
        model="grok-imagine-image",
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
        model="grok-imagine-image",
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
        "gen_ai.response.0.image.up_sampled_prompt": response.prompt,
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
        client.image.sample(prompt="A beautiful sunset", model="grok-imagine-image", image_format=image_format, user=user)

    expected_request_attributes = {
        "gen_ai.operation.name": "generate_image",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "image",
        "gen_ai.request.model": "grok-imagine-image",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample grok-imagine-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-image",
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
        "gen_ai.response.0.image.up_sampled_prompt": responses[0].prompt,
        "gen_ai.response.1.image.up_sampled_prompt": responses[1].prompt,
        "gen_ai.response.2.image.up_sampled_prompt": responses[2].prompt,
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
