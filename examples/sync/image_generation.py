import itertools
from typing import Sequence, cast

from absl import app, flags

import xai_sdk
from xai_sdk.image import ImageFormat
from xai_sdk.sync.image import ImageResponse

N = flags.DEFINE_integer("n", 1, "Number of images to generate.")
FORMAT = flags.DEFINE_enum("format", "base64", ["base64", "url"], "Image format used to return the result.")
MODEL = flags.DEFINE_string("model", "grok-imagine-image", "Image generation model to use.")
OUTPUT_DIR = flags.DEFINE_string("output-dir", None, "Directory to save the generated images.", required=True)


def generate_multi_turn(client: xai_sdk.Client, image_format: ImageFormat):
    """Multi-turn image generation that builds on the previous output image.

    Turn 0 generates an initial image from your prompt. Each subsequent turn reuses the previous
    image output as an input image (image-to-image) while you provide a new prompt to refine it.
    """
    previous_image: str | None = None

    for turn in itertools.count():
        if previous_image is None:
            prompt = input("Prompt (blank to stop): ")
        else:
            prompt = input("Edit prompt (blank to stop): ")
        if not prompt:
            return

        if N.value == 1:
            response = client.image.sample(
                prompt,
                model=MODEL.value,
                image_format=image_format,
                image_url=previous_image,
            )
            responses = [response]
        else:
            responses = client.image.sample_batch(
                prompt,
                n=N.value,
                model=MODEL.value,
                image_format=image_format,
                image_url=previous_image,
            )

        save_images(turn, responses)

        selected = 0
        if len(responses) > 1:
            raw = input(f"Continue from which image? [0-{len(responses) - 1}] (default 0): ").strip()
            if raw:
                selected = int(raw)
                if selected < 0 or selected >= len(responses):
                    raise ValueError(f"Invalid image index {selected}.")

        chosen = responses[selected]
        previous_image = chosen.url if image_format == "url" else chosen.base64

        if len(responses) > 1:
            if image_format == "url":
                print(f"Continuing from image {selected}: {chosen.url}")
            else:
                print(f"Continuing from image {selected} (base64).")


def save_images(turn: int, responses: Sequence[ImageResponse]):
    """Save images to a file."""
    for i, image in enumerate(responses):
        with open(f"{OUTPUT_DIR.value}/image_{turn}_{i}.jpg", "wb") as f:
            f.write(image.image)


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.Client()
    image_format: ImageFormat = cast(ImageFormat, FORMAT.value)
    generate_multi_turn(client, image_format)


if __name__ == "__main__":
    app.run(main)
