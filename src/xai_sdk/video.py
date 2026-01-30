from typing import Any, Literal, Optional, Union

import grpc

from .meta import ProtoDecorator
from .proto import image_pb2, usage_pb2, video_pb2, video_pb2_grpc
from .telemetry import should_disable_sensitive_attributes
from .types.video import VideoAspectRatio, VideoAspectRatioMap, VideoResolution, VideoResolutionMap

# Transport type for video client
VideoTransport = Literal["grpc", "rest"]

# REST API base URL
REST_API_BASE = "https://api.x.ai/v1"


class BaseClient:
    """Base Client for interacting with the `Video` API."""

    _stub: video_pb2_grpc.VideoStub
    _transport: VideoTransport
    _api_key: Optional[str]
    _api_host: Optional[str]

    def __init__(
        self,
        channel: Union[grpc.Channel, grpc.aio.Channel],
        *,
        transport: VideoTransport = "grpc",
        api_key: Optional[str] = None,
        api_host: Optional[str] = None,
    ):
        """Creates a new client based on a gRPC channel or REST configuration.

        Args:
            channel: The gRPC channel to use for gRPC transport.
            transport: The transport to use ("grpc" or "rest"). Defaults to "grpc".
            api_key: The API key for REST transport. Required if transport is "rest".
            api_host: The API host for REST transport. Defaults to "api.x.ai".
        """
        self._stub = video_pb2_grpc.VideoStub(channel)
        self._transport = transport
        self._api_key = api_key
        self._api_host = api_host or "api.x.ai"

    def _get_rest_base_url(self) -> str:
        """Returns the REST API base URL."""
        if self._api_host and self._api_host != "api.x.ai":
            # Handle localhost or custom hosts
            if self._api_host.startswith("localhost:"):
                return f"http://{self._api_host}/v1"
            return f"https://{self._api_host}/v1"
        return REST_API_BASE


class VideoResponse(ProtoDecorator[video_pb2.VideoResponse]):
    """Adds auxiliary functions for handling the video response proto."""

    _video: video_pb2.GeneratedVideo

    def __init__(self, proto: video_pb2.VideoResponse) -> None:
        """Initializes a new instance of the `VideoResponse` wrapper class."""
        super().__init__(proto)
        self._video = proto.video

    @property
    def model(self) -> str:
        """The model used to generate the video (ignoring aliases)."""
        return self._proto.model

    @property
    def usage(self) -> usage_pb2.SamplingUsage:
        """Token and tool usage for this request."""
        return self._proto.usage

    @property
    def respect_moderation(self) -> bool:
        """Whether the generated video respects moderation rules."""
        return getattr(self._video, "respect_moderation", True)

    @property
    def url(self) -> str:
        """The URL under which the video is stored or raises an error.

        Note: The returned URL is valid for 24 hours.
        """
        url = self._video.url
        if not url:
            if not self.respect_moderation:
                raise ValueError("Video did not respect moderation rules; URL is not available.")
            raise ValueError("Video URL missing from response.")
        return url

    @property
    def duration(self) -> int:
        """Duration of the generated video in seconds."""
        return self._video.duration


class RestVideoResponse:
    """Video response for REST API responses."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initializes a new instance from REST API JSON response.

        Args:
            data: The JSON response data from the REST API.
        """
        self._data = data
        self._video = data.get("video", data)  # Handle both nested and flat structures

    @property
    def model(self) -> str:
        """The model used to generate the video."""
        return self._data.get("model", "")

    @property
    def usage(self) -> dict[str, int]:
        """Token and tool usage for this request."""
        return self._data.get("usage", {})

    @property
    def respect_moderation(self) -> bool:
        """Whether the generated video respects moderation rules."""
        return self._video.get("respect_moderation", True)

    @property
    def url(self) -> str:
        """The URL under which the video is stored or raises an error.

        Note: The returned URL is valid for 24 hours.
        """
        url = self._video.get("url", self._data.get("url", ""))
        if not url:
            if not self.respect_moderation:
                raise ValueError("Video did not respect moderation rules; URL is not available.")
            raise ValueError("Video URL missing from response.")
        return url

    @property
    def duration(self) -> int:
        """Duration of the generated video in seconds."""
        return self._video.get("duration", self._data.get("duration", 0))

    @property
    def request_id(self) -> str:
        """The request ID for deferred requests."""
        return self._data.get("request_id", "")

    @property
    def status(self) -> str:
        """The status of a deferred request (pending, done, expired)."""
        return self._data.get("status", "")


class RestStartResponse:
    """Response for REST API start/deferred requests."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initializes from REST API JSON response."""
        self._data = data

    @property
    def request_id(self) -> str:
        """The request ID for polling."""
        return self._data.get("request_id", "")


class RestGetResponse:
    """Response for REST API get/poll requests."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initializes from REST API JSON response."""
        self._data = data

    @property
    def status(self) -> str:
        """The status of the deferred request."""
        return self._data.get("status", "pending")

    @property
    def url(self) -> str:
        """The video URL (when status is done)."""
        return self._data.get("url", "")

    @property
    def model(self) -> str:
        """The model used."""
        return self._data.get("model", "")

    @property
    def duration(self) -> int:
        """Video duration in seconds."""
        return self._data.get("duration", 0)

    @property
    def respect_moderation(self) -> bool:
        """Whether the video respects moderation rules."""
        return self._data.get("respect_moderation", True)

    @property
    def usage(self) -> dict[str, int]:
        """Token usage information."""
        return self._data.get("usage", {})

    def to_video_response(self) -> RestVideoResponse:
        """Converts to a RestVideoResponse when the request is complete."""
        return RestVideoResponse(self._data)


def _make_rest_generate_request(
    prompt: str,
    model: str,
    *,
    image_url: Optional[str],
    video_url: Optional[str],
    duration: Optional[int],
    aspect_ratio: Optional[VideoAspectRatio],
    resolution: Optional[VideoResolution],
) -> tuple[str, dict[str, Any]]:
    """Builds a REST API request for video generation.

    Returns:
        A tuple of (endpoint, request_body).
        endpoint is either "videos/generations" or "videos/edits".
    """
    body: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
    }

    if image_url is not None:
        body["image"] = {"url": image_url}

    if video_url is not None:
        body["video"] = {"url": video_url}

    if duration is not None:
        body["duration"] = duration

    if aspect_ratio is not None:
        body["aspect_ratio"] = aspect_ratio

    if resolution is not None:
        body["resolution"] = resolution

    # Determine endpoint based on whether we're editing a video
    endpoint = "videos/edits" if video_url is not None else "videos/generations"

    return endpoint, body


def _make_generate_request(
    prompt: str,
    model: str,
    *,
    image_url: Optional[str],
    video_url: Optional[str],
    duration: Optional[int],
    aspect_ratio: Optional[VideoAspectRatio],
    resolution: Optional[VideoResolution],
) -> video_pb2.GenerateVideoRequest:
    request = video_pb2.GenerateVideoRequest(prompt=prompt, model=model)

    if image_url is not None:
        request.image.CopyFrom(
            image_pb2.ImageUrlContent(
                image_url=image_url,
                detail=image_pb2.ImageDetail.DETAIL_AUTO,
            )
        )
    if video_url is not None:
        request.video.CopyFrom(video_pb2.VideoUrlContent(url=video_url))
    if duration is not None:
        request.duration = duration
    if aspect_ratio is not None:
        request.aspect_ratio = convert_video_aspect_ratio_to_pb(aspect_ratio)
    if resolution is not None:
        request.resolution = convert_video_resolution_to_pb(resolution)

    return request


def _make_span_request_attributes(request: video_pb2.GenerateVideoRequest) -> dict[str, Any]:
    """Creates the video generation span request attributes."""
    attributes: dict[str, Any] = {
        "gen_ai.operation.name": "generate_video",
        "gen_ai.request.model": request.model,
        "gen_ai.provider.name": "xai",
        "server.address": "api.x.ai",
        "gen_ai.output.type": "video",
    }

    if should_disable_sensitive_attributes():
        return attributes

    attributes["gen_ai.prompt"] = request.prompt

    if request.HasField("duration"):
        attributes["gen_ai.request.video.duration"] = request.duration
    if request.HasField("aspect_ratio"):
        attributes["gen_ai.request.video.aspect_ratio"] = (
            video_pb2.VideoAspectRatio.Name(request.aspect_ratio).removeprefix("VIDEO_ASPECT_RATIO_").replace("_", ":")
        )
    if request.HasField("resolution"):
        attributes["gen_ai.request.video.resolution"] = (
            video_pb2.VideoResolution.Name(request.resolution).removeprefix("VIDEO_RESOLUTION_").lower()
        )

    return attributes


def _make_span_response_attributes(request: video_pb2.GenerateVideoRequest, response: VideoResponse) -> dict[str, Any]:
    """Creates the video generation span response attributes."""
    attributes: dict[str, Any] = {
        "gen_ai.response.model": request.model,
    }

    if should_disable_sensitive_attributes():
        return attributes

    usage = response.usage
    attributes["gen_ai.usage.input_tokens"] = usage.prompt_tokens
    attributes["gen_ai.usage.output_tokens"] = usage.completion_tokens
    attributes["gen_ai.usage.total_tokens"] = usage.total_tokens
    attributes["gen_ai.usage.reasoning_tokens"] = usage.reasoning_tokens
    attributes["gen_ai.usage.cached_prompt_text_tokens"] = usage.cached_prompt_text_tokens
    attributes["gen_ai.usage.prompt_text_tokens"] = usage.prompt_text_tokens
    attributes["gen_ai.usage.prompt_image_tokens"] = usage.prompt_image_tokens

    attributes["gen_ai.response.0.video.respect_moderation"] = response.respect_moderation
    if response._video.url:
        attributes["gen_ai.response.0.video.url"] = response._video.url
    attributes["gen_ai.response.0.video.duration"] = response.duration

    return attributes


def convert_video_aspect_ratio_to_pb(aspect_ratio: VideoAspectRatio) -> video_pb2.VideoAspectRatio:
    """Converts a string literal representation of a video aspect ratio to its protobuf enum variant."""
    try:
        return VideoAspectRatioMap[aspect_ratio]
    except KeyError as exc:
        raise ValueError(f"Invalid video aspect ratio {aspect_ratio}.") from exc


def convert_video_resolution_to_pb(resolution: VideoResolution) -> video_pb2.VideoResolution:
    """Converts a string literal representation of a video resolution to its protobuf enum variant."""
    try:
        return VideoResolutionMap[resolution]
    except KeyError as exc:
        raise ValueError(f"Invalid video resolution {resolution}.") from exc
