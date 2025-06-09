import itertools
from typing import Sequence

from absl import app, flags

import xai_sdk
from xai_sdk.image import ImageFormat
from xai_sdk.sync.image import ImageResponse

N = flags.DEFINE_integer("n", 1, "Number of images to generate.")
FORMAT = flags.DEFINE_enum("format", "base64", ["base64", "url"], "Image format used to return the result.")
OUTPUT_DIR = flags.DEFINE_string("output-dir", None, "Directory to save the generated images.", required=True)


def generate_single(client: xai_sdk.Client, image_format: ImageFormat):
    """Generate a single image from a prompt."""
    for turn in itertools.count():
        prompt = input("Prompt: ")
        result = client.image.sample(prompt, model="grok-2-image", image_format=image_format)
        save_images(turn, [result])


def generate_batch(client: xai_sdk.Client, image_format: ImageFormat):
    """Generate a batch of images from a prompt."""
    for turn in itertools.count():
        prompt = input("Prompt: ")
        results = client.image.sample_batch(prompt, n=N.value, model="grok-2-image", image_format=image_format)
        save_images(turn, results)


def save_images(turn: int, responses: Sequence[ImageResponse]):
    """Save images to a file."""
    for i, image in enumerate(responses):
        print(image.prompt)
        with open(f"{OUTPUT_DIR.value}/image_{turn}_{i}.jpg", "wb") as f:
            f.write(image.image)


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.Client()

    match (N.value, FORMAT.value):
        case (1, "base64"):
            generate_single(client, "base64")
        case (1, "url"):
            generate_single(client, "url")
        case (_, "base64"):
            generate_batch(client, "base64")
        case (_, "url"):
            generate_batch(client, "url")


if __name__ == "__main__":
    app.run(main)
