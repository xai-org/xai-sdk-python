from unittest import mock

import pytest

from xai_sdk import __version__
from xai_sdk.cli import (
    _build_messages,
    _handle_chat,
    _handle_image,
    _handle_models,
    _handle_video,
    _interactive_chat,
    _load_image,
    build_parser,
    main,
)


def test_parser_version(capsys):
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args(["--version"])
    assert exc.value.code == 0
    assert f"xai-sdk {__version__}" in capsys.readouterr().out


def test_main_version_subcommand(capsys):
    assert main(["version"]) == 0
    assert f"xai-sdk {__version__}" in capsys.readouterr().out


def test_main_empty_prints_help(capsys):
    assert main([]) == 0
    captured = capsys.readouterr().out
    assert "usage: xai" in captured
    assert "Available commands" in captured


def test_main_missing_api_key(monkeypatch, capsys):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert main(["chat", "hello"]) == 1
    assert "xAI API key is missing" in capsys.readouterr().err


def test_load_image_url():
    url = "https://example.com/test.png"
    img = _load_image(url)
    assert img.image_url.image_url == url


def test_load_image_local_file():
    img = _load_image("tests/test.jpg")
    assert img.image_url.image_url.startswith("data:image/jpeg;base64,")


def test_load_image_missing_file():
    with pytest.raises(FileNotFoundError):
        _load_image("tests/non_existent.png")


def test_build_messages():
    parser = build_parser()
    args = parser.parse_args(["chat", "hello", "--system", "be concise"])
    msgs = _build_messages(args, "hello")
    assert len(msgs) == 2
    assert msgs[0].content[0].text == "be concise"
    assert msgs[1].content[0].text == "hello"


def test_handle_chat_sample(capsys):
    parser = build_parser()
    args = parser.parse_args(["chat", "hello", "--no-stream"])

    mock_client = mock.MagicMock()
    mock_chat = mock.MagicMock()
    mock_response = mock.MagicMock()
    mock_response.content = "Quantum computing uses qubits."
    mock_chat.sample.return_value = mock_response
    mock_client.chat.create.return_value = mock_chat

    assert _handle_chat(args, mock_client) == 0
    assert "Quantum computing uses qubits." in capsys.readouterr().out


def test_handle_chat_stream(capsys):
    parser = build_parser()
    args = parser.parse_args(["chat", "hello"])

    mock_client = mock.MagicMock()
    mock_chat = mock.MagicMock()
    chunk1 = mock.MagicMock(content="Hello ")
    chunk2 = mock.MagicMock(content="world!")
    mock_chat.stream.return_value = [(mock.MagicMock(), chunk1), (mock.MagicMock(), chunk2)]
    mock_client.chat.create.return_value = mock_chat

    assert _handle_chat(args, mock_client) == 0
    assert "Hello world!" in capsys.readouterr().out


def test_handle_models_list(capsys):
    parser = build_parser()
    args = parser.parse_args(["models", "list", "--type", "language"])

    mock_client = mock.MagicMock()
    model_obj = mock.MagicMock(name="grok-4.6", version="1.0")
    model_obj.name = "grok-4.6"
    mock_client.models.list_language_models.return_value = [model_obj]

    assert _handle_models(args, mock_client) == 0
    assert "grok-4.6" in capsys.readouterr().out


def test_handle_models_get(capsys):
    parser = build_parser()
    args = parser.parse_args(["models", "get", "grok-4.6"])

    mock_client = mock.MagicMock()
    model_obj = mock.MagicMock(
        name="grok-4.6",
        aliases=["grok-latest"],
        version="1.0",
        input_modalities=["text"],
        output_modalities=["text"],
        max_prompt_length=131072,
    )
    model_obj.name = "grok-4.6"
    mock_client.models.get_language_model.return_value = model_obj

    assert _handle_models(args, mock_client) == 0
    out = capsys.readouterr().out
    assert "grok-4.6" in out
    assert "131072" in out


def test_handle_image_generate(capsys):
    parser = build_parser()
    args = parser.parse_args(["image", "generate", "a cute cat", "--format", "url"])

    mock_client = mock.MagicMock()
    mock_response = mock.MagicMock(url="https://x.ai/image.png")
    mock_client.image.sample.return_value = mock_response

    assert _handle_image(args, mock_client) == 0
    assert "https://x.ai/image.png" in capsys.readouterr().out


def test_handle_video_generate(capsys):
    parser = build_parser()
    args = parser.parse_args(["video", "generate", "a cinematic landscape"])

    mock_client = mock.MagicMock()
    mock_response = mock.MagicMock(
        respect_moderation=True,
        url="https://x.ai/video.mp4",
        duration=5,
        cost_usd=0.05,
    )
    mock_client.video.generate.return_value = mock_response

    assert _handle_video(args, mock_client) == 0
    out = capsys.readouterr().out
    assert "https://x.ai/video.mp4" in out
    assert "Duration: 5s" in out


def test_handle_chat_piped_stdin(monkeypatch, capsys):
    parser = build_parser()
    args = parser.parse_args(["chat", "Analyze this", "--no-stream"])

    monkeypatch.setattr("xai_sdk.cli._read_stdin", lambda: "Error 500: Server Error")

    mock_client = mock.MagicMock()
    mock_chat = mock.MagicMock()
    mock_response = mock.MagicMock(content="Found server error.")
    mock_chat.sample.return_value = mock_response
    mock_client.chat.create.return_value = mock_chat

    assert _handle_chat(args, mock_client) == 0
    assert "Found server error." in capsys.readouterr().out
    call_args = mock_client.chat.create.call_args[1]
    assert "Analyze this\n\nError 500: Server Error" in call_args["messages"][0].content[0].text


def test_handle_chat_no_prompt_not_interactive(capsys):
    parser = build_parser()
    args = parser.parse_args(["chat"])
    mock_client = mock.MagicMock()
    assert _handle_chat(args, mock_client) == 1
    assert "No prompt provided" in capsys.readouterr().err


def test_interactive_chat_exit(monkeypatch, capsys):
    parser = build_parser()
    args = parser.parse_args(["chat", "-i"])
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    mock_client = mock.MagicMock()
    mock_chat = mock.MagicMock()
    mock_client.chat.create.return_value = mock_chat
    assert _interactive_chat(args, mock_client) == 0
    assert "Bye!" in capsys.readouterr().out

