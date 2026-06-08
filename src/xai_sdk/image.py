import base64
import warnings
from typing import Any, Optional, Sequence, Union

import grpc

from .cost import cost_usd_from_usage
from .files import StorageOptions, _resolve_storage_options_pb
from .meta import ProtoDecorator
from .proto import image_pb2, image_pb2_grpc, usage_pb2
from .telemetry import should_disable_sensitive_attributes
from .types import ImageAspectRatio, ImageFormat, ImageGenerationModel, ImageResolution

_IMAGE_ASPECT_RATIO_MAP: dict[ImageAspectRatio, image_pb2.ImageAspectRatio] = {
    "1:1": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_1_1,
    "3:4": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_3_4,
    "4:3": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_4_3,
    "9:16": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_9_16,
    "16:9": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_16_9,
    "2:3": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_2_3,
    "3:2": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_3_2,
    "9:19.5": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_9_19_5,
    "19.5:9": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_19_5_9,
    "9:20": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_9_20,
    "20:9": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_20_9,
    "1:2": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_1_2,
    "2:1": image_pb2.ImageAspectRatio.IMG_ASPECT_RATIO_2_1,
}


class BaseClient:
    """Base Client for interacting with the `Image` API."""

    _stub: image_pb2_grpc.ImageStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = image_pb2_grpc.ImageStub(channel)


class BaseImageResponse(ProtoDecorator[image_pb2.ImageResponse]):
    """Adds auxiliary functions for handling the image response proto."""

    _image: image_pb2.GeneratedImage

    def __init__(self, proto: image_pb2.ImageResponse, index: int) -> None:
        """Initializes a new instance of the `ImageResponse` class.

        Args:
            proto: The proto to wrap.
            index: The index of the image within that proto to expose.
        """
        super().__init__(proto)
        self._image = proto.images[index]

    @property
    def model(self) -> str:
        """The model used to generate the image (ignoring aliases)."""
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
    def prompt(self) -> str:
        """The actual prompt used to generate the image.

        This is different from the prompt used in the request because prompts get rewritten by the
        system.

        .. deprecated::
            This field is no longer populated by the server and always returns an empty string.
            It will be removed in a future release.
        """
        warnings.warn(
            "BaseImageResponse.prompt is deprecated and will be removed in a future release. "
            "The field is no longer populated by the server.",
            DeprecationWarning,
            stacklevel=2,
        )
        return ""

    @property
    def respect_moderation(self) -> bool:
        """Whether the image respects moderation rules."""
        return self._image.respect_moderation

    @property
    def url(self) -> str:
        """Returns the URL under which the image is stored or raises an error."""
        url = self._image.url
        if not url:
            if not self.respect_moderation:
                raise ValueError("Image did not respect moderation rules; URL is not available.")
            raise ValueError("Image was not returned via URL and cannot be fetched.")
        return url

    @property
    def base64(self) -> str:
        """Returns the image as base64-encoded string or raises an error."""
        value = self._image.base64
        if not value:
            if not self.respect_moderation:
                raise ValueError("Image did not respect moderation rules; base64 is not available.")
            raise ValueError("Image was not returned via base64.")
        return value

    @property
    def file_output(self) -> Optional[image_pb2.FileOutput]:
        """The full FileOutput proto if the asset was stored, or None otherwise."""
        if self._image.HasField("file_output"):
            return self._image.file_output
        return None

    @property
    def storage_error(self) -> Optional[str]:
        """Error message if storage was requested but failed, or None on success."""
        if self._image.storage_error:
            return self._image.storage_error
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

    def _decode_base64(self) -> bytes:
        """Returns the raw image buffer from a base64-encoded response."""
        encoded = self.base64
        # Remove the prefix.
        _, encoded_buffer = encoded.split("base64,", 1)
        return base64.b64decode(encoded_buffer)


def _validate_image_inputs(
    image_url: str | None,
    image_file_id: str | None,
    image_urls: Sequence[str] | None,
    image_file_ids: Sequence[str] | None,
) -> None:
    """Validates mutual exclusion constraints on image input parameters.

    `image_urls` and `image_file_ids` may be supplied together so callers can
    mix URL/base64 and file-ID references in the same multi-image request.
    When both are provided, file IDs are appended first, then URLs.
    """
    if image_url is not None and image_file_id is not None:
        raise ValueError("Only one of image_url or image_file_id can be set for a request.")
    has_single = image_url is not None or image_file_id is not None
    has_multi = image_urls is not None or image_file_ids is not None
    if has_single and has_multi:
        raise ValueError("Only one of image_url/image_file_id or image_urls/image_file_ids can be set for a request.")


def _make_generate_request(
    prompt: str,
    model: Union[ImageGenerationModel, str],
    *,
    n: int = 1,
    image_url: str | None = None,
    image_file_id: str | None = None,
    image_urls: Sequence[str] | None = None,
    image_file_ids: Sequence[str] | None = None,
    user: str | None = None,
    image_format: ImageFormat | None = None,
    aspect_ratio: ImageAspectRatio | None = None,
    resolution: ImageResolution | None = None,
    storage_options: Union[StorageOptions, image_pb2.StorageOptions, None] = None,
) -> image_pb2.GenerateImageRequest:
    _validate_image_inputs(image_url, image_file_id, image_urls, image_file_ids)

    image_format = image_format or "url"
    request = image_pb2.GenerateImageRequest(
        prompt=prompt,
        model=model,
        user=user,
        n=n,
        format=convert_image_format_to_pb(image_format),
    )
    if image_url is not None:
        request.image.CopyFrom(
            image_pb2.ImageUrlContent(
                image_url=image_url,
                detail=image_pb2.ImageDetail.DETAIL_AUTO,
            )
        )
    elif image_file_id is not None:
        request.image.CopyFrom(
            image_pb2.ImageUrlContent(
                file_id=image_file_id,
                detail=image_pb2.ImageDetail.DETAIL_AUTO,
            )
        )
    # When both `image_file_ids` and `image_urls` are provided we send both
    # lists in the same `images` field. File IDs are appended first so callers
    # can predict the resulting `<IMAGE_N>` positional indices used by the
    # model prompt.
    if image_file_ids is not None:
        request.images.extend(
            [
                image_pb2.ImageUrlContent(
                    file_id=fid,
                    detail=image_pb2.ImageDetail.DETAIL_AUTO,
                )
                for fid in image_file_ids
            ]
        )
    if image_urls is not None:
        request.images.extend(
            [
                image_pb2.ImageUrlContent(
                    image_url=url,
                    detail=image_pb2.ImageDetail.DETAIL_AUTO,
                )
                for url in image_urls
            ]
        )
    if aspect_ratio is not None:
        request.aspect_ratio = convert_image_aspect_ratio_to_pb(aspect_ratio)
    if resolution is not None:
        request.resolution = convert_image_resolution_to_pb(resolution)
    if storage_options is not None:
        request.storage_options.CopyFrom(_resolve_storage_options_pb(storage_options))
    return request


def _make_span_request_attributes(request: image_pb2.GenerateImageRequest) -> dict[str, str | int]:
    """Creates the image sampling span request attributes."""
    attributes: dict[str, str | int] = {
        "gen_ai.operation.name": "generate_image",
        "gen_ai.request.model": request.model,
        "gen_ai.provider.name": "xai",
        "gen_ai.output.type": "image",
    }

    if should_disable_sensitive_attributes():
        return attributes

    attributes["gen_ai.request.image.format"] = (
        image_pb2.ImageFormat.Name(request.format).removeprefix("IMG_FORMAT_").lower()
    )
    attributes["gen_ai.prompt"] = request.prompt

    if request.HasField("storage_options"):
        attributes["gen_ai.request.storage"] = True
        if request.storage_options.filename:
            attributes["gen_ai.request.storage.filename"] = request.storage_options.filename
        if request.storage_options.expires_after:
            attributes["gen_ai.request.storage.expires_after"] = request.storage_options.expires_after
        if request.storage_options.HasField("public_url"):
            attributes["gen_ai.request.storage.public_url"] = True

    if request.HasField("n"):
        attributes["gen_ai.request.image.count"] = request.n
    if request.HasField("aspect_ratio"):
        attributes["gen_ai.request.image.aspect_ratio"] = _format_image_aspect_ratio(request.aspect_ratio)
    if request.HasField("resolution"):
        attributes["gen_ai.request.image.resolution"] = (
            image_pb2.ImageResolution.Name(request.resolution).removeprefix("IMG_RESOLUTION_").lower()
        )
    if request.user:
        attributes["user_id"] = request.user

    return attributes


def _collect_per_image_attributes(
    prefix: str,
    response: BaseImageResponse,
    image_format: int,
) -> dict[str, Any]:
    """Collects span attributes for a single generated image."""
    attributes: dict[str, Any] = {
        f"{prefix}.respect_moderation": response.respect_moderation,
    }
    if image_format == image_pb2.ImageFormat.IMG_FORMAT_URL and response._image.url:
        attributes[f"{prefix}.url"] = response._image.url
    elif image_format == image_pb2.ImageFormat.IMG_FORMAT_BASE64 and response._image.base64:
        attributes[f"{prefix}.base64"] = response._image.base64
    if response.file_output and response.file_output.file_id:
        attributes[f"{prefix}.file_id"] = response.file_output.file_id
    if response.public_url:
        attributes[f"{prefix}.public_url"] = response.public_url
    if response.public_url_error:
        attributes[f"{prefix}.public_url_error"] = response.public_url_error
    if response.storage_error:
        attributes[f"{prefix}.storage_error"] = response.storage_error
    return attributes


def _make_span_response_attributes(
    request: image_pb2.GenerateImageRequest, responses: Sequence[BaseImageResponse]
) -> dict[str, Any]:
    """Creates the image sampling span response attributes."""
    attributes: dict[str, Any] = {
        "gen_ai.response.model": request.model,
    }

    if should_disable_sensitive_attributes():
        return attributes

    if responses:
        usage = responses[0].usage
        attributes["gen_ai.usage.input_tokens"] = usage.prompt_tokens
        attributes["gen_ai.usage.output_tokens"] = usage.completion_tokens
        attributes["gen_ai.usage.total_tokens"] = usage.total_tokens
        attributes["gen_ai.usage.reasoning_tokens"] = usage.reasoning_tokens
        attributes["gen_ai.usage.cached_prompt_text_tokens"] = usage.cached_prompt_text_tokens
        attributes["gen_ai.usage.prompt_text_tokens"] = usage.prompt_text_tokens
        attributes["gen_ai.usage.prompt_image_tokens"] = usage.prompt_image_tokens
        if usage.HasField("cost_in_usd_ticks"):
            attributes["gen_ai.usage.cost_in_usd_ticks"] = usage.cost_in_usd_ticks

    attributes["gen_ai.response.image.format"] = (
        image_pb2.ImageFormat.Name(request.format).removeprefix("IMG_FORMAT_").lower()
    )
    for index, response in enumerate(responses):
        attributes.update(_collect_per_image_attributes(f"gen_ai.response.{index}.image", response, request.format))

    return attributes


def convert_image_format_to_pb(image_format: ImageFormat) -> image_pb2.ImageFormat:
    """Converts a string literal representation of an image format to its protobuf enum variant."""
    match image_format:
        case "base64":
            return image_pb2.ImageFormat.IMG_FORMAT_BASE64
        case "url":
            return image_pb2.ImageFormat.IMG_FORMAT_URL
        case _:
            raise ValueError(f"Invalid image format {image_format}.")


def convert_image_aspect_ratio_to_pb(aspect_ratio: ImageAspectRatio) -> image_pb2.ImageAspectRatio:
    """Converts a string literal representation of an image aspect ratio to its protobuf enum variant."""
    try:
        return _IMAGE_ASPECT_RATIO_MAP[aspect_ratio]
    except KeyError as exc:
        raise ValueError(f"Invalid image aspect ratio {aspect_ratio}.") from exc


def _format_image_aspect_ratio(aspect_ratio: image_pb2.ImageAspectRatio) -> str:
    """Formats the protobuf enum into the public string form (e.g. '9:19.5')."""
    name = image_pb2.ImageAspectRatio.Name(aspect_ratio).removeprefix("IMG_ASPECT_RATIO_")
    if name == "AUTO":
        return "auto"
    # Protobuf encodes the "19.5" ratio portion as "19_5".
    return name.replace("19_5", "19.5").replace("_", ":")


def convert_image_resolution_to_pb(resolution: ImageResolution) -> image_pb2.ImageResolution:
    """Converts a string literal representation of an image resolution to its protobuf enum variant."""
    match resolution:
        case "1k":
            return image_pb2.ImageResolution.IMG_RESOLUTION_1K
        case "2k":
            return image_pb2.ImageResolution.IMG_RESOLUTION_2K
        case _:
            raise ValueError(f"Invalid image resolution {resolution}.")
