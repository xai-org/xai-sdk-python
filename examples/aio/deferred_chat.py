import asyncio
from datetime import timedelta
from typing import Sequence

from absl import app, flags

from xai_sdk import AsyncClient
from xai_sdk.chat import user

TIMEOUT = flags.DEFINE_integer("timeout", 5, "Timeout for the deferred chat request.")
INTERVAL = flags.DEFINE_integer("interval", 2000, "Interval for the deferred chat request.")


# see https://docs.x.ai/docs/guides/deferred-chat-completions#deferred-chat-completions


async def deferred_chat(client: AsyncClient):
    """Sample a response from a model using polling."""

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello"))
    try:
        response = await chat.defer(
            timeout=timedelta(minutes=TIMEOUT.value), interval=timedelta(milliseconds=INTERVAL.value)
        )
        print(response.content)
    except RuntimeError as e:
        # request expired
        print(e)
    except ValueError as e:
        # unknown deferred status
        print(e)


async def batch_deferred_chat(client: AsyncClient):
    """Sample multiple responses from a model using polling."""
    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello"))
    try:
        responses = await chat.defer_batch(
            n=10, timeout=timedelta(minutes=TIMEOUT.value), interval=timedelta(milliseconds=INTERVAL.value)
        )
        for response in responses:
            print(response.content)
    except RuntimeError as e:
        # request expired
        print(e)
    except ValueError as e:
        # unknown deferred status
        print(e)


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = AsyncClient()
    await deferred_chat(client)


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
