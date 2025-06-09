import asyncio
import base64
from typing import Sequence

import aiohttp
from absl import app, flags

from xai_sdk import AsyncClient
from xai_sdk.chat import image, user

FORMAT = flags.DEFINE_enum("format", "url", ["url", "base64"], "Image format used when providing the image.")


async def image_understanding(client: AsyncClient) -> None:
    """Image understanding with multiple images."""
    chat = client.chat.create(model="grok-2-vision")

    # We can easily interleave text and images in a single user conversation turn.
    chat.append(
        user(
            "What do these images have in common?",
            image(
                "https://www.nasa.gov/wp-content/uploads/2025/04/51d-9092large.jpg",
                detail="high",
            ),
            image(
                "https://www.nasa.gov/wp-content/uploads/2025/04/0101247orig-1.jpg",
                detail="high",
            ),
        )
    )

    response = await chat.sample()

    print(response.content)
    print(response.usage.prompt_image_tokens)


async def image_understanding_b64(client: AsyncClient) -> None:
    """Image understanding with an image encoded as base64."""
    chat = client.chat.create(model="grok-2-vision")

    image_url = "https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            image_data = await response.content.read()
            image_data = base64.b64encode(image_data).decode("utf-8")

    chat.append(
        user(
            "What kind of ant is this?",
            image(f"data:image/jpeg;base64,{image_data}"),
        )
    )

    response = await chat.sample()
    print(response.content)
    print(response.usage.prompt_image_tokens)


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = AsyncClient()

    match FORMAT.value:
        case "base64":
            await image_understanding_b64(client)
        case "url":
            await image_understanding(client)


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
