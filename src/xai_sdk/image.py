import base64
from typing import Any, Sequence, Union

import grpc

from .meta import ProtoDecorator
from .proto import image_pb2, image_pb2_grpc, usage_pb2
from .telemetry import should_disable_sensitive_attributes
from .types.image import ImageAspectRatio, ImageFormat, ImageResolution

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
    def prompt(self) -> str:
        """The actual prompt used to generate the image.

        This is different from the prompt used in the request because prompts get rewritten by the
        system.
        """
        return self._image.up_sampled_prompt

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

    def _decode_base64(self) -> bytes:
        """Returns the raw image buffer from a base64-encoded response."""
        encoded = self.base64
        # Remove the prefix.
        _, encoded_buffer = encoded.split("base64,", 1)
        return base64.b64decode(encoded_buffer)


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


def _make_span_response_attributes(
    request: image_pb2.GenerateImageRequest, responses: Sequence[BaseImageResponse]
) -> dict[str, Any]:
    """Creates the image sampling span response attributes."""
    attributes: dict[str, Any] = {
        "gen_ai.response.model": request.model,
    }

    if should_disable_sensitive_attributes():
        return attributes

    # All of these attributes are the same for all images in this response.
    if responses:
        usage = responses[0].usage
        attributes["gen_ai.usage.input_tokens"] = usage.prompt_tokens
        attributes["gen_ai.usage.output_tokens"] = usage.completion_tokens
        attributes["gen_ai.usage.total_tokens"] = usage.total_tokens
        attributes["gen_ai.usage.reasoning_tokens"] = usage.reasoning_tokens
        attributes["gen_ai.usage.cached_prompt_text_tokens"] = usage.cached_prompt_text_tokens
        attributes["gen_ai.usage.prompt_text_tokens"] = usage.prompt_text_tokens
        attributes["gen_ai.usage.prompt_image_tokens"] = usage.prompt_image_tokens

    attributes["gen_ai.response.image.format"] = (
        image_pb2.ImageFormat.Name(request.format).removeprefix("IMG_FORMAT_").lower()
    )
    for index, response in enumerate(responses):
        attributes[f"gen_ai.response.{index}.image.up_sampled_prompt"] = response.prompt
        attributes[f"gen_ai.response.{index}.image.respect_moderation"] = response.respect_moderation
        if request.format == image_pb2.ImageFormat.IMG_FORMAT_URL:
            if response._image.url:
                attributes[f"gen_ai.response.{index}.image.url"] = response._image.url
        elif request.format == image_pb2.ImageFormat.IMG_FORMAT_BASE64:
            if response._image.base64:
                attributes[f"gen_ai.response.{index}.image.base64"] = response._image.base64

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
        case _:
            raise ValueError(f"Invalid image resolution {resolution}.")
