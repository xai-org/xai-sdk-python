"""Multi-reference image editing example.

Example:
  uv run examples/aio/image_multi_reference_editing.py \
    --prompt "Blend these references into a cyberpunk skyline" \
    --image-url "https://example.com/one.jpg" \
    --image-url "https://example.com/two.jpg" \
    --format url
"""

import asyncio
from typing import Sequence, cast

from absl import app, flags

import xai_sdk
from xai_sdk.aio.image import ImageResponse
from xai_sdk.image import ImageFormat

N = flags.DEFINE_integer("n", 1, "Number of images to generate.")
FORMAT = flags.DEFINE_enum("format", "base64", ["base64", "url"], "Image format used to return the result.")
MODEL = flags.DEFINE_string("model", "grok-imagine-image", "Image generation model to use.")
OUTPUT_DIR = flags.DEFINE_string("output-dir", None, "Directory to save the generated images.")
PROMPT = flags.DEFINE_string("prompt", None, "Prompt to edit the input images.", required=True)
IMAGE_URLS = flags.DEFINE_multi_string(
    "image-url",
    [],
    "Input image URL or base64-encoded string. Repeat for multiple images.",
)


async def edit_images(client: xai_sdk.AsyncClient, image_format: ImageFormat) -> Sequence[ImageResponse]:
    """Multi-reference image editing using image URLs or base64 strings."""
    image_urls = list(IMAGE_URLS.value)
    if not image_urls:
        raise app.UsageError("At least one --image-url is required.")

    if N.value == 1:
        response = await client.image.sample(
            PROMPT.value,
            model=MODEL.value,
            image_format=image_format,
            image_urls=image_urls,
        )
        return [response]

    return await client.image.sample_batch(
        PROMPT.value,
        n=N.value,
        model=MODEL.value,
        image_format=image_format,
        image_urls=image_urls,
    )


async def save_images(responses: Sequence[ImageResponse]) -> None:
    """Save images to a file."""
    for i, image in enumerate(responses):
        with open(f"{OUTPUT_DIR.value}/image_{i}.jpg", "wb") as f:
            f.write(await image.image)


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    if FORMAT.value != "url" and not OUTPUT_DIR.value:
        raise app.UsageError("--output-dir is required when --format is not url.")

    client = xai_sdk.AsyncClient()
    image_format: ImageFormat = cast(ImageFormat, FORMAT.value)
    responses = await edit_images(client, image_format)

    if image_format == "url":
        for i, image in enumerate(responses):
            print(f"Image {i} URL: {image.url}")
        return

    await save_images(responses)


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
