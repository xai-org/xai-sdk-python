"""Examples for the server-side `image_generation` tool.

Unlike the standalone Image API (`client.image`, see `image_generation.py`), the
`image_generation` tool lets the model generate and edit images mid-conversation
as part of a single agentic chat request. Generated images are exposed on the
response via `response.image_outputs`.
"""

import os

from xai_sdk import Client
from xai_sdk.chat import Response, image, user
from xai_sdk.tools import get_tool_call_type, image_generation, web_search


def generate_image(client: Client) -> None:
    """Generates an image in a single turn."""
    chat = client.chat.create(
        model="grok-4.5",
        tools=[image_generation()],
    )
    chat.append(user("Generate an image of a corgi surfing a big wave, in the style of a Japanese woodblock print"))
    response = chat.sample()
    print(response.content)
    _save_images(response, "corgi_surfing")
    print(response.server_side_tool_usage)


def edit_input_image(client: Client) -> None:
    """Edits an image attached to the chat context.

    With `action="edit"` (or the default `"auto"`), the model can edit any image
    already in the conversation — images attached as input via the `image()`
    content helper as well as images it generated earlier.
    """
    chat = client.chat.create(
        model="grok-4.5",
        tools=[image_generation(action="edit")],
    )
    chat.append(
        user(
            "Edit this image so it looks like a watercolor painting.",
            image("https://docs.x.ai/assets/api-examples/images/style-realistic.png"),
        )
    )
    response = chat.sample()
    print(response.content)
    _save_images(response, "watercolor")


def generate_then_edit_image(client: Client) -> None:
    """Generates an image, then edits it in a follow-up turn of the same chat."""
    chat = client.chat.create(
        model="grok-4.5",
        # Auto mode: exposes both imagine_text_to_image AND imagine_image_to_image.
        # (action="generate" would hide the edit tool from every turn of this chat.)
        tools=[image_generation()],
    )

    # -- Turn 1: generate ----------------------------------------------------
    chat.append(user("Generate an image of a corgi surfing a big wave, in the style of a Japanese woodblock print"))
    response = chat.sample()
    print(response.content)
    _save_images(response, "corgi_surfing")

    chat.append(response)

    # -- Turn 2: edit --------------------------------------------------------
    chat.append(user("Edit the image you just generated: make it night time, lit by a full moon"))
    response = chat.sample()
    print(response.content)
    _save_images(response, "corgi_surfing_night")


def search_and_generate_image(client: Client) -> None:
    """Combines web search with image generation in a single agentic request.

    The model first looks up live data with the web_search tool, then renders
    what it found into a generated image.
    """
    chat = client.chat.create(
        model="grok-4.5",
        tools=[web_search(), image_generation()],
    )
    chat.append(
        user(
            "Generate an infographic image based on next week's temperature forecast in the UK, "
            "with key city icons along with their forecast in the image"
        )
    )
    response = chat.sample()
    print(response.content)
    _save_images(response, "uk_forecast_infographic")
    print(response.server_side_tool_usage)


def stream_image_generation(client: Client) -> None:
    """Streams a response that generates an image.

    With `include=["verbose_streaming"]`, tool-call activity and text deltas
    arrive on the streamed chunks as they happen. The image payload itself
    streams as a (large) tool output; the decoded bytes are exposed on the
    accumulated response via `response.image_outputs` once the stream ends.
    """
    chat = client.chat.create(
        model="grok-4.5",
        tools=[image_generation()],
        include=["verbose_streaming"],
    )
    chat.append(user("Generate an image of an origami fox in a paper forest"))

    last_response: Response | None = None
    for response, chunk in chat.stream():
        last_response = response
        for tool_call in chunk.tool_calls:
            if get_tool_call_type(tool_call) == "image_generation_tool":
                print(f"\nGenerating image: {tool_call.function.arguments}")
        for tool_output in chunk.tool_outputs:
            # The raw payload is a base64 data URL envelope; don't print it.
            print(f"\nReceived image payload chunk ({len(tool_output.content)} chars)")
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print()
    if last_response is not None:
        _save_images(last_response, "origami_fox")


def _save_images(response: Response, prefix: str) -> None:
    """Saves every image produced by image_generation tool calls in a response."""
    if not response.image_outputs:
        print("No images were generated.")
        return
    for i, output in enumerate(response.image_outputs):
        extension = output.mime_type.removeprefix("image/")
        filename = f"{prefix}_{i}.{extension}"
        with open(filename, "wb") as f:
            f.write(output.image)
        print(f"Saved {filename} ({output.tool_call.function.name}, image_uuid={output.image_uuid})")


def main() -> None:
    client = Client(api_key=os.getenv("XAI_API_KEY"))

    generate_image(client)

    # Edit an image attached to the chat context.
    # edit_input_image(client)

    # Multi-turn: generate an image, then edit it in a follow-up turn.
    # generate_then_edit_image(client)

    # Combine web search with image generation.
    # search_and_generate_image(client)

    # Stream tool activity and text deltas while the image is generated.
    # stream_image_generation(client)


if __name__ == "__main__":
    main()
