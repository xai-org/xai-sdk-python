from typing import Optional, Sequence

import requests

from ..__about__ import __version__
from ..image import BaseClient, BaseImageResponse, ImageFormat, convert_image_format_to_pb
from ..proto import image_pb2


class Client(BaseClient):
    """Synchronous client for interacting with the `Image` API."""

    def sample(
        self,
        prompt: str,
        model: str,
        *,
        user: Optional[str] = None,
        image_format: Optional[ImageFormat] = None,
    ) -> "ImageResponse":
        """Samples a single image based on the provided prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use for image generation.
            user: A unique identifier representing your end-user, which can help xAI to monitor and detect abuse.
            image_format: The format of the image to return. One of:
            - `"url"`: The image is returned as a URL.
            - `"base64"`: The image is returned as a base64-encoded string.
            defaults to `"url"` if not specified.

        Returns:
            An `ImageResponse` object allowing access to the generated image.
        """
        image_format = image_format or "url"
        request = image_pb2.GenerateImageRequest(
            prompt=prompt,
            model=model,
            user=user,
            n=1,
            format=convert_image_format_to_pb(image_format),
        )
        response = self._stub.GenerateImage(request)
        return ImageResponse(response, 0)

    def sample_batch(
        self,
        prompt: str,
        model: str,
        n: int,
        *,
        user: Optional[str] = None,
        image_format: Optional[ImageFormat] = None,
    ) -> Sequence["ImageResponse"]:
        """Samples a batch of images based on the provided prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use for image generation.
            n: The number of images to generate.
            user: A unique identifier representing your end-user, which can help xAI to monitor and detect abuse.
            image_format: The format of the image to return. One of:
            - `"url"`: The image is returned as a URL.
            - `"base64"`: The image is returned as a base64-encoded string.
            defaults to `"url"` if not specified.

        Returns:
            A sequence of `ImageResponse` objects, one for each image generated.
        """
        image_format = image_format or "url"
        request = image_pb2.GenerateImageRequest(
            prompt=prompt,
            model=model,
            user=user,
            n=n,
            format=convert_image_format_to_pb(image_format),
        )
        response = self._stub.GenerateImage(request)
        return [ImageResponse(response, i) for i in range(n)]


class ImageResponse(BaseImageResponse):
    """Adds auxiliary functions for handling the image response proto."""

    @property
    def image(self) -> bytes:
        """Returns the image as a JPG byte string. If necessary, attempts to download the image."""
        if self._image.base64:
            return self._decode_base64()
        elif self._image.url:
            response = requests.get(
                self.url,
                headers={"User-Agent": f"XaiSdk/{__version__}"},
                timeout=5,  # 5 seconds
            )
            response.raise_for_status()
            return response.content
        else:
            raise ValueError("Image was not returned via URL or base64.")
