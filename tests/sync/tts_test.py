"""Unit tests for the synchronous TTS client (mocked HTTP)."""

import base64
import json
from unittest import mock

import pytest

from xai_sdk import Client
from xai_sdk.sync.tts import Client as TtsClient
from xai_sdk.tts import TtsError

from .. import server


@pytest.fixture
def tts_client():
    return TtsClient(api_key=server.API_KEY, api_host="api.x.ai")


def _mock_response(*, status_code=200, content=b"", headers=None, json_data=None, text=""):
    response = mock.Mock()
    response.status_code = status_code
    response.content = content if json_data is None else json.dumps(json_data).encode()
    response.headers = headers or {}
    response.text = text if text or json_data is None else json.dumps(json_data)
    response.json.return_value = json_data
    return response


def test_client_exposes_tts():
    with server.run_test_server() as port:
        client = Client(api_key=server.API_KEY, api_host=f"localhost:{port}")
        assert hasattr(client, "tts")
        assert client.tts.base_url.startswith("http://localhost:")


def test_synthesize_raw_audio_success(tts_client: TtsClient):
    audio = b"ID3fake-mp3-bytes"
    mock_resp = _mock_response(
        status_code=200,
        content=audio,
        headers={"Content-Type": "audio/mpeg"},
    )
    with mock.patch("xai_sdk.sync.tts.requests.post", return_value=mock_resp) as post:
        result = tts_client.synthesize("Hello world", language="en", voice_id="eve")

    assert result.audio == audio
    assert result.content_type == "audio/mpeg"
    assert result.with_timestamps is False
    post.assert_called_once()
    _, kwargs = post.call_args
    assert kwargs["json"]["text"] == "Hello world"
    assert kwargs["json"]["language"] == "en"
    assert kwargs["json"]["voice_id"] == "eve"
    assert kwargs["headers"]["Authorization"] == f"Bearer {server.API_KEY}"


def test_synthesize_with_timestamps(tts_client: TtsClient):
    audio = b"timed-audio"
    payload = {
        "audio": base64.b64encode(audio).decode(),
        "content_type": "audio/mpeg",
        "duration": 0.5,
        "audio_timestamps": {
            "graph_chars": ["H", "i"],
            "graph_times": [[0.0, 0.2], [0.2, 0.5]],
        },
    }
    mock_resp = _mock_response(
        status_code=200,
        json_data=payload,
        headers={"Content-Type": "application/json"},
    )
    with mock.patch("xai_sdk.sync.tts.requests.post", return_value=mock_resp):
        result = tts_client.synthesize("Hi", language="en", with_timestamps=True)

    assert result.audio == audio
    assert result.duration == 0.5
    assert result.audio_timestamps is not None
    assert list(result.audio_timestamps.graph_chars) == ["H", "i"]


@pytest.mark.parametrize(
    "status,body",
    [(400, "bad request"), (401, "unauthorized"), (404, "unknown voice"), (429, "rate limit")],
)
def test_synthesize_http_errors(tts_client: TtsClient, status: int, body: str):
    mock_resp = _mock_response(status_code=status, text=body, content=body.encode())
    with mock.patch("xai_sdk.sync.tts.requests.post", return_value=mock_resp):
        with pytest.raises(TtsError) as exc_info:
            tts_client.synthesize("Hello", language="en")
    assert exc_info.value.status_code == status


def test_synthesize_validation_error_before_http(tts_client: TtsClient):
    with mock.patch("xai_sdk.sync.tts.requests.post") as post:
        with pytest.raises(ValueError, match="non-empty"):
            tts_client.synthesize("", language="en")
    post.assert_not_called()


def test_list_voices_success(tts_client: TtsClient):
    payload = {
        "voices": [
            {"voice_id": "eve", "name": "Eve", "language": "en"},
            {"voice_id": "leo", "name": "Leo", "language": "en"},
        ]
    }
    mock_resp = _mock_response(status_code=200, json_data=payload, headers={"Content-Type": "application/json"})
    with mock.patch("xai_sdk.sync.tts.requests.get", return_value=mock_resp) as get:
        result = tts_client.list_voices()

    assert len(result.voices) == 2
    assert result.voices[0].voice_id == "eve"
    get.assert_called_once()
    args, _ = get.call_args
    assert args[0].endswith("/v1/tts/voices")


def test_list_voices_unauthorized(tts_client: TtsClient):
    mock_resp = _mock_response(status_code=401, text="unauthorized")
    with mock.patch("xai_sdk.sync.tts.requests.get", return_value=mock_resp):
        with pytest.raises(TtsError) as exc_info:
            tts_client.list_voices()
    assert exc_info.value.status_code == 401


def test_get_voice_success(tts_client: TtsClient):
    payload = {"voice_id": "eve", "name": "Eve", "language": "en"}
    mock_resp = _mock_response(status_code=200, json_data=payload)
    with mock.patch("xai_sdk.sync.tts.requests.get", return_value=mock_resp):
        voice = tts_client.get_voice("eve")
    assert voice.voice_id == "eve"
    assert voice.name == "Eve"


def test_get_voice_not_found(tts_client: TtsClient):
    mock_resp = _mock_response(status_code=404, text="not found")
    with mock.patch("xai_sdk.sync.tts.requests.get", return_value=mock_resp):
        with pytest.raises(TtsError) as exc_info:
            tts_client.get_voice("nope")
    assert exc_info.value.status_code == 404
