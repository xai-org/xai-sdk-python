import datetime
import sys
import time
from typing import Optional, Union

import requests
from opentelemetry.trace import SpanKind

from ..__about__ import __version__
from ..poll_timer import PollTimer
from ..proto import deferred_pb2, video_pb2
from ..telemetry import get_tracer
from ..video import (
    BaseClient,
    RestGetResponse,
    RestStartResponse,
    RestVideoResponse,
    VideoAspectRatio,
    VideoResolution,
    VideoResponse,
    VideoTransport,
    _make_generate_request,
    _make_rest_generate_request,
    _make_span_request_attributes,
    _make_span_response_attributes,
)

tracer = get_tracer(__name__)

# Type alias for responses that can be either gRPC or REST based
VideoResponseType = Union[VideoResponse, RestVideoResponse]
StartResponseType = Union[deferred_pb2.StartDeferredResponse, RestStartResponse]
GetResponseType = Union[video_pb2.GetDeferredVideoResponse, RestGetResponse]


class Client(BaseClient):
    """Synchronous client for interacting with the `Video` API.

    Supports both gRPC and REST transports. The transport is determined by the
    `transport` parameter passed during initialization.
    """

    def _get_rest_headers(self) -> dict[str, str]:
        """Returns headers for REST API requests."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"xai-sdk-python/{__version__}",
            "xai-sdk-version": f"python/{__version__}",
            "xai-sdk-language": f"python/{sys.version_info.major}.{sys.version_info.minor}",
        }

    def _rest_start(
        self,
        prompt: str,
        model: str,
        *,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
    ) -> RestStartResponse:
        """Starts a video generation request via REST API."""
        endpoint, body = _make_rest_generate_request(
            prompt,
            model,
            image_url=image_url,
            video_url=video_url,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        url = f"{self._get_rest_base_url()}/{endpoint}"
        response = requests.post(url, json=body, headers=self._get_rest_headers(), timeout=30)
        response.raise_for_status()
        return RestStartResponse(response.json())

    def _rest_get(self, request_id: str) -> RestGetResponse:
        """Gets video generation status via REST API."""
        url = f"{self._get_rest_base_url()}/videos/{request_id}"
        response = requests.get(url, headers=self._get_rest_headers(), timeout=30)
        response.raise_for_status()
        return RestGetResponse(response.json())

    def _rest_generate(
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
    ) -> RestVideoResponse:
        """Generates a video via REST API with automatic polling."""
        timer = PollTimer(timeout, interval)

        # Start the generation
        start_response = self._rest_start(
            prompt,
            model,
            image_url=image_url,
            video_url=video_url,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        # Poll until complete
        while True:
            get_response = self._rest_get(start_response.request_id)
            status = get_response.status.lower()

            if status == "done" or status == "completed":
                return get_response.to_video_response()
            elif status == "expired" or status == "failed":
                raise RuntimeError(f"Video generation {status}.")
            elif status == "pending" or status == "processing":
                time.sleep(timer.sleep_interval_or_raise())
                continue
            else:
                raise ValueError(f"Unknown status: {status}")

    def start(
        self,
        prompt: str,
        model: str,
        *,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
        transport: Optional[VideoTransport] = None,
    ) -> StartResponseType:
        """Starts a video generation request and returns a request_id for polling.

        Args:
            prompt: The text prompt describing the video to generate.
            model: The model to use for generation.
            image_url: Optional URL of an image for image-to-video generation.
            video_url: Optional URL of a video for video editing.
            duration: Optional duration in seconds (1-15).
            aspect_ratio: Optional aspect ratio for the output video.
            resolution: Optional resolution for the output video.
            transport: Override the default transport ("grpc" or "rest").

        Returns:
            A response containing the request_id for polling.
        """
        use_transport = transport or self._transport

        if use_transport == "rest":
            return self._rest_start(
                prompt,
                model,
                image_url=image_url,
                video_url=video_url,
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
            )

        # gRPC transport
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
            return self._stub.GenerateVideo(request)

    def get(
        self,
        request_id: str,
        *,
        transport: Optional[VideoTransport] = None,
    ) -> GetResponseType:
        """Gets the current status (and optional result) for a deferred video request.

        Args:
            request_id: The request ID from a previous start() call.
            transport: Override the default transport ("grpc" or "rest").

        Returns:
            A response containing the current status and result if complete.
        """
        use_transport = transport or self._transport

        if use_transport == "rest":
            return self._rest_get(request_id)

        # gRPC transport
        request = video_pb2.GetDeferredVideoRequest(request_id=request_id)
        return self._stub.GetDeferredVideo(request)

    def generate(
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
        transport: Optional[VideoTransport] = None,
    ) -> VideoResponseType:
        """Generates a video using polling and returns the completed response.

        This wraps start() + repeated get() calls until the request is complete.

        Args:
            prompt: The text prompt describing the video to generate.
            model: The model to use for generation.
            image_url: Optional URL of an image for image-to-video generation.
            video_url: Optional URL of a video for video editing.
            duration: Optional duration in seconds (1-15).
            aspect_ratio: Optional aspect ratio for the output video.
            resolution: Optional resolution for the output video.
            timeout: Optional timeout for the entire operation.
            interval: Optional polling interval.
            transport: Override the default transport ("grpc" or "rest").

        Returns:
            A VideoResponse (gRPC) or RestVideoResponse (REST) containing the result.
        """
        use_transport = transport or self._transport

        if use_transport == "rest":
            return self._rest_generate(
                prompt,
                model,
                image_url=image_url,
                video_url=video_url,
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                timeout=timeout,
                interval=interval,
            )

        # gRPC transport
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
            start = self._stub.GenerateVideo(request_pb)

            while True:
                get_req = video_pb2.GetDeferredVideoRequest(request_id=start.request_id)

                r = self._stub.GetDeferredVideo(get_req)
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
                        time.sleep(timer.sleep_interval_or_raise())
                        continue
                    case unknown_status:
                        raise ValueError(f"Unknown deferred status: {unknown_status}")
