import warnings
from unittest import mock

import pytest
import pytest_asyncio
from google.protobuf import timestamp_pb2
from opentelemetry.trace import SpanKind

from xai_sdk import AsyncClient
from xai_sdk.cost import USD_PER_TICK
from xai_sdk.proto import batch_pb2, deferred_pb2, image_pb2, usage_pb2, video_pb2
from xai_sdk.video import VideoGenerationError, VideoResponse

from .. import server


@pytest_asyncio.fixture(scope="session")
async def client():
    with server.run_test_server() as port:
        yield AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_returns_video_url_and_optional_prompt(client: AsyncClient):
    response = await client.video.generate(prompt="foo", model="grok-imagine-video")

    assert response.model == "grok-imagine-video"
    assert response.url
    assert response.duration > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_duration_aspect_ratio_and_resolution(client: AsyncClient):
    server.clear_last_video_request()

    response = await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        duration=3,
        aspect_ratio="16:9",
        resolution="480p",
    )

    assert response.duration == 3

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("duration")
    assert request.duration == 3
    assert request.HasField("aspect_ratio")
    assert request.aspect_ratio == video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_16_9
    assert request.HasField("resolution")
    assert request.resolution == video_pb2.VideoResolution.VIDEO_RESOLUTION_480P


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_image_url(client: AsyncClient):
    server.clear_last_video_request()

    input_image_url = "https://example.com/image.jpg"
    await client.video.generate(prompt="foo", model="grok-imagine-video", image_url=input_image_url)

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("image")
    assert request.image.image_url == input_image_url
    assert request.image.detail == image_pb2.ImageDetail.DETAIL_AUTO


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_video_url(client: AsyncClient):
    server.clear_last_video_request()

    input_video_url = "https://example.com/video.mp4"
    await client.video.generate(prompt="foo", model="grok-imagine-video", video_url=input_video_url)

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("video")
    assert request.video.url == input_video_url


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_reference_image_urls(client: AsyncClient):
    server.clear_last_video_request()

    ref_urls = ["https://example.com/ref1.jpg", "https://example.com/ref2.jpg"]
    await client.video.generate(prompt="foo", model="grok-imagine-video", reference_image_urls=ref_urls)

    request = server.get_last_video_request()
    assert request is not None
    assert len(request.reference_images) == 2
    assert request.reference_images[0].image_url == ref_urls[0]
    assert request.reference_images[0].detail == image_pb2.ImageDetail.DETAIL_AUTO
    assert request.reference_images[1].image_url == ref_urls[1]


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_with_reference_image_urls(client: AsyncClient):
    """Test that prepare() passes reference_image_urls."""
    ref_urls = ["https://example.com/ref1.jpg", "https://example.com/ref2.jpg"]
    batch_req = client.video.prepare(
        prompt="Generate from references",
        model="grok-imagine-video",
        reference_image_urls=ref_urls,
    )

    assert len(batch_req.video_request.reference_images) == 2
    assert batch_req.video_request.reference_images[0].image_url == ref_urls[0]
    assert batch_req.video_request.reference_images[1].image_url == ref_urls[1]


@mock.patch("xai_sdk.aio.video.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_generate_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    response = await client.video.generate(prompt="A beautiful sunset", model="grok-imagine-video")

    expected_request_attributes = {
        "gen_ai.prompt": "A beautiful sunset",
        "gen_ai.operation.name": "generate_video",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "video",
        "server.address": "api.x.ai",
        "gen_ai.request.model": "grok-imagine-video",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="video.generate grok-imagine-video",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-video",
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.0.video.respect_moderation": response.respect_moderation,
        "gen_ai.response.0.video.url": response.url,
        "gen_ai.response.0.video.duration": response.duration,
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.video.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_generate_creates_span_without_sensitive_attributes_when_disabled(
    mock_tracer: mock.MagicMock, client: AsyncClient
):
    """Test that sensitive attributes are not included when XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES is set."""
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    with mock.patch.dict("os.environ", {"XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES": "1"}):
        await client.video.generate(prompt="A beautiful sunset", model="grok-imagine-video")

    expected_request_attributes = {
        "gen_ai.operation.name": "generate_video",
        "gen_ai.provider.name": "xai",
        "server.address": "api.x.ai",
        "gen_ai.request.model": "grok-imagine-video",
        "gen_ai.output.type": "video",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="video.generate grok-imagine-video",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-video",
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_raises_video_generation_error_on_failure(client: AsyncClient):
    """Test that generate raises VideoGenerationError when the deferred request fails."""
    failed_response = video_pb2.GetDeferredVideoResponse(
        status=deferred_pb2.DeferredStatus.FAILED,
        response=video_pb2.VideoResponse(
            error=video_pb2.VideoError(
                code="CONTENT_POLICY_VIOLATION",
                message="The prompt violates content policy guidelines.",
            )
        ),
    )

    async def mock_get_deferred_video(_request):
        return failed_response

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with pytest.raises(VideoGenerationError) as exc_info:
            await client.video.generate(prompt="foo", model="grok-imagine-video")

        assert exc_info.value.code == "CONTENT_POLICY_VIOLATION"
        assert exc_info.value.message == "The prompt violates content policy guidelines."
        assert "CONTENT_POLICY_VIOLATION" in str(exc_info.value)
        assert "The prompt violates content policy guidelines." in str(exc_info.value)


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_raises_video_generation_error_without_details(client: AsyncClient):
    """Test that generate raises VideoGenerationError with UNKNOWN code when no error details are provided."""
    failed_response = video_pb2.GetDeferredVideoResponse(
        status=deferred_pb2.DeferredStatus.FAILED,
    )

    async def mock_get_deferred_video(_request):
        return failed_response

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with pytest.raises(VideoGenerationError) as exc_info:
            await client.video.generate(prompt="foo", model="grok-imagine-video")

        assert exc_info.value.code == "UNKNOWN"
        assert "Video generation failed with no error details." in exc_info.value.message


# Tests for video.prepare() batch request method


@pytest.mark.asyncio(loop_scope="session")
async def test_create_returns_batch_request(client: AsyncClient):
    """Test that create() returns a BatchRequest proto."""
    batch_req = client.video.prepare(
        prompt="A timelapse of clouds",
        model="grok-imagine-video",
        batch_request_id="test_video_1",
    )

    assert isinstance(batch_req, batch_pb2.BatchRequest)
    assert batch_req.batch_request_id == "test_video_1"
    assert batch_req.HasField("video_request")
    assert batch_req.video_request.prompt == "A timelapse of clouds"
    assert batch_req.video_request.model == "grok-imagine-video"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_with_duration_aspect_ratio_and_resolution(client: AsyncClient):
    """Test that create() passes duration, aspect_ratio and resolution."""
    batch_req = client.video.prepare(
        prompt="A sunset",
        model="grok-imagine-video",
        batch_request_id="sunset_1",
        duration=5,
        aspect_ratio="16:9",
        resolution="720p",
    )

    assert batch_req.video_request.duration == 5
    assert batch_req.video_request.aspect_ratio == video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_16_9
    assert batch_req.video_request.resolution == video_pb2.VideoResolution.VIDEO_RESOLUTION_720P


@pytest.mark.asyncio(loop_scope="session")
async def test_create_with_image_url(client: AsyncClient):
    """Test that create() passes image_url."""
    input_image_url = "https://example.com/start_frame.jpg"
    batch_req = client.video.prepare(
        prompt="Animate this image",
        model="grok-imagine-video",
        image_url=input_image_url,
    )

    assert batch_req.video_request.HasField("image")
    assert batch_req.video_request.image.image_url == input_image_url


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_returns_batch_request(client: AsyncClient):
    """Test that prepare_extension() returns a BatchRequest with video_extension_request."""
    batch_req = client.video.prepare_extension(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
        batch_request_id="ext_1",
    )

    assert isinstance(batch_req, batch_pb2.BatchRequest)
    assert batch_req.batch_request_id == "ext_1"
    assert batch_req.HasField("video_extension_request")
    assert batch_req.video_extension_request.prompt == "Continue the scene"
    assert batch_req.video_extension_request.model == "grok-imagine-video"
    assert batch_req.video_extension_request.video.url == "https://example.com/input.mp4"


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_without_batch_request_id(client: AsyncClient):
    """Test that prepare_extension() works without batch_request_id."""
    batch_req = client.video.prepare_extension(
        prompt="Extend this",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
    )

    assert batch_req.batch_request_id == ""
    assert batch_req.HasField("video_extension_request")


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_with_duration(client: AsyncClient):
    """Test that prepare_extension() passes duration."""
    batch_req = client.video.prepare_extension(
        prompt="More action",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
        duration=8,
    )

    assert batch_req.video_extension_request.duration == 8


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_warns_on_unknown_status_then_resolves(client: AsyncClient):
    """Test that generate emits a warning on unknown deferred status and continues polling."""
    # First poll returns an unknown status (999), second poll returns DONE.
    responses = [
        video_pb2.GetDeferredVideoResponse(status=999),  # type: ignore[arg-type]
        video_pb2.GetDeferredVideoResponse(
            status=deferred_pb2.DeferredStatus.DONE,
            response=video_pb2.VideoResponse(
                model="grok-imagine-video",
                video=video_pb2.GeneratedVideo(url="https://example.com/video.mp4", duration=5),
            ),
        ),
    ]

    async def mock_get_deferred_video(_request):
        return responses.pop(0)

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            response = await client.video.generate(prompt="foo", model="grok-imagine-video")

    assert response.url == "https://example.com/video.mp4"
    assert len(w) == 1
    assert "Encountered unknown status: 999 whilst waiting for video generation." in str(w[0].message)


# Tests for video.extend()


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_returns_video_url(client: AsyncClient):
    """Test that extend() returns a video response with a URL."""
    response = await client.video.extend(
        prompt="The camera zooms out",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
    )

    assert response.model == "grok-imagine-video"
    assert response.url
    assert response.duration > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_passes_video_url_and_duration(client: AsyncClient):
    """Test that extend() correctly passes video_url and duration to the request."""
    server.clear_last_extend_video_request()

    response = await client.video.extend(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_url="https://example.com/source.mp4",
        duration=8,
    )

    assert response.duration == 8

    request = server.get_last_extend_video_request()
    assert request is not None
    assert request.prompt == "Continue the scene"
    assert request.model == "grok-imagine-video"
    assert request.HasField("video")
    assert request.video.url == "https://example.com/source.mp4"
    assert request.HasField("duration")
    assert request.duration == 8


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_without_duration(client: AsyncClient):
    """Test that extend() works without specifying duration."""
    server.clear_last_extend_video_request()

    await client.video.extend(
        prompt="A bird flies across the sky",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
    )

    request = server.get_last_extend_video_request()
    assert request is not None
    assert not request.HasField("duration")


@mock.patch("xai_sdk.aio.video.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_extend_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    response = await client.video.extend(
        prompt="The scene continues",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
    )

    expected_request_attributes = {
        "gen_ai.prompt": "The scene continues",
        "gen_ai.operation.name": "extend_video",
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "video",
        "server.address": "api.x.ai",
        "gen_ai.request.model": "grok-imagine-video",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="video.extend grok-imagine-video",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-video",
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.0.video.respect_moderation": response.respect_moderation,
        "gen_ai.response.0.video.url": response.url,
        "gen_ai.response.0.video.duration": response.duration,
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.video.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_extend_creates_span_without_sensitive_attributes_when_disabled(
    mock_tracer: mock.MagicMock, client: AsyncClient
):
    """Test that sensitive attributes are not included when XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES is set."""
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    with mock.patch.dict("os.environ", {"XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES": "1"}):
        await client.video.extend(
            prompt="The scene continues",
            model="grok-imagine-video",
            video_url="https://example.com/input.mp4",
        )

    expected_request_attributes = {
        "gen_ai.operation.name": "extend_video",
        "gen_ai.provider.name": "xai",
        "server.address": "api.x.ai",
        "gen_ai.request.model": "grok-imagine-video",
        "gen_ai.output.type": "video",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="video.extend grok-imagine-video",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-imagine-video",
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_raises_video_generation_error_on_failure(client: AsyncClient):
    """Test that extend raises VideoGenerationError when the deferred request fails."""
    failed_response = video_pb2.GetDeferredVideoResponse(
        status=deferred_pb2.DeferredStatus.FAILED,
        response=video_pb2.VideoResponse(
            error=video_pb2.VideoError(
                code="CONTENT_POLICY_VIOLATION",
                message="The prompt violates content policy guidelines.",
            )
        ),
    )

    async def mock_get_deferred_video(_request):
        return failed_response

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with pytest.raises(VideoGenerationError) as exc_info:
            await client.video.extend(
                prompt="foo",
                model="grok-imagine-video",
                video_url="https://example.com/input.mp4",
            )

        assert exc_info.value.code == "CONTENT_POLICY_VIOLATION"
        assert exc_info.value.message == "The prompt violates content policy guidelines."


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_raises_video_generation_error_without_details(client: AsyncClient):
    """Test that extend raises VideoGenerationError with UNKNOWN code when no error details are provided."""
    failed_response = video_pb2.GetDeferredVideoResponse(
        status=deferred_pb2.DeferredStatus.FAILED,
    )

    async def mock_get_deferred_video(_request):
        return failed_response

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with pytest.raises(VideoGenerationError) as exc_info:
            await client.video.extend(
                prompt="foo",
                model="grok-imagine-video",
                video_url="https://example.com/input.mp4",
            )

        assert exc_info.value.code == "UNKNOWN"
        assert "Video extension failed with no error details." in exc_info.value.message


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_warns_on_unknown_status_then_resolves(client: AsyncClient):
    """Test that extend emits a warning on unknown deferred status and continues polling."""
    responses = [
        video_pb2.GetDeferredVideoResponse(status=999),  # type: ignore[arg-type]
        video_pb2.GetDeferredVideoResponse(
            status=deferred_pb2.DeferredStatus.DONE,
            response=video_pb2.VideoResponse(
                model="grok-imagine-video",
                video=video_pb2.GeneratedVideo(url="https://example.com/extended.mp4", duration=6),
            ),
        ),
    ]

    async def mock_get_deferred_video(_request):
        return responses.pop(0)

    with mock.patch.object(client.video._stub, "GetDeferredVideo", side_effect=mock_get_deferred_video):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            response = await client.video.extend(
                prompt="foo",
                model="grok-imagine-video",
                video_url="https://example.com/input.mp4",
            )

    assert response.url == "https://example.com/extended.mp4"
    assert len(w) == 1
    assert "Encountered unknown status: 999 whilst waiting for video extension." in str(w[0].message)


def test_video_response_cost_usd_returns_dollars_when_set():
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5),
        usage=usage_pb2.SamplingUsage(cost_in_usd_ticks=12345),
    )
    assert VideoResponse(proto).cost_usd == 12345 * USD_PER_TICK


def test_video_response_cost_usd_returns_none_when_unset():
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5),
        usage=usage_pb2.SamplingUsage(),
    )
    assert VideoResponse(proto).cost_usd is None


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_image_file_id(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(prompt="foo", model="grok-imagine-video", image_file_id="file_abc")

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("image")
    assert request.image.file_id == "file_abc"
    assert request.image.detail == image_pb2.ImageDetail.DETAIL_AUTO


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_video_file_id(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(prompt="foo", model="grok-imagine-video", video_file_id="file_abc")

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("video")
    assert request.video.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_reference_image_file_ids(client: AsyncClient):
    server.clear_last_video_request()

    ref_ids = ["file_abc", "file_def"]
    await client.video.generate(prompt="foo", model="grok-imagine-video", reference_image_file_ids=ref_ids)

    request = server.get_last_video_request()
    assert request is not None
    assert len(request.reference_images) == 2
    assert request.reference_images[0].file_id == ref_ids[0]
    assert request.reference_images[0].detail == image_pb2.ImageDetail.DETAIL_AUTO
    assert request.reference_images[1].file_id == ref_ids[1]


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_rejects_image_url_and_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="Only one of image_url or image_file_id can be set"):
        await client.video.generate(
            prompt="foo",
            model="grok-imagine-video",
            image_url="https://example.com/image.jpg",
            image_file_id="file_abc",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_rejects_video_url_and_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="Only one of video_url or video_file_id can be set"):
        await client.video.generate(
            prompt="foo",
            model="grok-imagine-video",
            video_url="https://example.com/video.mp4",
            video_file_id="file_abc",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_mixed_reference_image_urls_and_file_ids(client: AsyncClient):
    """`reference_image_urls` and `reference_image_file_ids` can be combined; file IDs first."""
    server.clear_last_video_request()

    file_ids = ["file_abc", "file_def"]
    urls = ["https://example.com/ref1.jpg", "https://example.com/ref2.jpg"]
    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        reference_image_urls=urls,
        reference_image_file_ids=file_ids,
    )

    request = server.get_last_video_request()
    assert request is not None
    assert len(request.reference_images) == 4
    assert request.reference_images[0].file_id == "file_abc"
    assert request.reference_images[1].file_id == "file_def"
    assert request.reference_images[2].image_url == "https://example.com/ref1.jpg"
    assert request.reference_images[3].image_url == "https://example.com/ref2.jpg"


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_passes_video_file_id(client: AsyncClient):
    server.clear_last_extend_video_request()

    await client.video.extend(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_file_id="file_abc",
    )

    request = server.get_last_extend_video_request()
    assert request is not None
    assert request.HasField("video")
    assert request.video.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_rejects_video_url_and_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="Only one of video_url or video_file_id can be set"):
        await client.video.extend(
            prompt="foo",
            model="grok-imagine-video",
            video_url="https://example.com/input.mp4",
            video_file_id="file_abc",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_rejects_neither_video_url_nor_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="One of video_url or video_file_id must be set"):
        await client.video.extend(
            prompt="foo",
            model="grok-imagine-video",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_start_passes_video_file_id(client: AsyncClient):
    server.clear_last_extend_video_request()

    await client.video.extend_start(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_file_id="file_abc",
    )

    request = server.get_last_extend_video_request()
    assert request is not None
    assert request.HasField("video")
    assert request.video.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_start_rejects_video_url_and_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="Only one of video_url or video_file_id can be set"):
        await client.video.extend_start(
            prompt="foo",
            model="grok-imagine-video",
            video_url="https://example.com/input.mp4",
            video_file_id="file_abc",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_start_rejects_neither_video_url_nor_file_id(client: AsyncClient):
    with pytest.raises(ValueError, match="One of video_url or video_file_id must be set"):
        await client.video.extend_start(
            prompt="foo",
            model="grok-imagine-video",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_passes_image_file_id(client: AsyncClient):
    batch_req = client.video.prepare(
        prompt="Animate this image",
        model="grok-imagine-video",
        image_file_id="file_abc",
    )

    assert batch_req.video_request.HasField("image")
    assert batch_req.video_request.image.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_passes_video_file_id(client: AsyncClient):
    batch_req = client.video.prepare(
        prompt="Edit this video",
        model="grok-imagine-video",
        video_file_id="file_abc",
    )

    assert batch_req.video_request.HasField("video")
    assert batch_req.video_request.video.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_passes_reference_image_file_ids(client: AsyncClient):
    ref_ids = ["file_abc", "file_def"]
    batch_req = client.video.prepare(
        prompt="Generate from references",
        model="grok-imagine-video",
        reference_image_file_ids=ref_ids,
    )

    assert len(batch_req.video_request.reference_images) == 2
    assert batch_req.video_request.reference_images[0].file_id == ref_ids[0]
    assert batch_req.video_request.reference_images[1].file_id == ref_ids[1]


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_storage_options(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        storage_options={"filename": "my-video.mp4", "expires_after": 7200},
    )

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "my-video.mp4"
    assert request.storage_options.expires_after == 7200


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_storage_options_with_filename_only(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        storage_options={"filename": "test.mp4"},
    )

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.mp4"


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_omits_storage_options_by_default(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(prompt="foo", model="grok-imagine-video")

    request = server.get_last_video_request()
    assert request is not None
    assert not request.HasField("storage_options")


@pytest.mark.asyncio(loop_scope="session")
async def test_extend_passes_storage_options(client: AsyncClient):
    server.clear_last_extend_video_request()

    await client.video.extend(
        prompt="Continue",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
        storage_options={"filename": "extended.mp4"},
    )

    request = server.get_last_extend_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "extended.mp4"


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_passes_storage_options(client: AsyncClient):
    batch_req = client.video.prepare(
        prompt="Generate video",
        model="grok-imagine-video",
        storage_options={"filename": "batch.mp4"},
    )

    assert batch_req.video_request.HasField("storage_options")
    assert batch_req.video_request.storage_options.filename == "batch.mp4"


def test_video_response_file_output_properties():
    file_output = image_pb2.FileOutput(
        file_id="file-xyz789",
        filename="my-video.mp4",
        expires_at=timestamp_pb2.Timestamp(seconds=1720000000),
    )
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5, file_output=file_output),
    )
    response = VideoResponse(proto)
    assert response.file_output is not None
    assert response.file_output.file_id == "file-xyz789"
    assert response.file_output.filename == "my-video.mp4"
    assert response.file_output.expires_at == timestamp_pb2.Timestamp(seconds=1720000000)
    assert response.storage_error is None


def test_video_response_no_file_output():
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5),
    )
    response = VideoResponse(proto)
    assert response.file_output is None
    assert response.storage_error is None


def test_video_response_storage_error():
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5, storage_error="quota exceeded"),
    )
    response = VideoResponse(proto)
    assert response.storage_error == "quota exceeded"


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_storage_options_with_public_url(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        storage_options={"filename": "my-video.mp4", "public_url": {"expires_after": 86400}},
    )

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "my-video.mp4"
    assert request.storage_options.HasField("public_url")
    assert request.storage_options.public_url.expires_after == 86400


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_storage_options_with_public_url_true(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        storage_options={"filename": "test.mp4", "public_url": True},
    )

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.mp4"
    assert request.storage_options.HasField("public_url")
    assert not request.storage_options.public_url.HasField("expires_after")


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_passes_storage_options_with_public_url_false(client: AsyncClient):
    server.clear_last_video_request()

    await client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        storage_options={"filename": "test.mp4", "public_url": False},
    )

    request = server.get_last_video_request()
    assert request is not None
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "test.mp4"
    assert not request.storage_options.HasField("public_url")


def test_video_response_public_url_properties():
    file_output = image_pb2.FileOutput(
        file_id="file-xyz789",
        filename="my-video.mp4",
        public_url="https://files-cdn.x.ai/tok/file-xyz789.mp4",
    )
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5, file_output=file_output),
    )
    response = VideoResponse(proto)
    assert response.public_url == "https://files-cdn.x.ai/tok/file-xyz789.mp4"
    assert response.public_url_error is None


def test_video_response_public_url_error():
    file_output = image_pb2.FileOutput(
        file_id="file-xyz789",
        filename="my-video.mp4",
        public_url_error="content type not allowed",
    )
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5, file_output=file_output),
    )
    response = VideoResponse(proto)
    assert response.public_url is None
    assert response.public_url_error == "content type not allowed"


def test_video_response_public_url_none_when_no_file_output():
    proto = video_pb2.VideoResponse(
        video=video_pb2.GeneratedVideo(url="https://example.com/v.mp4", duration=5),
    )
    response = VideoResponse(proto)
    assert response.public_url is None
    assert response.public_url_error is None


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_with_video_file_id(client: AsyncClient):
    """Test that prepare_extension() accepts a video_file_id."""
    batch_req = client.video.prepare_extension(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_file_id="file_abc",
    )

    assert batch_req.video_extension_request.video.file_id == "file_abc"


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_rejects_video_url_and_file_id(client: AsyncClient):
    """Test that prepare_extension() rejects setting both video_url and video_file_id."""
    with pytest.raises(ValueError, match="Only one of video_url or video_file_id can be set"):
        client.video.prepare_extension(
            prompt="foo",
            model="grok-imagine-video",
            video_url="https://example.com/input.mp4",
            video_file_id="file_abc",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_prepare_extension_passes_storage_options(client: AsyncClient):
    """Test that prepare_extension() passes storage_options through to the request."""
    batch_req = client.video.prepare_extension(
        prompt="Continue the scene",
        model="grok-imagine-video",
        video_url="https://example.com/input.mp4",
        storage_options={"filename": "output.mp4", "public_url": True},
    )

    request = batch_req.video_extension_request
    assert request.HasField("storage_options")
    assert request.storage_options.filename == "output.mp4"
    assert request.storage_options.HasField("public_url")
