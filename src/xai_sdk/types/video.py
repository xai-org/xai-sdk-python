from typing import Annotated, Literal, TypeAlias

from pydantic import StringConstraints, TypeAdapter
from typing_extensions import TypedDict

from ..proto import video_pb2

__all__ = [
    "ReferenceAudio",
    "ReferenceAudioValidator",
    "VideoAspectRatio",
    "VideoAspectRatioMap",
    "VideoResolution",
    "VideoResolutionMap",
    "VoiceAudioRef",
]

# Aspect ratio for video generation.
VideoAspectRatio: TypeAlias = Literal[
    "1:1",
    "16:9",
    "9:16",
    "4:3",
    "3:4",
    "3:2",
    "2:3",
]

# Resolution for video generation.
VideoResolution: TypeAlias = Literal["480p", "720p", "1080p"]

# Non-empty string after stripping whitespace (Pydantic runtime check).
_NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class VoiceAudioRef(TypedDict):
    """Reference audio that uses a preset voice from the xAI voice catalog.

    ``voice_id`` is a first-party preset id shared with text-to-speech
    (e.g. ``"ara"``, ``"leo"``). See the
    `voice catalog <https://docs.x.ai/developers/model-capabilities/audio/text-to-speech#voices>`_
    for the full list of available presets.
    """

    voice_id: _NonEmptyStr


# Structured reference-audio entry for ``reference_audios``. Additional source
# kinds can be unioned in later without changing the top-level parameter.
ReferenceAudio: TypeAlias = VoiceAudioRef

# Runtime validation for public ``reference_audios`` entries.
ReferenceAudioValidator = TypeAdapter(ReferenceAudio)


VideoAspectRatioMap: dict[VideoAspectRatio, "video_pb2.VideoAspectRatio"] = {
    "1:1": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_1_1,
    "16:9": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_16_9,
    "9:16": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_9_16,
    "4:3": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_4_3,
    "3:4": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_3_4,
    "3:2": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_3_2,
    "2:3": video_pb2.VideoAspectRatio.VIDEO_ASPECT_RATIO_2_3,
}

VideoResolutionMap: dict[VideoResolution, "video_pb2.VideoResolution"] = {
    "480p": video_pb2.VideoResolution.VIDEO_RESOLUTION_480P,
    "720p": video_pb2.VideoResolution.VIDEO_RESOLUTION_720P,
    "1080p": video_pb2.VideoResolution.VIDEO_RESOLUTION_1080P,
}
