"""Type aliases for the Text-to-Speech API."""

from typing import Literal, TypeAlias

__all__ = [
    "TtsBitRate",
    "TtsCodec",
    "TtsLanguage",
    "TtsOptimizeStreamingLatency",
    "TtsSampleRate",
]

TtsCodec: TypeAlias = Literal["mp3", "wav", "pcm", "mulaw", "alaw", "ulaw"]
TtsSampleRate: TypeAlias = Literal[8000, 16000, 22050, 24000, 44100, 48000]
TtsBitRate: TypeAlias = Literal[32000, 64000, 96000, 128000, 192000]
TtsOptimizeStreamingLatency: TypeAlias = Literal[0, 1, 2]

# Documented BCP-47 codes; the API also accepts others with varying accuracy.
TtsLanguage: TypeAlias = Literal[
    "auto",
    "en",
    "ar-EG",
    "ar-SA",
    "ar-AE",
    "bn",
    "zh",
    "fr",
    "de",
    "hi",
    "id",
    "it",
    "ja",
    "ko",
    "pt-BR",
    "pt-PT",
    "ru",
    "es-MX",
    "es-ES",
    "tr",
    "vi",
]
