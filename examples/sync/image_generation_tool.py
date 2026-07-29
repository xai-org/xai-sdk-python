import base64
import json
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.proto import chat_pb2
from xai_sdk.tools import image_generation


def save_images(response, prefix: str) -> None:
    """Saves every image produced by image_generation tool calls in a response.

    Image generation calls produce ROLE_TOOL outputs. Select them by the
    tool-call type enum, then read the data URL out of the result envelope.
    """
    image_outputs = [
        output
        for output in response.tool_outputs
        if any(
            tool_call.type == chat_pb2.TOOL_CALL_TYPE_IMAGE_GENERATION_TOOL for tool_call in output.message.tool_calls
        )
    ]
    for i, output in enumerate(image_outputs):
        envelope = json.loads(output.message.content)
        data_url = envelope["result"]  # data:image/jpeg;base64,...
        mime_type, payload = data_url.removeprefix("data:").split(";base64,", 1)
        image_bytes = base64.b64decode(payload)
        filename = f"{prefix}_{i}.{mime_type.removeprefix('image/')}"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Saved {filename} ({len(image_bytes)} bytes)")


def generate_image(client: Client) -> None:
    """Generates an image in a single turn."""
    chat = client.chat.create(
        model="grok-4.5",
        # Optionally restrict the tool with image_generation(action="generate")
        # (text-to-image only) or image_generation(action="edit") (editing only).
        tools=[image_generation()],
    )

    chat.append(user("Generate an image of a corgi surfing a big wave, in the style of a Japanese woodblock print"))
    response = chat.sample()

    print(response.content)
    save_images(response, "corgi_surfing")
    print(response.server_side_tool_usage)


def generate_then_edit_image(client: Client) -> None:
    """Generates an image, then edits it in a follow-up turn.

    Storing the first turn (`store_messages=True`) and chaining the second one
    via `previous_response_id` replays the full agentic state on the server,
    so the model can edit the image it generated on the previous turn.
    """
    chat = client.chat.create(
        model="grok-4.5",
        tools=[image_generation(action="generate")],
        store_messages=True,
    )
    chat.append(user("Generate an image of a corgi surfing a big wave, in the style of a Japanese woodblock print"))
    response = chat.sample()

    print(response.content)
    save_images(response, "corgi_surfing")

    follow_up_chat = client.chat.create(
        model="grok-4.5",
        tools=[image_generation()],
        store_messages=True,
        previous_response_id=response.id,
    )
    follow_up_chat.append(user("Edit the image you just generated: make it night time, lit by a full moon"))
    follow_up_response = follow_up_chat.sample()

    print(follow_up_response.content)
    save_images(follow_up_response, "corgi_surfing_night")
    print(follow_up_response.server_side_tool_usage)


def main() -> None:
    client = Client(api_key=os.getenv("XAI_API_KEY"))

    generate_image(client)

    # Multi-turn: generate an image, then edit it in a follow-up turn.
    generate_then_edit_image(client)


if __name__ == "__main__":
    main()
