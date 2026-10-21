"""Command-Line Interface (CLI) for the xAI SDK."""

import argparse
import base64
import mimetypes
import os
import sys
from typing import Optional, Sequence

import grpc

from .__about__ import __version__
from .chat import image, system, user
from .sync.client import Client


def _read_stdin() -> Optional[str]:
    """Reads stdin if data is piped into the process."""
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            return data.strip() if data else None
    except (OSError, ValueError):
        return None
    return None


def _load_image(image_arg: str):
    """Loads an image from a URL or a local file path."""
    if image_arg.startswith(("http://", "https://", "data:")):
        return image(image_arg)

    if not os.path.exists(image_arg):
        raise FileNotFoundError(f"Image file not found: {image_arg}")

    mime_type, _ = mimetypes.guess_type(image_arg)
    mime_type = mime_type or "image/jpeg"
    with open(image_arg, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return image(f"data:{mime_type};base64,{encoded}")


def _build_messages(args: argparse.Namespace, prompt: str) -> list:
    """Constructs the initial chat message list from CLI arguments."""
    messages = []
    if args.system:
        messages.append(system(args.system))

    if args.image:
        img = _load_image(args.image)
        messages.append(user(prompt, img))
    else:
        messages.append(user(prompt))
    return messages


def _single_turn_chat(args: argparse.Namespace, client: Client, prompt: str) -> int:
    """Executes a single-turn prompt chat."""
    try:
        messages = _build_messages(args, prompt)
    except Exception as e:
        print(f"Error preparing message: {e}", file=sys.stderr)
        return 1

    chat = client.chat.create(
        model=args.model,
        messages=messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    if args.stream:
        try:
            for _, chunk in chat.stream():
                if chunk.content:
                    print(chunk.content, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError during streaming: {e}", file=sys.stderr)
            return 1
    else:
        try:
            response = chat.sample()
            print(response.content)
        except Exception as e:
            print(f"Error during completion: {e}", file=sys.stderr)
            return 1
    return 0


def _execute_interactive_turn(chat, turn_prompt: str, *, stream: bool) -> None:
    """Executes a single turn in an interactive chat session."""
    chat.append(user(turn_prompt))
    print("Grok: ", end="", flush=True)

    if stream:
        last_response = None
        for response, chunk in chat.stream():
            if chunk.content:
                print(chunk.content, end="", flush=True)
            last_response = response
        print()
        if last_response is not None:
            chat.append(last_response)
    else:
        response = chat.sample()
        print(response.content)
        chat.append(response)


def _interactive_chat(args: argparse.Namespace, client: Client, initial_prompt: Optional[str] = None) -> int:
    """Runs a multi-turn interactive chat loop in the terminal."""
    print(f"xAI Interactive Chat (model: {args.model})")
    print("Type 'exit', 'quit', or press Ctrl+C to exit.\n")

    initial_messages = [system(args.system)] if args.system else None
    chat = client.chat.create(
        model=args.model,
        messages=initial_messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    turn_prompt = initial_prompt
    while True:
        try:
            if turn_prompt is None:
                turn_prompt = input("You: ").strip()
                if not turn_prompt:
                    continue

            if turn_prompt.lower() in ("exit", "quit", ":q"):
                print("Bye!")
                break

            _execute_interactive_turn(chat, turn_prompt, stream=args.stream)
            turn_prompt = None

        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            turn_prompt = None

    return 0


def _handle_chat(args: argparse.Namespace, client: Client) -> int:
    """Handles single prompt or interactive chat."""
    piped_input = _read_stdin() if not args.interactive else None
    prompt = args.prompt

    if piped_input:
        prompt = f"{prompt}\n\n{piped_input}" if prompt else piped_input

    if args.interactive:
        return _interactive_chat(args, client, initial_prompt=prompt)

    if not prompt:
        print("Error: No prompt provided. Use -i/--interactive for chat mode or provide a prompt.", file=sys.stderr)
        return 1

    return _single_turn_chat(args, client, prompt)


def _list_models(args: argparse.Namespace, client: Client) -> int:
    """Lists available models by category."""
    model_type = args.type or "language"
    if model_type in ("language", "all"):
        print("=== Language Models ===")
        for m in client.models.list_language_models():
            print(f"- {m.name} (version: {m.version or 'n/a'})")
    if model_type in ("image", "all"):
        print("\n=== Image Generation Models ===")
        for m in client.models.list_image_generation_models():
            print(f"- {m.name} (version: {m.version or 'n/a'})")
    if model_type in ("embedding", "all"):
        print("\n=== Embedding Models ===")
        for m in client.models.list_embedding_models():
            print(f"- {m.name} (system fingerprint: {m.system_fingerprint or 'n/a'})")
    return 0


def _get_model(args: argparse.Namespace, client: Client) -> int:
    """Fetches and displays metadata for a specific model."""
    if not args.name:
        print("Error: Model name is required.", file=sys.stderr)
        return 1

    model_type = args.type or "language"
    try:
        if model_type == "language":
            m = client.models.get_language_model(args.name)
        elif model_type == "image":
            m = client.models.get_image_generation_model(args.name)
        elif model_type == "embedding":
            m = client.models.get_embedding_model(args.name)
        else:
            print(f"Error: Unknown model type: {model_type}", file=sys.stderr)
            return 1

        print(f"Name: {m.name}")
        print(f"Aliases: {list(m.aliases)}")
        print(f"Version: {getattr(m, 'version', 'n/a')}")
        print(f"Input modalities: {list(m.input_modalities)}")
        print(f"Output modalities: {list(m.output_modalities)}")
        if hasattr(m, "max_prompt_length"):
            print(f"Max prompt length: {m.max_prompt_length}")
        return 0
    except Exception as e:
        print(f"Error retrieving model: {e}", file=sys.stderr)
        return 1


def _handle_models(args: argparse.Namespace, client: Client) -> int:
    """Routes model inspection and listing subcommands."""
    if args.models_action == "list":
        return _list_models(args, client)
    elif args.models_action == "get":
        return _get_model(args, client)
    print("Error: Unknown models action. Use 'list' or 'get'.", file=sys.stderr)
    return 1


def _handle_image(args: argparse.Namespace, client: Client) -> int:
    """Handles image generation."""
    if args.image_action != "generate":
        print("Error: Unknown image action. Use 'generate'.", file=sys.stderr)
        return 1

    if not args.prompt:
        print("Error: Prompt is required for image generation.", file=sys.stderr)
        return 1

    try:
        response = client.image.sample(
            prompt=args.prompt,
            model=args.model,
            image_format=args.format,
            image_url=args.image_url,
        )
        if args.output:
            with open(args.output, "wb") as f:
                f.write(response.image)
            print(f"Image saved to: {args.output}")
        elif args.format == "url":
            print(response.url)
        else:
            print(f"Image successfully generated ({len(response.image)} bytes). Use -o/--output to save.")
        return 0
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return 1


def _handle_video(args: argparse.Namespace, client: Client) -> int:
    """Handles video generation."""
    if args.video_action != "generate":
        print("Error: Unknown video action. Use 'generate'.", file=sys.stderr)
        return 1

    if not args.prompt:
        print("Error: Prompt is required for video generation.", file=sys.stderr)
        return 1

    try:
        response = client.video.generate(
            prompt=args.prompt,
            model=args.model,
            image_url=args.image_url or None,
            video_url=args.video_url or None,
            duration=args.duration or None,
            aspect_ratio=args.aspect_ratio or None,
            resolution=args.resolution or None,
        )
        if response.respect_moderation:
            print(f"Video URL: {response.url}")
            print(f"Duration: {response.duration}s")
            if response.cost_usd is not None:
                print(f"Cost: ${response.cost_usd:.4f}")
        else:
            print("Video URL not returned due to moderation.")
        return 0
    except Exception as e:
        print(f"Error generating video: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Builds the argument parser for the xai command."""
    parser = argparse.ArgumentParser(
        prog="xai",
        description="Official Command-Line Interface for the xAI SDK.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"xai-sdk {__version__}")
    parser.add_argument("--api-key", help="xAI API key. If not specified, reads from XAI_API_KEY.")
    parser.add_argument("--api-host", help="xAI API host. If not specified, reads from XAI_API_HOST.")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # chat command
    chat_parser = subparsers.add_parser("chat", help="Run single prompt or interactive chat.")
    chat_parser.add_argument("prompt", nargs="?", default=None, help="User prompt to send.")
    chat_parser.add_argument(
        "-m", "--model", default=os.getenv("XAI_MODEL", "grok-4.6"), help="Model to use (default: grok-4.6)."
    )
    chat_parser.add_argument("-s", "--system", help="System prompt to set context or instructions.")
    chat_parser.add_argument(
        "-i", "--interactive", action="store_true", help="Launch interactive multi-turn terminal chat."
    )
    chat_parser.add_argument(
        "--no-stream", dest="stream", action="store_false", default=True, help="Disable streaming response."
    )
    chat_parser.add_argument("-t", "--temperature", type=float, help="Sampling temperature.")
    chat_parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens to generate.")
    chat_parser.add_argument("--image", help="Path or URL to an image for vision understanding.")

    # models command
    models_parser = subparsers.add_parser("models", help="List or inspect models.")
    models_sub = models_parser.add_subparsers(dest="models_action", help="Models subcommands")
    models_list = models_sub.add_parser("list", help="List available models.")
    models_list.add_argument(
        "--type", choices=["language", "image", "embedding", "all"], default="language", help="Model type to list."
    )
    models_get = models_sub.add_parser("get", help="Get model details.")
    models_get.add_argument("name", help="Model name.")
    models_get.add_argument(
        "--type", choices=["language", "image", "embedding"], default="language", help="Model type."
    )

    # image command
    image_parser = subparsers.add_parser("image", help="Image operations.")
    image_sub = image_parser.add_subparsers(dest="image_action", help="Image subcommands")
    img_gen = image_sub.add_parser("generate", help="Generate an image from prompt.")
    img_gen.add_argument("prompt", help="Text description of the image to generate.")
    img_gen.add_argument("-m", "--model", default="grok-imagine-image", help="Model (default: grok-imagine-image).")
    img_gen.add_argument("-o", "--output", help="File path to save the generated image.")
    img_gen.add_argument("--format", choices=["base64", "url"], default="base64", help="Response format.")
    img_gen.add_argument("--image-url", help="Base image URL/path for image-to-image generation.")

    # video command
    video_parser = subparsers.add_parser("video", help="Video generation.")
    video_sub = video_parser.add_subparsers(dest="video_action", help="Video subcommands")
    vid_gen = video_sub.add_parser("generate", help="Generate a video from prompt.")
    vid_gen.add_argument("prompt", help="Text prompt for the video.")
    vid_gen.add_argument("-m", "--model", default="grok-imagine-video", help="Model (default: grok-imagine-video).")
    vid_gen.add_argument("--duration", type=int, help="Duration in seconds (1-15).")
    vid_gen.add_argument(
        "--aspect-ratio", choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"], help="Aspect ratio."
    )
    vid_gen.add_argument("--resolution", choices=["480p", "720p"], help="Video resolution.")
    vid_gen.add_argument("--image-url", help="First frame image for image-to-video.")
    vid_gen.add_argument("--video-url", help="Base video for video-to-video.")

    # version command
    subparsers.add_parser("version", help="Print SDK version.")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point for the xai command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 0

    if args.subcommand == "version":
        print(f"xai-sdk {__version__}")
        return 0

    api_key = args.api_key or os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: xAI API key is missing. Set XAI_API_KEY or pass --api-key.", file=sys.stderr)
        return 1

    handlers = {
        "chat": _handle_chat,
        "models": _handle_models,
        "image": _handle_image,
        "video": _handle_video,
    }
    handler = handlers.get(args.subcommand)
    if not handler:
        return 1

    client_kwargs = {"api_key": api_key}
    if args.api_host:
        client_kwargs["api_host"] = args.api_host

    ret = 1
    try:
        client = Client(**client_kwargs)
        ret = handler(args, client)
    except grpc.RpcError as e:
        code_name = e.code().name if hasattr(e, "code") and e.code() else "RPC_ERROR"
        details = e.details() if hasattr(e, "details") and e.details() else str(e)
        print(f"API Error ({code_name}): {details}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    return ret


if __name__ == "__main__":
    sys.exit(main())
