import asyncio
import datetime
import warnings
from typing import Optional, Union

from opentelemetry.trace import SpanKind

from ..poll_timer import PollTimer
from ..proto import batch_pb2, deferred_pb2, video_pb2
from ..telemetry import get_tracer
from ..types import VideoGenerationModel
from ..video import (
    DEFAULT_VIDEO_POLL_INTERVAL,
    DEFAULT_VIDEO_TIMEOUT,
    BaseClient,
    VideoAspectRatio,
    VideoGenerationError,
    VideoResolution,
    VideoResponse,
    _make_generate_request,
    _make_span_request_attributes,
    _make_span_response_attributes,
)

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Asynchronous client for interacting with the `Video` API."""

    def prepare(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        *,
        batch_request_id: Optional[str] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
    ) -> batch_pb2.BatchRequest:
        """Prepares a video generation request for batch processing.

        Use this method to prepare video generation requests that can be added to a batch.
        This does not execute the generation - use `client.batch.add()` to submit requests.

        Args:
            prompt: The prompt to generate a video from.
            model: The model to use for video generation.
            batch_request_id: An optional user-provided identifier for the batch request.
                **If provided, it must be unique within the batch.** Used to identify the
                corresponding result when the response is returned.
            image_url: The URL of an input image to use as a starting frame.
            video_url: The URL of an input video to use as a starting point.
            duration: The duration of the video to generate in seconds.
            aspect_ratio: The aspect ratio of the video to generate.
            resolution: The video resolution to generate.

        Returns:
            A `BatchRequest` proto ready to be added to a batch.

        Examples:
            ```python
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Create a batch
            batch = await client.batch.create("my_video_batch")

            # Prepare batch requests for multiple videos
            requests = [
                client.video.prepare(
                    prompt="A timelapse of a sunset",
                    model="grok-imagine-video",
                    batch_request_id="sunset_video_1",
                ),
                client.video.prepare(
                    prompt="Waves crashing on a beach",
                    model="grok-imagine-video",
                    batch_request_id="beach_video_1",
                ),
            ]

            # Add requests to batch
            await client.batch.add(batch.batch_id, requests)
            ```
        """
        request = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            video_url=video_url,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        return batch_pb2.BatchRequest(
            video_request=request,
            batch_request_id=batch_request_id or "",
        )

    async def start(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        *,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
    ) -> deferred_pb2.StartDeferredResponse:
        """Starts a video generation request and returns a request_id for polling."""
        request = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            video_url=video_url,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        with tracer.start_as_current_span(
            name=f"video.start {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_span_request_attributes(request),
        ):
            return await self._stub.GenerateVideo(request)

    async def get(self, request_id: str) -> video_pb2.GetDeferredVideoResponse:
        """Gets the current status (and optional result) for a deferred video request."""
        request = video_pb2.GetDeferredVideoRequest(request_id=request_id)
        return await self._stub.GetDeferredVideo(request)

    async def generate(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        *,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
        timeout: Optional[datetime.timedelta] = None,
        interval: Optional[datetime.timedelta] = None,
    ) -> VideoResponse:
        """Generates a video using polling and returns the completed response.

        This wraps `GenerateVideo` + repeated `GetDeferredVideo` calls until the request is complete.
        """
        timer = PollTimer(
            timeout or DEFAULT_VIDEO_TIMEOUT,
            interval or DEFAULT_VIDEO_POLL_INTERVAL,
            context="waiting for video to be generated",
        )
        request_pb = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            video_url=video_url,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        with tracer.start_as_current_span(
            name=f"video.generate {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_span_request_attributes(request_pb),
        ) as span:
            start = await self._stub.GenerateVideo(request_pb)

            while True:
                get_req = video_pb2.GetDeferredVideoRequest(request_id=start.request_id)

                r = await self._stub.GetDeferredVideo(get_req)
                match r.status:
                    case deferred_pb2.DeferredStatus.DONE:
                        if not r.HasField("response"):
                            raise RuntimeError("Deferred request completed but no response was returned.")
                        response = VideoResponse(r.response)
                        span.set_attributes(_make_span_response_attributes(request_pb, response))
                        return response
                    case deferred_pb2.DeferredStatus.EXPIRED:
                        raise RuntimeError("Deferred request expired.")
                    case deferred_pb2.DeferredStatus.PENDING:
                        await asyncio.sleep(timer.sleep_interval_or_raise())
                        continue
                    case deferred_pb2.DeferredStatus.FAILED:
                        if r.HasField("response") and r.response.HasField("error"):
                            error = r.response.error
                            raise VideoGenerationError(error.code, error.message)
                        raise VideoGenerationError("UNKNOWN", "Video generation failed with no error details.")
                    case unknown_status:
                        warnings.warn(
                            f"Encountered unknown status: {unknown_status} whilst waiting for video generation.",
                            stacklevel=2,
                        )
                        await asyncio.sleep(timer.sleep_interval_or_raise())
