import asyncio
import datetime
from typing import Optional

from opentelemetry.trace import SpanKind

from ..poll_timer import PollTimer
from ..proto import deferred_pb2, video_pb2
from ..telemetry import get_tracer
from ..video import (
    BaseClient,
    VideoAspectRatio,
    VideoResolution,
    VideoResponse,
    _make_generate_request,
    _make_span_request_attributes,
    _make_span_response_attributes,
)

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Asynchronous client for interacting with the `Video` API."""

    async def start(
        self,
        prompt: str,
        model: str,
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
        model: str,
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
        timer = PollTimer(timeout, interval)
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
                    case unknown_status:
                        raise ValueError(f"Unknown deferred status: {unknown_status}")
