from typing import Literal, TypeAlias

from ..proto import video_pb2

__all__ = [
    "VideoAspectRatio",
    "VideoAspectRatioMap",
    "VideoResolution",
    "VideoResolutionMap",
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
VideoResolution: TypeAlias = Literal["480p", "720p"]

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
}
