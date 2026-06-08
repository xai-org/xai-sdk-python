from typing import Optional, Sequence, Union

import aiohttp
from opentelemetry.trace import SpanKind

from ..__about__ import __version__
from ..files import StorageOptions
from ..image import (
    BaseClient,
    BaseImageResponse,
    ImageAspectRatio,
    ImageFormat,
    ImageResolution,
    _make_generate_request,
    _make_span_request_attributes,
    _make_span_response_attributes,
)
from ..proto import batch_pb2, image_pb2
from ..telemetry import get_tracer
from ..types import ImageGenerationModel

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Asynchronous client for interacting with the `Image` API."""

    def prepare(
        self,
        prompt: str,
        model: Union[ImageGenerationModel, str],
        *,
        batch_request_id: Optional[str] = None,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        image_urls: Optional[Sequence[str]] = None,
        image_file_ids: Optional[Sequence[str]] = None,
        user: Optional[str] = None,
        image_format: Optional[ImageFormat] = None,
        aspect_ratio: Optional[ImageAspectRatio] = None,
        resolution: Optional[ImageResolution] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> batch_pb2.BatchRequest:
        """Prepares an image generation request for batch processing.

        Use this method to prepare image generation requests that can be added to a batch.
        This does not execute the generation - use `client.batch.add()` to submit requests.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use for image generation.
            batch_request_id: An optional user-provided identifier for the batch request.
                **If provided, it must be unique within the batch.** Used to identify the
                corresponding result when the response is returned.
            image_url: The URL or base64-encoded string of an input image to use as a starting point.
                Cannot be set together with `image_file_id`, `image_urls`, or `image_file_ids`.
                Only supported for grok-imagine models.
            image_file_id: The file ID of an input image to use as a starting point.
                Cannot be set together with `image_url`, `image_urls`, or `image_file_ids`.
                Only supported for grok-imagine models.
            image_urls: Optional list of input images for multi-reference image editing.
                Cannot be set together with single-image params (`image_url` /
                `image_file_id`). May be combined with `image_file_ids` to mix
                URL/base64 and file-ID references in the same request; file IDs
                are appended first in that case.
                Only supported for grok-imagine models.
            image_file_ids: Optional list of input image file IDs for multi-reference image editing.
                Cannot be set together with single-image params (`image_url` /
                `image_file_id`). May be combined with `image_urls` to mix
                URL/base64 and file-ID references in the same request.
                Only supported for grok-imagine models.
            user: A unique identifier representing your end-user.
            image_format: The format of the image to return ("url" or "base64"). Defaults to "url".
            aspect_ratio: The aspect ratio of the image to generate.
            resolution: The image resolution to generate ("1k" or "2k").
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.png"}  # store privately, no expiry
                    storage_options={"filename": "output.png", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.png", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.png", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            A `BatchRequest` proto ready to be added to a batch.

        Examples:
            ```python
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Create a batch
            batch = await client.batch.create("my_image_batch")

            # Prepare batch requests for multiple images
            requests = [
                client.image.prepare(
                    prompt="A sunset over mountains",
                    model="grok-imagine-image",
                    batch_request_id="sunset_1",
                ),
                client.image.prepare(
                    prompt="A forest in autumn",
                    model="grok-imagine-image",
                    batch_request_id="forest_1",
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
            image_file_id=image_file_id,
            image_urls=image_urls,
            image_file_ids=image_file_ids,
            user=user,
            image_format=image_format,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            storage_options=storage_options,
        )
        return batch_pb2.BatchRequest(
            image_request=request,
            batch_request_id=batch_request_id or "",
        )

    async def sample(
        self,
        prompt: str,
        model: Union[ImageGenerationModel, str],
        *,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        image_urls: Optional[Sequence[str]] = None,
        image_file_ids: Optional[Sequence[str]] = None,
        user: Optional[str] = None,
        image_format: Optional[ImageFormat] = None,
        aspect_ratio: Optional[ImageAspectRatio] = None,
        resolution: Optional[ImageResolution] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> "ImageResponse":
        """Samples a single image asynchronously based on the provided prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use for image generation.
            image_url: The URL or base64-encoded string of an input image to use as a starting point for generation.
            This field cannot be set together with `image_file_id`, `image_urls`, or `image_file_ids`.
            Only supported for grok-imagine models.
            image_file_id: The file ID of an input image to use as a starting point for generation.
            Cannot be set together with `image_url`, `image_urls`, or `image_file_ids`.
            Only supported for grok-imagine models.
            image_urls: Optional list of input images for multi-reference image editing.
            Each image is a URL or base64-encoded string, matching the `image_url` format.
            Cannot be set together with single-image params (`image_url` /
            `image_file_id`). May be combined with `image_file_ids` to mix
            URL/base64 and file-ID references in the same request; file IDs
            are appended first in that case.
            Only supported for grok-imagine models.
            image_file_ids: Optional list of input image file IDs for multi-reference image editing.
            Cannot be set together with single-image params (`image_url` /
            `image_file_id`). May be combined with `image_urls` to mix
            URL/base64 and file-ID references in the same request.
            Only supported for grok-imagine models.
            user: A unique identifier representing your end-user, which can help xAI to monitor and detect abuse.
            image_format: The format of the image to return. One of:
            - `"url"`: The image is returned as a URL.
            - `"base64"`: The image is returned as a base64-encoded string.
            defaults to `"url"` if not specified.
            aspect_ratio: The aspect ratio of the image to generate. One of:
            - `"1:1"`
            - `"16:9"`
            - `"9:16"`
            - `"4:3"`
            - `"3:4"`
            - `"3:2"`
            - `"2:3"`
            - `"2:1"`
            - `"1:2"`
            - `"20:9"`
            - `"9:20"`
            - `"19.5:9"`
            - `"9:19.5"`
            Only supported for grok-imagine models.
            resolution: The image resolution to generate. One of:
            - `"1k"`: ~1 megapixel total. Dimensions vary by aspect ratio.
            - `"2k"`: ~4 megapixels total. Dimensions vary by aspect ratio.
            Only supported for grok-imagine models.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.png"}  # store privately, no expiry
                    storage_options={"filename": "output.png", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.png", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.png", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            An `ImageResponse` object allowing access to the generated image.
        """
        request = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            image_file_id=image_file_id,
            image_urls=image_urls,
            image_file_ids=image_file_ids,
            user=user,
            image_format=image_format,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            storage_options=storage_options,
        )
        with tracer.start_as_current_span(
            name=f"image.sample {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_span_request_attributes(request),
        ) as span:
            response_pb = await self._stub.GenerateImage(request)
            image_response = ImageResponse(response_pb, 0)
            span.set_attributes(_make_span_response_attributes(request, [image_response]))
            return image_response

    async def sample_batch(
        self,
        prompt: str,
        model: Union[ImageGenerationModel, str],
        n: int,
        *,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        image_urls: Optional[Sequence[str]] = None,
        image_file_ids: Optional[Sequence[str]] = None,
        user: Optional[str] = None,
        image_format: Optional[ImageFormat] = None,
        aspect_ratio: Optional[ImageAspectRatio] = None,
        resolution: Optional[ImageResolution] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> Sequence["ImageResponse"]:
        """Samples a batch of images asynchronously based on the provided prompt.

        Args:
            prompt: The prompt to generate an image from.
            model: The model to use for image generation.
            n: The number of images to generate.
            image_url: The URL or base64-encoded string of an input image to use as a starting point for generation.
            This field cannot be set together with `image_file_id`, `image_urls`, or `image_file_ids`.
            Only supported for grok-imagine models.
            image_file_id: The file ID of an input image to use as a starting point for generation.
            Cannot be set together with `image_url`, `image_urls`, or `image_file_ids`.
            Only supported for grok-imagine models.
            image_urls: Optional list of input images for multi-reference image editing.
            Each image is a URL or base64-encoded string, matching the `image_url` format.
            Cannot be set together with single-image params (`image_url` /
            `image_file_id`). May be combined with `image_file_ids` to mix
            URL/base64 and file-ID references in the same request; file IDs
            are appended first in that case.
            Only supported for grok-imagine models.
            image_file_ids: Optional list of input image file IDs for multi-reference image editing.
            Cannot be set together with single-image params (`image_url` /
            `image_file_id`). May be combined with `image_urls` to mix
            URL/base64 and file-ID references in the same request.
            Only supported for grok-imagine models.
            user: A unique identifier representing your end-user, which can help xAI to monitor and detect abuse.
            image_format: The format of the image to return. One of:
            - `"url"`: The image is returned as a URL.
            - `"base64"`: The image is returned as a base64-encoded string.
            defaults to `"url"` if not specified.
            aspect_ratio: The aspect ratio of the image to generate. One of:
            - `"1:1"`
            - `"16:9"`
            - `"9:16"`
            - `"4:3"`
            - `"3:4"`
            - `"3:2"`
            - `"2:3"`
            - `"2:1"`
            - `"1:2"`
            - `"20:9"`
            - `"9:20"`
            - `"19.5:9"`
            - `"9:19.5"`
            Only supported for grok-imagine models.
            resolution: The image resolution to generate. One of:
            - `"1k"`: ~1 megapixel total. Dimensions vary by aspect ratio.
            - `"2k"`: ~4 megapixels total. Dimensions vary by aspect ratio.
            Only supported for grok-imagine models.
            storage_options: Persist the results to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.png"}  # store privately, no expiry
                    storage_options={"filename": "output.png", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.png", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.png", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            A sequence of `ImageResponse` objects, one for each image generated.
        """
        request = _make_generate_request(
            prompt,
            model,
            n=n,
            image_url=image_url,
            image_file_id=image_file_id,
            image_urls=image_urls,
            image_file_ids=image_file_ids,
            user=user,
            image_format=image_format,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            storage_options=storage_options,
        )
        with tracer.start_as_current_span(
            name=f"image.sample_batch {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_span_request_attributes(request),
        ) as span:
            response_pb = await self._stub.GenerateImage(request)
            image_responses = [ImageResponse(response_pb, i) for i in range(n)]
            span.set_attributes(_make_span_response_attributes(request, image_responses))
            return image_responses


class ImageResponse(BaseImageResponse):
    """Adds auxiliary functions for handling the image response proto."""

    @property
    async def image(self) -> bytes:
        """Returns the image as a JPG byte string. If necessary, attempts to download the image."""
        if self._image.base64:
            return self._decode_base64()
        elif self._image.url:
            async with aiohttp.request(
                "GET",
                self.url,
                headers={"User-Agent": f"XaiSdk/{__version__}"},
            ) as session:
                session.raise_for_status()
                return await session.read()
        else:
            raise ValueError("Image was not returned via base64 or URL.")
