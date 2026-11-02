"""Shared Text-to-Speech (TTS) helpers, models, and validation.

The public TTS surface is REST-only (`POST /v1/tts`, `GET /v1/tts/voices`).
Sync and async clients live under ``xai_sdk.sync.tts`` / ``xai_sdk.aio.tts``.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from typing_extensions import NotRequired, TypedDict

from .client import USER_AGENT
from .types.tts import TtsBitRate, TtsCodec, TtsOptimizeStreamingLatency, TtsSampleRate

MAX_TEXT_LENGTH = 15_000
MAX_REPLACE_ENTRIES = 200
MAX_REPLACE_KEY_LENGTH = 100
MAX_REPLACE_VALUE_LENGTH = 128
MIN_SPEED = 0.7
MAX_SPEED = 1.5

_ALLOWED_CODECS = frozenset({"mp3", "wav", "pcm", "mulaw", "alaw"})
_ALLOWED_SAMPLE_RATES = frozenset({8000, 16000, 22050, 24000, 44100, 48000})
_ALLOWED_BIT_RATES = frozenset({32000, 64000, 96000, 128000, 192000})


class TtsError(Exception):
    """Raised when a TTS HTTP request fails."""

    def __init__(self, status_code: int, message: str, *, body: Optional[str] = None) -> None:
        """Initializes a new ``TtsError``.

        Args:
            status_code: HTTP status code returned by the API.
            message: Human-readable error description.
            body: Optional raw response body for debugging.
        """
        super().__init__(f"TTS request failed [{status_code}]: {message}")
        self.status_code = status_code
        self.message = message
        self.body = body


class OutputFormat(TypedDict):
    """Audio output format for unary TTS synthesis."""

    codec: TtsCodec
    sample_rate: NotRequired[TtsSampleRate]
    bit_rate: NotRequired[TtsBitRate]


@dataclass(frozen=True)
class AudioTimestamps:
    """Character-level timing metadata returned when ``with_timestamps=True``."""

    graph_chars: Sequence[str]
    graph_times: Sequence[tuple[float, float]]

    def pairs(self) -> Sequence[tuple[str, float, float]]:
        """Returns ``(char, start, end)`` triples aligned by index."""
        return [(char, start, end) for char, (start, end) in zip(self.graph_chars, self.graph_times, strict=False)]


@dataclass(frozen=True)
class Voice:
    """A built-in TTS voice from ``GET /v1/tts/voices``."""

    voice_id: str
    name: str
    language: Optional[str] = None


@dataclass(frozen=True)
class ListVoicesResponse:
    """Response from ``GET /v1/tts/voices``."""

    voices: Sequence[Voice] = field(default_factory=tuple)


@dataclass(frozen=True)
class TtsResponse:
    """Result of a unary TTS synthesis request.

    When ``with_timestamps`` is ``False``, ``audio`` contains the raw audio bytes
    and ``content_type`` comes from the response ``Content-Type`` header.
    When ``with_timestamps`` is ``True``, the API returns a JSON envelope; ``audio``
    is the decoded payload and ``duration`` / ``audio_timestamps`` are populated.
    """

    audio: bytes
    content_type: str
    duration: Optional[float] = None
    audio_timestamps: Optional[AudioTimestamps] = None
    with_timestamps: bool = False

    def write_to_file(self, path: str) -> None:
        """Writes the audio bytes to ``path``."""
        with open(path, "wb") as f:
            f.write(self.audio)


def _http_base_url(api_host: str, *, use_insecure_channel: bool = False) -> str:
    """Builds an HTTP(S) base URL from the gRPC-style ``api_host``."""
    host = api_host.strip().rstrip("/")
    if host.startswith("http://") or host.startswith("https://"):
        return host
    if use_insecure_channel or host.startswith("localhost") or host.startswith("127.0.0.1"):
        return f"http://{host}"
    return f"https://{host}"


def _auth_headers(
    api_key: str,
    metadata: Optional[tuple[tuple[str, str], ...]] = None,
) -> dict[str, str]:
    """Builds HTTP headers for TTS requests."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }
    if metadata:
        for key, value in metadata:
            # Avoid overriding core auth / content headers.
            if key.lower() in {"authorization", "content-type", "user-agent"}:
                continue
            headers[key] = value
    return headers


def _normalize_codec(codec: str) -> str:
    normalized = codec.lower()
    if normalized == "ulaw":
        return "mulaw"
    return normalized


def _validate_output_format(output_format: Optional[Mapping[str, Any]]) -> Optional[dict[str, Any]]:
    if output_format is None:
        return None
    if "codec" not in output_format:
        raise ValueError("output_format.codec is required when output_format is provided.")
    codec = _normalize_codec(str(output_format["codec"]))
    if codec not in _ALLOWED_CODECS:
        raise ValueError(
            f"Invalid output_format.codec {output_format['codec']!r}. Expected one of: mp3, wav, pcm, mulaw, alaw."
        )
    payload: dict[str, Any] = {"codec": codec}
    if "sample_rate" in output_format and output_format["sample_rate"] is not None:
        sample_rate = int(output_format["sample_rate"])
        if sample_rate not in _ALLOWED_SAMPLE_RATES:
            raise ValueError(
                f"Invalid output_format.sample_rate {sample_rate}. Expected one of: {sorted(_ALLOWED_SAMPLE_RATES)}."
            )
        payload["sample_rate"] = sample_rate
    if "bit_rate" in output_format and output_format["bit_rate"] is not None:
        bit_rate = int(output_format["bit_rate"])
        if bit_rate not in _ALLOWED_BIT_RATES:
            raise ValueError(
                f"Invalid output_format.bit_rate {bit_rate}. Expected one of: {sorted(_ALLOWED_BIT_RATES)}."
            )
        if codec != "mp3":
            raise ValueError("output_format.bit_rate is only valid when codec is 'mp3'.")
        payload["bit_rate"] = bit_rate
    return payload


def _validate_replace(replace: Optional[Mapping[str, str]]) -> Optional[dict[str, str]]:
    if replace is None:
        return None
    if len(replace) > MAX_REPLACE_ENTRIES:
        raise ValueError(f"replace has too many entries ({len(replace)}); maximum is {MAX_REPLACE_ENTRIES}.")

    seen_normalized: dict[str, str] = {}
    cleaned: dict[str, str] = {}
    for key, value in replace.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("replace keys and values must be strings.")
        if not key.strip():
            raise ValueError("replace keys must not be blank.")
        if len(key) > MAX_REPLACE_KEY_LENGTH:
            raise ValueError(f'replace key "{key}" is too long (max {MAX_REPLACE_KEY_LENGTH} characters).')
        if len(value) > MAX_REPLACE_VALUE_LENGTH:
            raise ValueError(f'replace value for "{key}" is too long (max {MAX_REPLACE_VALUE_LENGTH} characters).')
        if any(not (ch.isalnum() or ch in "' ") for ch in key):
            raise ValueError(f'replace key "{key}" may not contain punctuation or symbols.')
        normalized = " ".join(key.casefold().split())
        if normalized in seen_normalized:
            other = seen_normalized[normalized]
            raise ValueError(f'replace keys "{other}" and "{key}" are the same phrase; keep one.')
        seen_normalized[normalized] = key
        cleaned[key] = value
    return cleaned


def validate_synthesize_args(  # noqa: C901, PLR0912
    text: str,
    *,
    language: str,
    voice_id: Optional[str] = None,
    output_format: Optional[Mapping[str, Any]] = None,
    speed: Optional[float] = None,
    optimize_streaming_latency: Optional[int] = None,
    text_normalization: Optional[bool] = None,
    with_timestamps: Optional[bool] = None,
    replace: Optional[Mapping[str, str]] = None,
) -> dict[str, Any]:
    """Validates and builds the JSON body for ``POST /v1/tts``."""
    if not isinstance(text, str) or not text:
        raise ValueError("text must be a non-empty string.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"text exceeds maximum length of {MAX_TEXT_LENGTH} characters (got {len(text)}).")
    if not isinstance(language, str) or not language.strip():
        raise ValueError("language must be a non-empty string (BCP-47 code or 'auto').")

    body: dict[str, Any] = {
        "text": text,
        "language": language.strip(),
    }
    if voice_id is not None:
        if not isinstance(voice_id, str) or not voice_id.strip():
            raise ValueError("voice_id must be a non-empty string when provided.")
        body["voice_id"] = voice_id.strip()

    fmt = _validate_output_format(output_format)
    if fmt is not None:
        body["output_format"] = fmt

    if speed is not None:
        if not (MIN_SPEED <= float(speed) <= MAX_SPEED):
            raise ValueError(f"speed must be between {MIN_SPEED} and {MAX_SPEED} (got {speed}).")
        body["speed"] = float(speed)

    if optimize_streaming_latency is not None:
        level = int(optimize_streaming_latency)
        if level not in (0, 1, 2):
            raise ValueError("optimize_streaming_latency must be 0, 1, or 2.")
        body["optimize_streaming_latency"] = level

    if text_normalization is not None:
        body["text_normalization"] = bool(text_normalization)

    if with_timestamps is not None:
        body["with_timestamps"] = bool(with_timestamps)

    cleaned_replace = _validate_replace(replace)
    if cleaned_replace is not None:
        body["replace"] = cleaned_replace

    return body


def _parse_graph_times(raw_times: Any) -> list[tuple[float, float]]:
    """Parses ``graph_times`` as either ``[start, end]`` pairs or ``{start, end}`` objects."""
    if not isinstance(raw_times, list):
        raise TtsError(200, "Invalid audio_timestamps.graph_times in TTS response.")
    times: list[tuple[float, float]] = []
    for item in raw_times:
        if isinstance(item, Mapping):
            times.append((float(item["start"]), float(item["end"])))
        elif isinstance(item, list | tuple) and len(item) >= 2:  # noqa: PLR2004
            times.append((float(item[0]), float(item[1])))
        else:
            raise TtsError(200, f"Unrecognized graph_times entry: {item!r}")
    return times


def parse_voices_payload(payload: Mapping[str, Any]) -> ListVoicesResponse:
    """Parses a ``GET /v1/tts/voices`` JSON body."""
    raw_voices = payload.get("voices", [])
    if not isinstance(raw_voices, list):
        raise TtsError(200, "Invalid voices list in TTS response.")
    voices: list[Voice] = []
    for item in raw_voices:
        if not isinstance(item, Mapping):
            raise TtsError(200, f"Invalid voice entry: {item!r}")
        voices.append(
            Voice(
                voice_id=str(item["voice_id"]),
                name=str(item["name"]),
                language=item.get("language"),
            )
        )
    return ListVoicesResponse(voices=tuple(voices))


def parse_voice_payload(payload: Mapping[str, Any]) -> Voice:
    """Parses a ``GET /v1/tts/voices/{voice_id}`` JSON body."""
    return Voice(
        voice_id=str(payload["voice_id"]),
        name=str(payload["name"]),
        language=payload.get("language"),
    )


def parse_synthesize_response(
    *,
    content: bytes,
    content_type: str,
    with_timestamps: bool,
    json_payload: Optional[Mapping[str, Any]] = None,
) -> TtsResponse:
    """Builds a ``TtsResponse`` from either raw audio bytes or a timestamps JSON envelope."""
    if not with_timestamps:
        return TtsResponse(
            audio=content,
            content_type=content_type or "application/octet-stream",
            with_timestamps=False,
        )

    if json_payload is None:
        raise TtsError(200, "Expected JSON envelope when with_timestamps=True.")

    audio_b64 = json_payload.get("audio")
    if not isinstance(audio_b64, str):
        raise TtsError(200, "Missing base64 'audio' field in timestamps TTS response.")

    try:
        audio = base64.b64decode(audio_b64, validate=False)
    except Exception as exc:
        raise TtsError(200, f"Failed to decode base64 audio: {exc}") from exc

    timestamps = None
    raw_ts = json_payload.get("audio_timestamps")
    if isinstance(raw_ts, Mapping):
        chars = raw_ts.get("graph_chars") or []
        if not isinstance(chars, list):
            raise TtsError(200, "Invalid audio_timestamps.graph_chars in TTS response.")
        times = _parse_graph_times(raw_ts.get("graph_times") or [])
        timestamps = AudioTimestamps(
            graph_chars=tuple(str(c) for c in chars),
            graph_times=tuple(times),
        )

    duration_val = json_payload.get("duration")
    duration = float(duration_val) if duration_val is not None else None

    return TtsResponse(
        audio=audio,
        content_type=str(json_payload.get("content_type") or content_type or "application/octet-stream"),
        duration=duration,
        audio_timestamps=timestamps,
        with_timestamps=True,
    )


def is_success_status(status_code: int) -> bool:
    """Returns True for HTTP 2xx status codes."""
    return 200 <= status_code < 300  # noqa: PLR2004


def raise_for_tts_status(status_code: int, body_text: str) -> None:
    """Raises ``TtsError`` for non-success HTTP status codes."""
    if is_success_status(status_code):
        return
    message = body_text.strip() or _default_error_message(status_code)
    raise TtsError(status_code, message, body=body_text)


def _default_error_message(status_code: int) -> str:
    defaults = {
        400: "Bad request",
        401: "Unauthorized — API key is missing or invalid",
        404: "Not found — unknown voice_id",
        429: "Rate limited",
        500: "Server error",
        503: "Service unavailable",
    }
    return defaults.get(status_code, f"HTTP {status_code}")


class BaseClient:
    """Base client holding shared TTS HTTP configuration."""

    def __init__(
        self,
        api_key: str,
        api_host: str = "api.x.ai",
        *,
        timeout: Optional[float] = None,
        metadata: Optional[tuple[tuple[str, str], ...]] = None,
        use_insecure_channel: bool = False,
    ) -> None:
        """Creates a new TTS client.

        Args:
            api_key: xAI API key.
            api_host: API hostname (same as the gRPC client ``api_host``).
            timeout: Request timeout in seconds.
            metadata: Extra headers to attach to each request.
            use_insecure_channel: When True (or host is localhost), use ``http://``.
        """
        if not api_key:
            raise ValueError("Empty xAI API key provided.")
        self._api_key = api_key
        self._base_url = _http_base_url(api_host, use_insecure_channel=use_insecure_channel)
        self._timeout = timeout
        self._metadata = metadata
        self._headers = _auth_headers(api_key, metadata)

    @property
    def base_url(self) -> str:
        """HTTP base URL used for TTS requests."""
        return self._base_url


# Re-export type aliases for convenience.
__all__ = [
    "MAX_TEXT_LENGTH",
    "AudioTimestamps",
    "BaseClient",
    "ListVoicesResponse",
    "OutputFormat",
    "TtsBitRate",
    "TtsCodec",
    "TtsError",
    "TtsOptimizeStreamingLatency",
    "TtsResponse",
    "TtsSampleRate",
    "Voice",
    "is_success_status",
    "parse_synthesize_response",
    "parse_voice_payload",
    "parse_voices_payload",
    "raise_for_tts_status",
    "validate_synthesize_args",
]
