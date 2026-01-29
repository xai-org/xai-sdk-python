from typing import Any, Optional, Union

import grpc

from .meta import ProtoDecorator
from .proto import image_pb2, usage_pb2, video_pb2, video_pb2_grpc
from .telemetry import should_disable_sensitive_attributes
from .types.video import VideoAspectRatio, VideoAspectRatioMap, VideoResolution, VideoResolutionMap


class BaseClient:
    """Base Client for interacting with the `Video` API."""

    _stub: video_pb2_grpc.VideoStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = video_pb2_grpc.VideoStub(channel)


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
