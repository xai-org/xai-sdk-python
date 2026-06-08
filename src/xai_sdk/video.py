import datetime
from typing import Any, Optional, Sequence, Union

import grpc

from .cost import cost_usd_from_usage
from .files import StorageOptions, _resolve_storage_options_pb
from .meta import ProtoDecorator
from .proto import image_pb2, usage_pb2, video_pb2, video_pb2_grpc
from .telemetry import should_disable_sensitive_attributes
from .types import VideoGenerationModel
from .types.video import VideoAspectRatio, VideoAspectRatioMap, VideoResolution, VideoResolutionMap

DEFAULT_VIDEO_POLL_INTERVAL = datetime.timedelta(seconds=1)
DEFAULT_VIDEO_TIMEOUT = datetime.timedelta(minutes=10)


class VideoGenerationError(Exception):
    """Raised when video generation fails."""

    def __init__(self, code: str, message: str) -> None:
        """Initializes a new instance of `VideoGenerationError`.

        Args:
            code: The error code from the video generation failure.
            message: The error message describing the failure.
        """
        super().__init__(f"Video generation failed [{code}]: {message}")
        self.code = code
        self.message = message


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
    def cost_usd(self) -> Optional[float]:
        """Cost of the request in USD, or None if the server did not report it."""
        return cost_usd_from_usage(self._proto.usage)

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

    @property
    def file_output(self) -> Optional[image_pb2.FileOutput]:
        """The full FileOutput proto if the asset was stored, or None otherwise."""
        if self._video.HasField("file_output"):
            return self._video.file_output
        return None

    @property
    def storage_error(self) -> Optional[str]:
        """Error message if storage was requested but failed, or None on success."""
        if self._video.storage_error:
            return self._video.storage_error
        return None

    @property
    def public_url(self) -> Optional[str]:
        """Public URL for the stored file, or None if not requested or creation failed."""
        file_output = self.file_output
        if file_output is not None and file_output.public_url:
            return file_output.public_url
        return None

    @property
    def public_url_error(self) -> Optional[str]:
        """Error message if public URL creation failed, or None on success."""
        file_output = self.file_output
        if file_output is not None and file_output.public_url_error:
            return file_output.public_url_error
        return None


def _validate_video_inputs(
    *,
    image_url: Optional[str] = None,
    image_file_id: Optional[str] = None,
    video_url: Optional[str] = None,
    video_file_id: Optional[str] = None,
) -> None:
    """Validates mutual exclusion constraints on video input parameters."""
    if image_url is not None and image_file_id is not None:
        raise ValueError("Only one of image_url or image_file_id can be set for a request.")
    if video_url is not None and video_file_id is not None:
        raise ValueError("Only one of video_url or video_file_id can be set for a request.")


def _make_generate_request(
    prompt: str,
    model: Union[VideoGenerationModel, str],
    *,
    image_url: Optional[str],
    image_file_id: Optional[str] = None,
    video_url: Optional[str],
    video_file_id: Optional[str] = None,
    duration: Optional[int],
    aspect_ratio: Optional[VideoAspectRatio],
    resolution: Optional[VideoResolution],
    reference_image_urls: Optional[Sequence[str]],
    reference_image_file_ids: Optional[Sequence[str]] = None,
    storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
) -> video_pb2.GenerateVideoRequest:
    _validate_video_inputs(
        image_url=image_url, image_file_id=image_file_id, video_url=video_url, video_file_id=video_file_id
    )

    request = video_pb2.GenerateVideoRequest(prompt=prompt, model=model)

    if image_url is not None:
        request.image.CopyFrom(image_pb2.ImageUrlContent(image_url=image_url, detail=image_pb2.ImageDetail.DETAIL_AUTO))
    elif image_file_id is not None:
        request.image.CopyFrom(
            image_pb2.ImageUrlContent(file_id=image_file_id, detail=image_pb2.ImageDetail.DETAIL_AUTO)
        )
    if video_url is not None:
        request.video.CopyFrom(video_pb2.VideoUrlContent(url=video_url))
    elif video_file_id is not None:
        request.video.CopyFrom(video_pb2.VideoUrlContent(file_id=video_file_id))
    if duration is not None:
        request.duration = duration
    if aspect_ratio is not None:
        request.aspect_ratio = convert_video_aspect_ratio_to_pb(aspect_ratio)
    if resolution is not None:
        request.resolution = convert_video_resolution_to_pb(resolution)
    _set_reference_images(request, reference_image_urls, reference_image_file_ids)
    if storage_options is not None:
        request.storage_options.CopyFrom(_resolve_storage_options_pb(storage_options))

    return request


def _set_reference_images(
    request: video_pb2.GenerateVideoRequest,
    urls: Optional[Sequence[str]],
    file_ids: Optional[Sequence[str]],
) -> None:
    """Populates `reference_images` from URL and/or file-ID lists.

    Both lists may be supplied to mix URL/base64 and file-ID references in
    the same request. File IDs are appended first so callers can predict the
    resulting positional ordering used by the model.
    """
    if file_ids is not None:
        request.reference_images.extend(
            [
                image_pb2.ImageUrlContent(
                    file_id=fid,
                    detail=image_pb2.ImageDetail.DETAIL_AUTO,
                )
                for fid in file_ids
            ]
        )
    if urls is not None:
        request.reference_images.extend(
            [
                image_pb2.ImageUrlContent(
                    image_url=url,
                    detail=image_pb2.ImageDetail.DETAIL_AUTO,
                )
                for url in urls
            ]
        )


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

    if request.HasField("storage_options"):
        attributes["gen_ai.request.storage"] = True
        if request.storage_options.filename:
            attributes["gen_ai.request.storage.filename"] = request.storage_options.filename
        if request.storage_options.expires_after:
            attributes["gen_ai.request.storage.expires_after"] = request.storage_options.expires_after
        if request.storage_options.HasField("public_url"):
            attributes["gen_ai.request.storage.public_url"] = True

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
    if usage.HasField("cost_in_usd_ticks"):
        attributes["gen_ai.usage.cost_in_usd_ticks"] = usage.cost_in_usd_ticks

    attributes["gen_ai.response.0.video.respect_moderation"] = response.respect_moderation
    if response._video.url:
        attributes["gen_ai.response.0.video.url"] = response._video.url
    attributes["gen_ai.response.0.video.duration"] = response.duration
    if response.file_output and response.file_output.file_id:
        attributes["gen_ai.response.0.video.file_id"] = response.file_output.file_id
    if response.public_url:
        attributes["gen_ai.response.0.video.public_url"] = response.public_url
    if response.public_url_error:
        attributes["gen_ai.response.0.video.public_url_error"] = response.public_url_error
    if response.storage_error:
        attributes["gen_ai.response.0.video.storage_error"] = response.storage_error

    return attributes


def _make_extend_request(
    prompt: str,
    model: Union[VideoGenerationModel, str],
    *,
    video_url: Optional[str] = None,
    video_file_id: Optional[str] = None,
    duration: Optional[int],
    storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
) -> video_pb2.ExtendVideoRequest:
    _validate_video_inputs(video_url=video_url, video_file_id=video_file_id)
    if video_url is None and video_file_id is None:
        raise ValueError("One of video_url or video_file_id must be set for a request.")

    request = video_pb2.ExtendVideoRequest(prompt=prompt, model=model)
    if video_url is not None:
        request.video.CopyFrom(video_pb2.VideoUrlContent(url=video_url))
    else:
        request.video.CopyFrom(video_pb2.VideoUrlContent(file_id=video_file_id))

    if duration is not None:
        request.duration = duration
    if storage_options is not None:
        request.storage_options.CopyFrom(_resolve_storage_options_pb(storage_options))
    return request


def _make_extend_span_request_attributes(request: video_pb2.ExtendVideoRequest) -> dict[str, Any]:
    """Creates the video extension span request attributes."""
    attributes: dict[str, Any] = {
        "gen_ai.operation.name": "extend_video",
        "gen_ai.request.model": request.model,
        "gen_ai.provider.name": "xai",
        "server.address": "api.x.ai",
        "gen_ai.output.type": "video",
    }

    if should_disable_sensitive_attributes():
        return attributes

    attributes["gen_ai.prompt"] = request.prompt

    if request.HasField("storage_options"):
        attributes["gen_ai.request.storage"] = True
        if request.storage_options.filename:
            attributes["gen_ai.request.storage.filename"] = request.storage_options.filename
        if request.storage_options.expires_after:
            attributes["gen_ai.request.storage.expires_after"] = request.storage_options.expires_after
        if request.storage_options.HasField("public_url"):
            attributes["gen_ai.request.storage.public_url"] = True

    if request.HasField("duration"):
        attributes["gen_ai.request.video.duration"] = request.duration

    return attributes


def _make_extend_span_response_attributes(
    request: video_pb2.ExtendVideoRequest, response: VideoResponse
) -> dict[str, Any]:
    """Creates the video extension span response attributes."""
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
    if usage.HasField("cost_in_usd_ticks"):
        attributes["gen_ai.usage.cost_in_usd_ticks"] = usage.cost_in_usd_ticks

    attributes["gen_ai.response.0.video.respect_moderation"] = response.respect_moderation
    if response._video.url:
        attributes["gen_ai.response.0.video.url"] = response._video.url
    attributes["gen_ai.response.0.video.duration"] = response.duration
    if response.file_output and response.file_output.file_id:
        attributes["gen_ai.response.0.video.file_id"] = response.file_output.file_id
    if response.public_url:
        attributes["gen_ai.response.0.video.public_url"] = response.public_url
    if response.public_url_error:
        attributes["gen_ai.response.0.video.public_url_error"] = response.public_url_error
    if response.storage_error:
        attributes["gen_ai.response.0.video.storage_error"] = response.storage_error

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
