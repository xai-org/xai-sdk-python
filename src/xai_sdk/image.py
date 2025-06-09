import base64
from typing import Literal, Union

import grpc

from .meta import ProtoDecorator
from .proto import image_pb2, image_pb2_grpc

ImageFormat = Literal["base64", "url"]


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
    def prompt(self) -> str:
        """The actual prompt used to generate the image.

        This is different from the prompt used in the request because prompts get rewritten by the
        system.
        """
        return self._image.up_sampled_prompt

    @property
    def url(self) -> str:
        """Returns the URL under which the image is stored or raises an error."""
        url = self._image.url
        if not url:
            raise ValueError("Image was not returned via URL and cannot be fetched.")
        return url

    @property
    def base64(self) -> str:
        """Returns the image as base64-encoded string or raises an error."""
        value = self._image.base64
        if not value:
            raise ValueError("Image was not returned via base64.")
        return value

    def _decode_base64(self) -> bytes:
        """Returns the raw image buffer from a base64-encoded response."""
        encoded = self.base64
        # Remove the prefix.
        _, encoded_buffer = encoded.split("base64,", 1)
        return base64.b64decode(encoded_buffer)


def convert_image_format_to_pb(image_format: ImageFormat) -> image_pb2.ImageFormat:
    """Converts a string literal representation of an image format to its protobuf enum variant."""
    match image_format:
        case "base64":
            return image_pb2.ImageFormat.IMG_FORMAT_BASE64
        case "url":
            return image_pb2.ImageFormat.IMG_FORMAT_URL
        case _:
            raise ValueError(f"Invalid image format {image_format}.")
