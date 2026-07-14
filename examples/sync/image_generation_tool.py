"""Examples for the server-side `image_generation` tool.

Unlike the standalone image API (see `image_generation.py`), the `image_generation`
tool runs inside an agentic chat request: the model decides when to generate or
edit images as part of answering the conversation.

The generated image rides on the response as a `ROLE_TOOL` output message whose
content is a JSON envelope of the form:

    {"__type": "image_generation_result", "result": "data:<mime>;base64,..."}
"""

import base64
import json
import pathlib

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.proto import chat_pb2
from xai_sdk.tools import get_tool_call_type, image_generation


def save_generated_images(response, output_dir: pathlib.Path) -> list[pathlib.Path]:
    """Decodes and saves every image the image_generation tool produced."""
    saved_paths = []
    tool_outputs = [
        output
        for output in response.proto.outputs
        if output.message.role == chat_pb2.MessageRole.ROLE_TOOL
        and any(get_tool_call_type(tool_call) == "image_generation_tool" for tool_call in output.message.tool_calls)
    ]
    for i, output in enumerate(tool_outputs):
        envelope = json.loads(output.message.content)
        if envelope.get("__type") != "image_generation_result":
            continue
        # The result is a data URL, e.g. "data:image/jpeg;base64,<payload>".
        data_url = envelope["result"]
        header, payload = data_url.split(",", 1)
        mime_type = header.removeprefix("data:").removesuffix(";base64")
        extension = mime_type.removeprefix("image/")
        path = output_dir / f"generated_image_{i}.{extension}"
        path.write_bytes(base64.b64decode(payload))
        saved_paths.append(path)
    return saved_paths


def generate_image(client: Client, model: str) -> None:
    """Asks the model to generate an image and saves the result to disk."""
    chat = client.chat.create(
        model=model,
        # action="auto" (the default) allows both generation and editing.
        # Use action="generate" for text-to-image only, or action="edit" for editing only.
        tools=[image_generation()],
    )
    chat.append(user("Generate an image of a red panda drinking boba tea."))

    response = chat.sample()

    for tool_call in response.tool_calls:
        if get_tool_call_type(tool_call) == "image_generation_tool":
            print(f"Tool call: {tool_call.function.name} with arguments: {tool_call.function.arguments}")

    print(f"Response: {response.content}")

    saved_paths = save_generated_images(response, pathlib.Path.cwd())
    for path in saved_paths:
        print(f"Saved generated image to: {path}")

    print(f"Server-side tool usage: {response.server_side_tool_usage}")
    print(f"Image generations: {response.usage.num_image_generations}")
    if response.cost_usd is not None:
        print(f"Cost: ${response.cost_usd:.4f}")


def generate_then_edit(client: Client, model: str) -> None:
    """Generates an image on turn 1, then edits it on turn 2 via `previous_response_id`."""
    chat = client.chat.create(
        model=model,
        tools=[image_generation(action="generate")],
        store_messages=True,
    )
    chat.append(user("Generate an image of a lighthouse on a cliff."))
    response = chat.sample()
    print(f"Turn 1: {response.content}")

    # The follow-up chat replays the stored conversation, including the generated
    # image, so the model can edit it.
    follow_up_chat = client.chat.create(
        model=model,
        tools=[image_generation()],
        store_messages=True,
        previous_response_id=response.id,
    )
    follow_up_chat.append(user("Edit the image you just generated: make it nighttime with a full moon."))
    follow_up_response = follow_up_chat.sample()

    for tool_call in follow_up_response.tool_calls:
        if get_tool_call_type(tool_call) == "image_generation_tool":
            # Generation calls are named `imagine_text_to_image`, edits `imagine_image_to_image`.
            print(f"Tool call: {tool_call.function.name}")

    print(f"Turn 2: {follow_up_response.content}")
    print(f"Image edits: {follow_up_response.usage.num_image_edits}")

    saved_paths = save_generated_images(follow_up_response, pathlib.Path.cwd())
    for path in saved_paths:
        print(f"Saved edited image to: {path}")


def main() -> None:
    client = Client()

    generate_image(client, model="grok-4.20")
    # generate_then_edit(client, model="grok-4.20")


if __name__ == "__main__":
    main()
