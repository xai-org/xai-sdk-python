from datetime import timedelta
from typing import Sequence

from absl import app, flags

from xai_sdk import Client
from xai_sdk.chat import user

TIMEOUT = flags.DEFINE_integer("timeout", 5, "Timeout in minutes for the deferred chat request.")
INTERVAL = flags.DEFINE_integer("interval", 100, "Interval in milliseconds for the deferred chat request.")
N = flags.DEFINE_integer("n", 1, "Number of responses to generate.")


# see https://docs.x.ai/docs/guides/deferred-chat-completions#deferred-chat-completions


def deferred_chat(client: Client):
    """Sample a response from a model using polling."""

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello"))
    try:
        response = chat.defer(timeout=timedelta(minutes=TIMEOUT.value), interval=timedelta(milliseconds=INTERVAL.value))
        print(response.content)
    except RuntimeError as e:
        # request expired
        print(e)
    except ValueError as e:
        # unknown deferred status
        print(e)


def batch_deferred_chat(client: Client):
    """Sample multiple responses from a model using polling."""
    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello"))
    try:
        responses = chat.defer_batch(
            n=N.value, timeout=timedelta(minutes=TIMEOUT.value), interval=timedelta(milliseconds=INTERVAL.value)
        )
        for response in responses:
            print(response.content)
    except RuntimeError as e:
        # request expired
        print(e)
    except ValueError as e:
        # unknown deferred status
        print(e)


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = Client()
    if N.value > 1:
        batch_deferred_chat(client)
    else:
        deferred_chat(client)


if __name__ == "__main__":
    app.run(main)
