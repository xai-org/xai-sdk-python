import asyncio
import itertools
from typing import Sequence

from absl import app, flags

import xai_sdk
from xai_sdk.aio.image import ImageResponse
from xai_sdk.image import ImageFormat

N = flags.DEFINE_integer("n", 1, "Number of images to generate.")
FORMAT = flags.DEFINE_enum("format", "base64", ["base64", "url"], "Image format used to return the result.")
OUTPUT_DIR = flags.DEFINE_string("output-dir", None, "Directory to save the generated images.", required=True)


async def generate_single(client: xai_sdk.AsyncClient, image_format: ImageFormat):
    """Generate a single image from a prompt."""
    for turn in itertools.count():
        prompt = input("Prompt: ")
        result = await client.image.sample(prompt, model="grok-2-image", image_format=image_format)
        await _save_images(turn, [result])


async def generate_batch(client: xai_sdk.AsyncClient, image_format: ImageFormat):
    """Generate a batch of images from a prompt."""
    for turn in itertools.count():
        prompt = input("Prompt: ")
        results = await client.image.sample_batch(prompt, n=N.value, model="grok-2-image", image_format=image_format)
        await _save_images(turn, results)


async def _save_images(turn: int, responses: Sequence[ImageResponse]):
    """Save images to a file."""
    for i, image in enumerate(responses):
        print(image.prompt)
        with open(f"{OUTPUT_DIR.value}/image_{turn}_{i}.jpg", "wb") as f:
            f.write(await image.image)


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.AsyncClient()

    match (N.value, FORMAT.value):
        case (1, "base64"):
            await generate_single(client, "base64")
        case (_, "base64"):
            await generate_batch(client, "base64")
        case (1, "url"):
            await generate_single(client, "url")
        case (_, "url"):
            await generate_batch(client, "url")


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
