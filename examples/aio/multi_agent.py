import asyncio
from typing import Sequence

from absl import app, flags

import xai_sdk
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

THINKING = flags.DEFINE_bool("thinking", True, "Whether the model display the reasoning tokens consumed or not")


async def basic_response(chat: xai_sdk.aio.chat.Chat):
    """Sample and print a complete multi-agent response."""
    # Sample a response from a multi-agent model.
    response = await chat.sample()

    print(f"Grok: {response.content}")

    # `cost_usd` is per-request; it shows us  the response costs in us dollars.
    if response.cost_usd is not None:
        print(f"Cost: ${response.cost_usd:.4f}")


async def response_with_thinking(chat: xai_sdk.aio.chat.Chat):
    """Stream a Multi-agent response with reasoning progress."""

    print("Grok: ", end="", flush=True)

    content_started = False
    last_response = None

    async for response, chunk in chat.stream():
        last_response = response

        if response.usage.reasoning_tokens and not content_started:
            print(f"\rThinking...({response.usage.reasoning_tokens} tokens)", end="", flush=True)

        if chunk.content:
            if not content_started:
                print("\rGrok: ", end="", flush=True)
                content_started = True

            print(chunk.content, end="", flush=True)

    print()

    if last_response is None:
        raise RuntimeError("The model returned no response.")

    # `cost_usd` is per-request; it shows us  the response costs in us dollars.
    if last_response.cost_usd is not None:
        print(f"Cost: ${last_response.cost_usd:.4f}")


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.AsyncClient()

    chat = client.chat.create(
        model="grok-4.20-multi-agent",
        # you can choose 4 or 16 agent
        agent_count=4,
        # you can use tools such as web search, x search, or/and code execution
        tools=[web_search(), x_search()],
        include=["verbose_streaming"],
    )

    chat.append(user("Research the latest breakthroughs in quantum computing and summarize the key findings."))

    if THINKING.value:
        await response_with_thinking(chat)
    else:
        await basic_response(chat)


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
