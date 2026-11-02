"""Asynchronous Text-to-Speech client (REST)."""

import json
from typing import Mapping, Optional, Union

import aiohttp

from ..tts import (
    BaseClient,
    ListVoicesResponse,
    OutputFormat,
    TtsOptimizeStreamingLatency,
    TtsResponse,
    Voice,
    is_success_status,
    parse_synthesize_response,
    parse_voice_payload,
    parse_voices_payload,
    raise_for_tts_status,
    validate_synthesize_args,
)


class Client(BaseClient):
    """Asynchronous client for the xAI Text-to-Speech REST API."""

    async def synthesize(
        self,
        text: str,
        *,
        language: str,
        voice_id: Optional[str] = None,
        output_format: Optional[Union[OutputFormat, Mapping[str, object]]] = None,
        speed: Optional[float] = None,
        optimize_streaming_latency: Optional[TtsOptimizeStreamingLatency] = None,
        text_normalization: Optional[bool] = None,
        with_timestamps: bool = False,
        replace: Optional[Mapping[str, str]] = None,
    ) -> TtsResponse:
        """Synthesize speech from text via ``POST /v1/tts``.

        Args:
            text: Text to convert to speech (max 15,000 characters). Supports speech tags.
            language: BCP-47 language code (e.g. ``"en"``, ``"zh"``, ``"pt-BR"``) or ``"auto"``.
            voice_id: Built-in or custom voice id. Defaults to ``"eve"`` on the server when omitted.
            output_format: Optional codec / sample_rate / bit_rate configuration.
            speed: Speech speed multiplier in ``[0.7, 1.5]``. Defaults to ``1.0``.
            optimize_streaming_latency: Latency optimization level ``0``, ``1``, or ``2``.
            text_normalization: When True, normalize written-form text before synthesis.
            with_timestamps: When True, return a JSON envelope with base64 audio and timings.
            replace: Phrase → pronunciation map applied before synthesis.

        Returns:
            A ``TtsResponse`` containing raw audio bytes (and optional timestamps metadata).

        Raises:
            ValueError: If request arguments fail local validation.
            TtsError: If the API returns a non-success status code.
        """
        body = validate_synthesize_args(
            text,
            language=language,
            voice_id=voice_id,
            output_format=output_format,
            speed=speed,
            optimize_streaming_latency=optimize_streaming_latency,
            text_normalization=text_normalization,
            with_timestamps=with_timestamps,
            replace=replace,
        )
        headers = {**self._headers, "Content-Type": "application/json"}
        timeout = aiohttp.ClientTimeout(total=self._timeout) if self._timeout is not None else None
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.post(f"{self._base_url}/v1/tts", headers=headers, json=body) as response,
        ):
            raw = await response.read()
            if not is_success_status(response.status):
                raise_for_tts_status(response.status, raw.decode("utf-8", errors="replace"))
            content_type = response.headers.get("Content-Type", "")
            if with_timestamps:
                payload = json.loads(raw.decode("utf-8"))
                return parse_synthesize_response(
                    content=raw,
                    content_type=content_type,
                    with_timestamps=True,
                    json_payload=payload,
                )
            return parse_synthesize_response(
                content=raw,
                content_type=content_type,
                with_timestamps=False,
            )

    async def list_voices(self) -> ListVoicesResponse:
        """List built-in TTS voices via ``GET /v1/tts/voices``.

        Returns:
            A ``ListVoicesResponse`` with available voices.

        Raises:
            TtsError: If the API returns a non-success status code.
        """
        timeout = aiohttp.ClientTimeout(total=self._timeout) if self._timeout is not None else None
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.get(f"{self._base_url}/v1/tts/voices", headers=self._headers) as response,
        ):
            raw = await response.read()
            if not is_success_status(response.status):
                raise_for_tts_status(response.status, raw.decode("utf-8", errors="replace"))
            return parse_voices_payload(json.loads(raw.decode("utf-8")))

    async def get_voice(self, voice_id: str) -> Voice:
        """Get a single built-in voice via ``GET /v1/tts/voices/{voice_id}``.

        Args:
            voice_id: Voice identifier (e.g. ``"eve"``).

        Returns:
            A ``Voice`` object.

        Raises:
            ValueError: If ``voice_id`` is empty.
            TtsError: If the API returns a non-success status code.
        """
        if not voice_id or not voice_id.strip():
            raise ValueError("voice_id must be a non-empty string.")
        timeout = aiohttp.ClientTimeout(total=self._timeout) if self._timeout is not None else None
        async with (
            aiohttp.ClientSession(timeout=timeout) as session,
            session.get(
                f"{self._base_url}/v1/tts/voices/{voice_id.strip()}",
                headers=self._headers,
            ) as response,
        ):
            raw = await response.read()
            if not is_success_status(response.status):
                raise_for_tts_status(response.status, raw.decode("utf-8", errors="replace"))
            return parse_voice_payload(json.loads(raw.decode("utf-8")))
