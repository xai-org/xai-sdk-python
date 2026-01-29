from . import image_pb2 as _image_pb2
from . import deferred_pb2 as _deferred_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VideoAspectRatio(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VIDEO_ASPECT_RATIO_UNSPECIFIED: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_1_1: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_16_9: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_9_16: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_4_3: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_3_4: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_3_2: _ClassVar[VideoAspectRatio]
    VIDEO_ASPECT_RATIO_2_3: _ClassVar[VideoAspectRatio]

class VideoResolution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VIDEO_RESOLUTION_UNSPECIFIED: _ClassVar[VideoResolution]
    VIDEO_RESOLUTION_480P: _ClassVar[VideoResolution]
    VIDEO_RESOLUTION_720P: _ClassVar[VideoResolution]
VIDEO_ASPECT_RATIO_UNSPECIFIED: VideoAspectRatio
VIDEO_ASPECT_RATIO_1_1: VideoAspectRatio
VIDEO_ASPECT_RATIO_16_9: VideoAspectRatio
VIDEO_ASPECT_RATIO_9_16: VideoAspectRatio
VIDEO_ASPECT_RATIO_4_3: VideoAspectRatio
VIDEO_ASPECT_RATIO_3_4: VideoAspectRatio
VIDEO_ASPECT_RATIO_3_2: VideoAspectRatio
VIDEO_ASPECT_RATIO_2_3: VideoAspectRatio
VIDEO_RESOLUTION_UNSPECIFIED: VideoResolution
VIDEO_RESOLUTION_480P: VideoResolution
VIDEO_RESOLUTION_720P: VideoResolution

class VideoUrlContent(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class VideoOutput(_message.Message):
    __slots__ = ("upload_url",)
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    def __init__(self, upload_url: _Optional[str] = ...) -> None: ...

class GenerateVideoRequest(_message.Message):
    __slots__ = ("prompt", "image", "model", "duration", "video", "aspect_ratio", "resolution")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIO_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    image: _image_pb2.ImageUrlContent
    model: str
    duration: int
    video: VideoUrlContent
    aspect_ratio: VideoAspectRatio
    resolution: VideoResolution
    def __init__(self, prompt: _Optional[str] = ..., image: _Optional[_Union[_image_pb2.ImageUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., duration: _Optional[int] = ..., video: _Optional[_Union[VideoUrlContent, _Mapping]] = ..., aspect_ratio: _Optional[_Union[VideoAspectRatio, str]] = ..., resolution: _Optional[_Union[VideoResolution, str]] = ...) -> None: ...

class GetDeferredVideoRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class VideoResponse(_message.Message):
    __slots__ = ("video", "model", "usage")
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    video: GeneratedVideo
    model: str
    usage: _usage_pb2.SamplingUsage
    def __init__(self, video: _Optional[_Union[GeneratedVideo, _Mapping]] = ..., model: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ...) -> None: ...

class GeneratedVideo(_message.Message):
    __slots__ = ("url", "duration", "respect_moderation")
    URL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    RESPECT_MODERATION_FIELD_NUMBER: _ClassVar[int]
    url: str
    duration: int
    respect_moderation: bool
    def __init__(self, url: _Optional[str] = ..., duration: _Optional[int] = ..., respect_moderation: bool = ...) -> None: ...

class GetDeferredVideoResponse(_message.Message):
    __slots__ = ("status", "response")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status: _deferred_pb2.DeferredStatus
    response: VideoResponse
    def __init__(self, status: _Optional[_Union[_deferred_pb2.DeferredStatus, str]] = ..., response: _Optional[_Union[VideoResponse, _Mapping]] = ...) -> None: ...
