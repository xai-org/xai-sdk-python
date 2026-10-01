"""Unit tests for shared TTS validation and response parsing."""

import base64

import pytest

from xai_sdk.tts import (
    MAX_TEXT_LENGTH,
    TtsError,
    parse_synthesize_response,
    parse_voices_payload,
    validate_synthesize_args,
)


def test_validate_synthesize_minimal():
    body = validate_synthesize_args("Hello", language="en")
    assert body == {"text": "Hello", "language": "en"}


def test_validate_synthesize_full():
    body = validate_synthesize_args(
        "Hello",
        language="en",
        voice_id="ara",
        output_format={"codec": "mp3", "sample_rate": 44100, "bit_rate": 192000},
        speed=1.2,
        optimize_streaming_latency=1,
        text_normalization=True,
        with_timestamps=True,
        replace={"Acme Mobile": "Acme Mobull"},
    )
    assert body["voice_id"] == "ara"
    assert body["output_format"] == {"codec": "mp3", "sample_rate": 44100, "bit_rate": 192000}
    assert body["speed"] == 1.2
    assert body["optimize_streaming_latency"] == 1
    assert body["text_normalization"] is True
    assert body["with_timestamps"] is True
    assert body["replace"] == {"Acme Mobile": "Acme Mobull"}


def test_validate_empty_text():
    with pytest.raises(ValueError, match="non-empty"):
        validate_synthesize_args("", language="en")


def test_validate_text_too_long():
    with pytest.raises(ValueError, match="maximum length"):
        validate_synthesize_args("x" * (MAX_TEXT_LENGTH + 1), language="en")


def test_validate_language_required():
    with pytest.raises(ValueError, match="language"):
        validate_synthesize_args("hi", language="  ")


def test_validate_speed_range():
    with pytest.raises(ValueError, match="speed"):
        validate_synthesize_args("hi", language="en", speed=0.5)
    with pytest.raises(ValueError, match="speed"):
        validate_synthesize_args("hi", language="en", speed=2.0)


def test_validate_codec_and_bitrate():
    with pytest.raises(ValueError, match="codec"):
        validate_synthesize_args("hi", language="en", output_format={"codec": "flac"})
    with pytest.raises(ValueError, match="bit_rate"):
        validate_synthesize_args(
            "hi",
            language="en",
            output_format={"codec": "wav", "bit_rate": 128000},
        )


def test_validate_ulaw_alias():
    body = validate_synthesize_args(
        "hi",
        language="en",
        output_format={"codec": "ulaw", "sample_rate": 8000},
    )
    assert body["output_format"]["codec"] == "mulaw"


def test_validate_replace_limits():
    with pytest.raises(ValueError, match="punctuation"):
        validate_synthesize_args("hi", language="en", replace={"C++": "cee plus plus"})
    with pytest.raises(ValueError, match="same phrase"):
        validate_synthesize_args("hi", language="en", replace={"Acme": "a", "acme": "b"})


def test_parse_raw_audio_response():
    resp = parse_synthesize_response(
        content=b"ID3fakeaudio",
        content_type="audio/mpeg",
        with_timestamps=False,
    )
    assert resp.audio == b"ID3fakeaudio"
    assert resp.content_type == "audio/mpeg"
    assert resp.duration is None
    assert resp.audio_timestamps is None
    assert resp.with_timestamps is False


def test_parse_timestamps_envelope_list_pairs():
    audio = b"abc123"
    payload = {
        "audio": base64.b64encode(audio).decode(),
        "content_type": "audio/mpeg",
        "duration": 0.92,
        "audio_timestamps": {
            "graph_chars": ["H", "i"],
            "graph_times": [[0.0, 0.4], [0.4, 0.92]],
        },
    }
    resp = parse_synthesize_response(
        content=b"{}",
        content_type="application/json",
        with_timestamps=True,
        json_payload=payload,
    )
    assert resp.audio == audio
    assert resp.duration == 0.92
    assert resp.audio_timestamps is not None
    assert list(resp.audio_timestamps.graph_chars) == ["H", "i"]
    assert list(resp.audio_timestamps.graph_times) == [(0.0, 0.4), (0.4, 0.92)]


def test_parse_timestamps_envelope_object_pairs():
    audio = b"xyz"
    payload = {
        "audio": base64.b64encode(audio).decode(),
        "content_type": "audio/wav",
        "duration": 1.0,
        "audio_timestamps": {
            "graph_chars": ["a"],
            "graph_times": [{"start": 0.0, "end": 1.0}],
        },
    }
    resp = parse_synthesize_response(
        content=b"{}",
        content_type="application/json",
        with_timestamps=True,
        json_payload=payload,
    )
    assert resp.audio == audio
    assert resp.audio_timestamps is not None
    assert resp.audio_timestamps.graph_times[0] == (0.0, 1.0)


def test_parse_voices():
    payload = {
        "voices": [
            {"voice_id": "eve", "name": "Eve", "language": "en"},
            {"voice_id": "ara", "name": "Ara", "language": "en"},
        ]
    }
    result = parse_voices_payload(payload)
    assert len(result.voices) == 2
    assert result.voices[0].voice_id == "eve"
    assert result.voices[1].name == "Ara"


def test_tts_error_str():
    err = TtsError(401, "Unauthorized")
    assert "401" in str(err)
    assert err.status_code == 401
