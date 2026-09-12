"""Unit tests for the asynchronous TTS client (mocked HTTP)."""

import base64
import json
from unittest import mock

import pytest

from xai_sdk import AsyncClient
from xai_sdk.aio.tts import Client as AsyncTtsClient
from xai_sdk.tts import TtsError

from .. import server


class _FakeResponse:
    def __init__(self, *, status=200, body=b"", headers=None):
        self.status = status
        self._body = body
        self.headers = headers or {}

    async def read(self):
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self._response = response
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self._response

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self._response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def tts_client():
    return AsyncTtsClient(api_key=server.API_KEY, api_host="api.x.ai")


@pytest.mark.asyncio
async def test_client_exposes_tts():
    with server.run_test_server() as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")
        assert hasattr(client, "tts")
        assert client.tts.base_url.startswith("http://localhost:")


@pytest.mark.asyncio
async def test_synthesize_raw_audio_success(tts_client: AsyncTtsClient):
    audio = b"ID3fake-mp3-bytes"
    fake = _FakeResponse(status=200, body=audio, headers={"Content-Type": "audio/mpeg"})
    session = _FakeSession(fake)
    with mock.patch("xai_sdk.aio.tts.aiohttp.ClientSession", return_value=session):
        result = await tts_client.synthesize("Hello world", language="en", voice_id="eve")

    assert result.audio == audio
    assert result.content_type == "audio/mpeg"
    assert session.post_calls
    url, kwargs = session.post_calls[0]
    assert url.endswith("/v1/tts")
    assert kwargs["json"]["text"] == "Hello world"


@pytest.mark.asyncio
async def test_synthesize_with_timestamps(tts_client: AsyncTtsClient):
    audio = b"timed-audio"
    payload = {
        "audio": base64.b64encode(audio).decode(),
        "content_type": "audio/mpeg",
        "duration": 0.5,
        "audio_timestamps": {
            "graph_chars": ["H", "i"],
            "graph_times": [{"start": 0.0, "end": 0.2}, {"start": 0.2, "end": 0.5}],
        },
    }
    fake = _FakeResponse(
        status=200,
        body=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    session = _FakeSession(fake)
    with mock.patch("xai_sdk.aio.tts.aiohttp.ClientSession", return_value=session):
        result = await tts_client.synthesize("Hi", language="en", with_timestamps=True)

    assert result.audio == audio
    assert result.duration == 0.5
    assert result.audio_timestamps is not None
    assert result.audio_timestamps.graph_times[0] == (0.0, 0.2)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [400, 401, 404, 429])
async def test_synthesize_http_errors(tts_client: AsyncTtsClient, status: int):
    fake = _FakeResponse(status=status, body=b"error")
    session = _FakeSession(fake)
    with mock.patch("xai_sdk.aio.tts.aiohttp.ClientSession", return_value=session):
        with pytest.raises(TtsError) as exc_info:
            await tts_client.synthesize("Hello", language="en")
    assert exc_info.value.status_code == status


@pytest.mark.asyncio
async def test_list_voices_success(tts_client: AsyncTtsClient):
    payload = {"voices": [{"voice_id": "eve", "name": "Eve", "language": "en"}]}
    fake = _FakeResponse(status=200, body=json.dumps(payload).encode())
    session = _FakeSession(fake)
    with mock.patch("xai_sdk.aio.tts.aiohttp.ClientSession", return_value=session):
        result = await tts_client.list_voices()
    assert result.voices[0].voice_id == "eve"


@pytest.mark.asyncio
async def test_get_voice_success(tts_client: AsyncTtsClient):
    payload = {"voice_id": "ara", "name": "Ara", "language": "en"}
    fake = _FakeResponse(status=200, body=json.dumps(payload).encode())
    session = _FakeSession(fake)
    with mock.patch("xai_sdk.aio.tts.aiohttp.ClientSession", return_value=session):
        voice = await tts_client.get_voice("ara")
    assert voice.name == "Ara"
