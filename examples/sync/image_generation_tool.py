import base64
import json
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.proto import chat_pb2
from xai_sdk.tools import image_generation


def main() -> None:
    client = Client(api_key=os.getenv("XAI_API_KEY"))

    chat = client.chat.create(
        model="grok-4.5",
        # Optionally restrict the tool with image_generation(action="generate")
        # (text-to-image only) or image_generation(action="edit") (editing only).
        tools=[image_generation()],
    )

    chat.append(user("Generate an image of a corgi surfing a big wave, in the style of a Japanese woodblock print"))
    response = chat.sample()

    print(response.content)

    # Image generation calls produce ROLE_TOOL outputs. Select them by the
    # tool-call type enum, then read the data URL out of the result envelope.
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
        filename = f"corgi_surfing_{i}.{mime_type.removeprefix('image/')}"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Saved {filename} ({len(image_bytes)} bytes)")

    print(response.server_side_tool_usage)


if __name__ == "__main__":
    main()
