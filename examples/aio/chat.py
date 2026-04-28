import asyncio
from typing import Sequence

from absl import app, flags

import xai_sdk
from xai_sdk.chat import assistant, system, user

STREAM = flags.DEFINE_bool("stream", False, "Whether streaming is enabled.")
N = flags.DEFINE_integer("n", 1, "Number of answers to generate.")


async def basic_chat(chat: xai_sdk.aio.chat.Chat):
    """Multi-turn chat between a user and an assistant."""
    total_cost_usd = 0.0
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        # Append a user turn to the conversation history.
        chat.append(user(prompt))
        # Sample a response from the assistant.
        response = await chat.sample()
        print(f"Grok: {response.content}")
        # Append the assistant's response to the conversation history.
        chat.append(response)
        # `cost_usd` is per-request; accumulate to track total spend across turns.
        # `or 0.0` skips turns where the server did not report a cost.
        total_cost_usd += response.cost_usd or 0.0

    print(f"Total cost: ${total_cost_usd:.4f}")


async def chat_with_streaming(chat: xai_sdk.aio.chat.Chat):
    """Multi-turn chat between a user and an assistant with streaming."""
    total_cost_usd = 0.0
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        # Append a user turn to the conversation history.
        chat.append(user(prompt))

        print("Grok: ", end="", flush=True)

        # Stream a response from the assistant.
        stream = chat.stream()
        last_response = None
        async for response, chunk in stream:
            print(chunk.content, end="", flush=True)
            last_response = response
        print()
        assert last_response is not None
        chat.append(last_response)
        # Final chunk's `cost_usd` is the per-request total. Accumulate across turns.
        # `or 0.0` skips turns where the server did not report a cost.
        total_cost_usd += last_response.cost_usd or 0.0

    print(f"Total cost: ${total_cost_usd:.4f}")


async def batch_chat(chat: xai_sdk.aio.chat.Chat):
    """Multi-turn chat between a user and an assistant with batch sampling."""
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        # Append a user turn to the conversation history.
        chat.append(user(prompt))

        # Sample multiple responses concurrently from the assistant.
        responses = await chat.sample_batch(N.value)
        for index, response in enumerate(responses):
            print(f"Grok (response {index + 1}): {response.content}")

        # Only add the first response to the history.
        chat.append(responses[0])


async def batch_chat_with_streaming(chat: xai_sdk.aio.chat.Chat):
    """Multi-turn chat between a user and an assistant with batch sampling and streaming."""
    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        # Append a user turn to the conversation history.
        chat.append(user(prompt))

        batch_stream = chat.stream_batch(N.value)
        responses = None
        async for responses, _ in batch_stream:
            for index, response in enumerate(responses):
                print(f"Grok (response {index + 1}): {response.content}")

        # Only add the first response.
        assert responses is not None
        chat.append(responses[0])


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.AsyncClient()

    chat = client.chat.create(
        model="grok-4.20-non-reasoning",
        messages=[
            system("You talk like a pirate."),
            user("How are you?"),
            assistant("Actually not so well..."),
        ],
    )

    match (N.value, STREAM.value):
        case (1, False):
            await basic_chat(chat)
        case (_, False):
            await batch_chat(chat)
        case (1, True):
            await chat_with_streaming(chat)
        case (_, True):
            await batch_chat_with_streaming(chat)


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
