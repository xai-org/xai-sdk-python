from unittest import mock

import pytest
import pytest_asyncio
from opentelemetry.trace import SpanKind

from xai_sdk import AsyncClient
from xai_sdk.proto import image_pb2, video_pb2

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
