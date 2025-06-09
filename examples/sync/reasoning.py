from typing import Sequence

from absl import app, flags

from xai_sdk import Client
from xai_sdk.chat import ReasoningEffort, user

STREAM = flags.DEFINE_bool("stream", False, "Whether streaming is enabled.")
REASONING_EFFORT = flags.DEFINE_enum("effort", "low", ["low", "high"], "The effort of the reasoning model.")


def reasoning(client: Client, reasoning_effort: ReasoningEffort) -> None:
    """Sample from a reasoning model."""
    chat = client.chat.create(
        model="grok-3-mini",  # This model is a reasoning model.
        reasoning_effort=reasoning_effort,
    )

    prompt = input("Enter a prompt: ")
    chat.append(user(prompt))

    response = chat.sample()
    print(f"Reasoning Content: {response.reasoning_content}")
    print(f"Final Answer: {response.content}")

    print("\n\n--------- Usage ---------")
    print(f"Reasoning Tokens: {response.usage.reasoning_tokens}")
    print(f"Completion Tokens: {response.usage.completion_tokens}")
    print(f"Total Tokens: {response.usage.total_tokens}")


def reasoning_with_streaming(client: Client, reasoning_effort: ReasoningEffort) -> None:
    """Sample from a reasoning model and stream the response."""
    chat = client.chat.create(
        model="grok-3-mini",  # This model is a reasoning model.
        reasoning_effort=reasoning_effort,
    )

    prompt = input("Enter a prompt: ")
    chat.append(user(prompt))

    print("\n\n--------- Reasoning ---------", flush=True)
    first_content = True

    latest_response = None
    for response, chunk in chat.stream():
        if chunk.reasoning_content:
            print(chunk.reasoning_content, end="", flush=True)
        if chunk.content:
            if first_content:
                print("\n\n--------- Final Response ---------", flush=True)
                first_content = False
            print(chunk.content, end="", flush=True)

        latest_response = response

    assert latest_response is not None
    print("\n\n--------- Usage ---------")
    print(f"Reasoning Tokens: {latest_response.usage.reasoning_tokens}")
    print(f"Completion Tokens: {latest_response.usage.completion_tokens}")
    print(f"Total Tokens: {latest_response.usage.total_tokens}")


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = Client()
    match (STREAM.value, REASONING_EFFORT.value):
        case (True, "low"):
            reasoning_with_streaming(client, "low")
        case (True, "high"):
            reasoning_with_streaming(client, "high")
        case (False, "low"):
            reasoning(client, "low")
        case (False, "high"):
            reasoning(client, "high")


if __name__ == "__main__":
    app.run(main)
