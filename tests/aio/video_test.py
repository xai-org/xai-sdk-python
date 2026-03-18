import warnings
from unittest import mock

import pytest
import pytest_asyncio
from opentelemetry.trace import SpanKind

from xai_sdk import AsyncClient
from xai_sdk.proto import batch_pb2, deferred_pb2, image_pb2, video_pb2
from xai_sdk.video import VideoGenerationError

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
