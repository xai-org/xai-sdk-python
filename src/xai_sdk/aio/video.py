import asyncio
import datetime
import warnings
from typing import Optional, Sequence, Union

from opentelemetry.trace import SpanKind

from ..files import StorageOptions
from ..poll_timer import PollTimer
from ..proto import batch_pb2, deferred_pb2, image_pb2, video_pb2
from ..telemetry import get_tracer
from ..types import VideoGenerationModel
from ..video import (
    DEFAULT_VIDEO_POLL_INTERVAL,
    DEFAULT_VIDEO_TIMEOUT,
    BaseClient,
    VideoAspectRatio,
    VideoGenerationError,
    VideoResolution,
    VideoResponse,
    _make_extend_request,
    _make_extend_span_request_attributes,
    _make_extend_span_response_attributes,
    _make_generate_request,
    _make_span_request_attributes,
    _make_span_response_attributes,
)

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Asynchronous client for interacting with the `Video` API."""

    def prepare(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        *,
        batch_request_id: Optional[str] = None,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        video_file_id: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
        reference_image_urls: Optional[Sequence[str]] = None,
        reference_image_file_ids: Optional[Sequence[str]] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> batch_pb2.BatchRequest:
        """Prepares a video generation request for batch processing.

        Use this method to prepare video generation requests that can be added to a batch.
        This does not execute the generation - use `client.batch.add()` to submit requests.

        Args:
            prompt: The prompt to generate a video from.
            model: The model to use for video generation.
            batch_request_id: An optional user-provided identifier for the batch request.
                **If provided, it must be unique within the batch.** Used to identify the
                corresponding result when the response is returned.
            image_url: The URL of an input image to use as a starting frame.
                Cannot be set together with ``image_file_id``.
            image_file_id: The file ID of an input image to use as a starting frame.
                Cannot be set together with ``image_url``.
            video_url: The URL of an input video to use as a starting point.
                Cannot be set together with ``video_file_id``.
            video_file_id: The file ID of an input video to use as a starting point.
                Cannot be set together with ``video_url``.
            duration: The duration of the video to generate in seconds.
            aspect_ratio: The aspect ratio of the video to generate.
            resolution: The video resolution to generate.
            reference_image_urls: Optional list of reference image URLs for
                reference-to-video (R2V) generation. When provided (and `image_url`
                is not set), generates video using these images as style/content references.
                May be combined with ``reference_image_file_ids`` to mix URL/base64
                and file-ID references in the same request; file IDs are appended
                first in that case.
            reference_image_file_ids: Optional list of reference image file IDs for
                reference-to-video (R2V) generation. May be combined with
                ``reference_image_urls`` to mix URL/base64 and file-ID references
                in the same request.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.mp4"}  # store privately, no expiry
                    storage_options={"filename": "output.mp4", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.mp4", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.mp4", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            A `BatchRequest` proto ready to be added to a batch.

        Examples:
            ```python
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Create a batch
            batch = await client.batch.create("my_video_batch")

            # Prepare batch requests for multiple videos
            requests = [
                client.video.prepare(
                    prompt="A timelapse of a sunset",
                    model="grok-imagine-video",
                    batch_request_id="sunset_video_1",
                ),
                client.video.prepare(
                    prompt="Waves crashing on a beach",
                    model="grok-imagine-video",
                    batch_request_id="beach_video_1",
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
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            reference_image_urls=reference_image_urls,
            reference_image_file_ids=reference_image_file_ids,
            storage_options=storage_options,
        )

        return batch_pb2.BatchRequest(
            video_request=request,
            batch_request_id=batch_request_id or "",
        )

    def prepare_extension(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        video_url: Optional[str] = None,
        *,
        video_file_id: Optional[str] = None,
        batch_request_id: Optional[str] = None,
        duration: Optional[int] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> batch_pb2.BatchRequest:
        """Prepares a video extension request for batch processing.

        Use this method to prepare video extension requests that can be added to a batch.
        This does not execute the extension - use `client.batch.add()` to submit requests.

        Args:
            prompt: Prompt describing what should happen next in the video.
            model: The model to use for video extension.
            video_url: The URL of the input video to extend.
                Cannot be set together with ``video_file_id``.
            video_file_id: The file ID of the input video to extend.
                Cannot be set together with ``video_url``.
            batch_request_id: An optional user-provided identifier for the batch request.
                **If provided, it must be unique within the batch.**
            duration: Duration of the extension segment in seconds (1-10).
                Defaults to 6 seconds if not specified.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.mp4"}  # store privately, no expiry
                    storage_options={"filename": "output.mp4", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.mp4", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.mp4", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            A `BatchRequest` proto ready to be added to a batch.
        """
        request = _make_extend_request(
            prompt,
            model,
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            storage_options=storage_options,
        )

        return batch_pb2.BatchRequest(
            video_extension_request=request,
            batch_request_id=batch_request_id or "",
        )

    async def start(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        *,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        video_file_id: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
        reference_image_urls: Optional[Sequence[str]] = None,
        reference_image_file_ids: Optional[Sequence[str]] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> deferred_pb2.StartDeferredResponse:
        """Starts a video generation request and returns a request_id for polling.

        See `generate()` for full parameter documentation.
        """
        request = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            image_file_id=image_file_id,
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            reference_image_urls=reference_image_urls,
            reference_image_file_ids=reference_image_file_ids,
            storage_options=storage_options,
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
        model: Union[VideoGenerationModel, str],
        *,
        image_url: Optional[str] = None,
        image_file_id: Optional[str] = None,
        video_url: Optional[str] = None,
        video_file_id: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: Optional[VideoAspectRatio] = None,
        resolution: Optional[VideoResolution] = None,
        reference_image_urls: Optional[Sequence[str]] = None,
        reference_image_file_ids: Optional[Sequence[str]] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
        timeout: Optional[datetime.timedelta] = None,
        interval: Optional[datetime.timedelta] = None,
    ) -> VideoResponse:
        """Generates a video from a text prompt and returns the completed response.

        This is a convenience method that starts asynchronous video generation and
        automatically polls for the result until it completes, times out, or fails.

        Supports four generation modes depending on which optional inputs are provided:

        - **Text-to-video**: Only a `prompt` is provided.
        - **Image-to-video**: An `image_url` or `image_file_id` is provided; the image is
          used as the first frame.
        - **Reference-to-video**: `reference_image_urls` or `reference_image_file_ids` are
          provided; generates video using the images as style/content references.
        - **Video editing**: A `video_url` or `video_file_id` is provided; the video is edited
          based on the prompt.

        Args:
            prompt: The text prompt to generate a video from.
            model: The model to use for video generation.
            image_url: The URL or base64-encoded data URL of an input image to use as
                the first frame (image-to-video). Cannot be combined with `image_file_id`
                or `video_url`.
            image_file_id: The file ID of an input image to use as the first frame
                (image-to-video). Cannot be combined with `image_url`.
            video_url: The URL or base64-encoded data URL of an input video to edit
                based on the prompt (video-to-video). Cannot be combined with `video_file_id`
                or `image_url`.
            video_file_id: The file ID of an input video to edit based on the prompt
                (video-to-video). Cannot be combined with `video_url`.
            duration: Duration of the video to generate in seconds (1-15).
                Defaults to 8 seconds if not specified.
            aspect_ratio: The aspect ratio of the video to generate.
                Defaults to ``"16:9"`` if not specified.
            resolution: The video resolution to generate.
                Defaults to ``"480p"`` if not specified.
            reference_image_urls: Optional list of reference image URLs for
                reference-to-video (R2V) generation. When provided (and `image_url`
                is not set), generates video using these images as style/content references.
                May be combined with `reference_image_file_ids` to mix URL/base64
                and file-ID references in the same request; file IDs are appended
                first in that case.
            reference_image_file_ids: Optional list of reference image file IDs for
                reference-to-video (R2V) generation. May be combined with
                `reference_image_urls` to mix URL/base64 and file-ID references
                in the same request.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.mp4"}  # store privately, no expiry
                    storage_options={"filename": "output.mp4", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.mp4", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.mp4", "public_url": {"expires_after": 86400}}  # + expiring URL
            timeout: Maximum time to wait for video generation to complete.
                Defaults to 10 minutes.
            interval: Polling interval between status checks.
                Defaults to 1 second.

        Returns:
            A `VideoResponse` containing the generated video URL, duration, and usage info.

        Raises:
            VideoGenerationError: If the video generation fails.
            RuntimeError: If the deferred request expires or completes without a response.
            TimeoutError: If polling exceeds the specified timeout.

        Examples:
            ```python
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Text-to-video
            response = await client.video.generate(
                prompt="A timelapse of a sunset over the ocean",
                model="grok-imagine-video",
            )
            print(response.url)

            # Image-to-video
            response = await client.video.generate(
                prompt="The scene slowly comes to life",
                model="grok-imagine-video",
                image_url="https://example.com/photo.jpg",
            )
            print(response.url)

            # Reference-to-video (R2V)
            response = await client.video.generate(
                prompt="A cinematic scene with characters in a forest",
                model="grok-imagine-video",
                reference_image_urls=[
                    "https://example.com/reference1.jpg",
                    "https://example.com/reference2.jpg",
                ],
            )
            print(response.url)

            # Video editing
            response = await client.video.generate(
                prompt="Add a rainbow in the sky",
                model="grok-imagine-video",
                video_url="https://example.com/my-video.mp4",
            )
            print(response.url)
            ```
        """
        timer = PollTimer(
            timeout or DEFAULT_VIDEO_TIMEOUT,
            interval or DEFAULT_VIDEO_POLL_INTERVAL,
            context="waiting for video to be generated",
        )
        request_pb = _make_generate_request(
            prompt,
            model,
            image_url=image_url,
            image_file_id=image_file_id,
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            reference_image_urls=reference_image_urls,
            reference_image_file_ids=reference_image_file_ids,
            storage_options=storage_options,
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
                    case deferred_pb2.DeferredStatus.FAILED:
                        if r.HasField("response") and r.response.HasField("error"):
                            error = r.response.error
                            raise VideoGenerationError(error.code, error.message)
                        raise VideoGenerationError("UNKNOWN", "Video generation failed with no error details.")
                    case unknown_status:
                        warnings.warn(
                            f"Encountered unknown status: {unknown_status} whilst waiting for video generation.",
                            stacklevel=2,
                        )
                        await asyncio.sleep(timer.sleep_interval_or_raise())

    async def extend_start(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        video_url: Optional[str] = None,
        *,
        video_file_id: Optional[str] = None,
        duration: Optional[int] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
    ) -> deferred_pb2.StartDeferredResponse:
        """Starts a video extension request and returns a request_id for polling.

        Args:
            prompt: Prompt describing what should happen next in the video.
            model: The model to use for video extension.
            video_url: The URL of the input video to extend. The extension continues
                from the end of this video. Input video must be between 2 and 30 seconds long.
                Cannot be set together with ``video_file_id``.
            video_file_id: The file ID of the input video to extend. The extension continues
                from the end of this video. Cannot be set together with ``video_url``.
            duration: Duration of the extension segment to generate in seconds (1-10).
                Defaults to 6 seconds if not specified.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.mp4"}  # store privately, no expiry
                    storage_options={"filename": "output.mp4", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.mp4", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.mp4", "public_url": {"expires_after": 86400}}  # + expiring URL

        Returns:
            A `StartDeferredResponse` containing the `request_id` for polling.
        """
        request = _make_extend_request(
            prompt,
            model,
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            storage_options=storage_options,
        )

        with tracer.start_as_current_span(
            name=f"video.extend_start {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_extend_span_request_attributes(request),
        ):
            return await self._stub.ExtendVideo(request)

    async def extend(
        self,
        prompt: str,
        model: Union[VideoGenerationModel, str],
        video_url: Optional[str] = None,
        *,
        video_file_id: Optional[str] = None,
        duration: Optional[int] = None,
        storage_options: Optional[Union[StorageOptions, image_pb2.StorageOptions]] = None,
        timeout: Optional[datetime.timedelta] = None,
        interval: Optional[datetime.timedelta] = None,
    ) -> VideoResponse:
        """Extends an existing video by generating continuation content.

        This is a convenience method that starts asynchronous video extension and
        automatically polls for the result until it completes, times out, or fails.
        The generated content continues from the end of the provided input video.

        Multiple extensions can be chained by feeding the returned video URL back
        as the `video_url` for the next call.

        Args:
            prompt: Prompt describing what should happen next in the video.
            model: The model to use for video extension.
            video_url: The URL or base64-encoded data URL of the input video to extend.
                The extension continues from the end of this video.
                Input video must be between 2 and 30 seconds long.
                Cannot be set together with ``video_file_id``.
            video_file_id: The file ID of the input video to extend. The extension continues
                from the end of this video. Cannot be set together with ``video_url``.
            duration: Duration of the extension segment to generate in seconds (1-10).
                Defaults to 6 seconds if not specified.
            storage_options: Persist the result to the Files API. Accepts a dict
                with a required ``filename`` and optional ``expires_after`` and ``public_url`` keys.
                Set ``public_url`` to also create a publicly shareable URL.
                Examples::

                    storage_options={"filename": "output.mp4"}  # store privately, no expiry
                    storage_options={"filename": "output.mp4", "expires_after": 7200}  # auto-delete after 2h
                    storage_options={"filename": "output.mp4", "public_url": True}  # + shareable URL
                    storage_options={"filename": "output.mp4", "public_url": {"expires_after": 86400}}  # + expiring URL
            timeout: Maximum time to wait for video extension to complete.
                Defaults to 10 minutes.
            interval: Polling interval between status checks.
                Defaults to 1 second.

        Returns:
            A `VideoResponse` containing the extended video URL, duration, and usage info.

        Raises:
            VideoGenerationError: If the video extension fails.
            RuntimeError: If the deferred request expires or completes without a response.
            TimeoutError: If polling exceeds the specified timeout.

        Examples:
            ```python
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Extend an existing video
            response = await client.video.extend(
                prompt="The camera slowly zooms out to reveal the city skyline",
                model="grok-imagine-video",
                video_url="https://example.com/my-video.mp4",
                duration=6,
            )
            print(response.url)

            # Chain extensions
            response = await client.video.extend(
                prompt="A bird flies across the sky",
                model="grok-imagine-video",
                video_url=response.url,
            )
            print(response.url)
            ```
        """
        timer = PollTimer(
            timeout or DEFAULT_VIDEO_TIMEOUT,
            interval or DEFAULT_VIDEO_POLL_INTERVAL,
            context="waiting for video extension to be generated",
        )
        request_pb = _make_extend_request(
            prompt,
            model,
            video_url=video_url,
            video_file_id=video_file_id,
            duration=duration,
            storage_options=storage_options,
        )

        with tracer.start_as_current_span(
            name=f"video.extend {model}",
            kind=SpanKind.CLIENT,
            attributes=_make_extend_span_request_attributes(request_pb),
        ) as span:
            start = await self._stub.ExtendVideo(request_pb)

            while True:
                get_req = video_pb2.GetDeferredVideoRequest(request_id=start.request_id)

                r = await self._stub.GetDeferredVideo(get_req)
                match r.status:
                    case deferred_pb2.DeferredStatus.DONE:
                        if not r.HasField("response"):
                            raise RuntimeError("Deferred request completed but no response was returned.")
                        response = VideoResponse(r.response)
                        span.set_attributes(_make_extend_span_response_attributes(request_pb, response))
                        return response
                    case deferred_pb2.DeferredStatus.EXPIRED:
                        raise RuntimeError("Deferred request expired.")
                    case deferred_pb2.DeferredStatus.PENDING:
                        await asyncio.sleep(timer.sleep_interval_or_raise())
                        continue
                    case deferred_pb2.DeferredStatus.FAILED:
                        if r.HasField("response") and r.response.HasField("error"):
                            error = r.response.error
                            raise VideoGenerationError(error.code, error.message)
                        raise VideoGenerationError("UNKNOWN", "Video extension failed with no error details.")
                    case unknown_status:
                        warnings.warn(
                            f"Encountered unknown status: {unknown_status} whilst waiting for video extension.",
                            stacklevel=2,
                        )
                        await asyncio.sleep(timer.sleep_interval_or_raise())
