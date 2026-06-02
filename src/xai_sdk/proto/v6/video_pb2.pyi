from . import image_pb2 as _image_pb2
from . import deferred_pb2 as _deferred_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VideoSize(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VIDEO_SIZE_UNSPECIFIED: _ClassVar[VideoSize]
    VIDEO_SIZE_848X480: _ClassVar[VideoSize]
    VIDEO_SIZE_1696X960: _ClassVar[VideoSize]
    VIDEO_SIZE_1280X720: _ClassVar[VideoSize]
    VIDEO_SIZE_1920X1080: _ClassVar[VideoSize]

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
    VIDEO_RESOLUTION_1080P: _ClassVar[VideoResolution]
VIDEO_SIZE_UNSPECIFIED: VideoSize
VIDEO_SIZE_848X480: VideoSize
VIDEO_SIZE_1696X960: VideoSize
VIDEO_SIZE_1280X720: VideoSize
VIDEO_SIZE_1920X1080: VideoSize
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
VIDEO_RESOLUTION_1080P: VideoResolution

class VideoUrlContent(_message.Message):
    __slots__ = ("url", "file_id")
    URL_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    url: str
    file_id: str
    def __init__(self, url: _Optional[str] = ..., file_id: _Optional[str] = ...) -> None: ...

class VideoOutput(_message.Message):
    __slots__ = ("upload_url",)
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    def __init__(self, upload_url: _Optional[str] = ...) -> None: ...

class GenerateVideoRequest(_message.Message):
    __slots__ = ("prompt", "image", "model", "duration", "size", "video", "aspect_ratio", "resolution", "moderation", "output", "safety_settings", "images", "reference_images", "storage_options", "service_tier")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIO_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    MODERATION_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SAFETY_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_IMAGES_FIELD_NUMBER: _ClassVar[int]
    STORAGE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    image: _image_pb2.ImageUrlContent
    model: str
    duration: int
    size: VideoSize
    video: VideoUrlContent
    aspect_ratio: VideoAspectRatio
    resolution: VideoResolution
    moderation: _image_pb2.ModerationLevel
    output: VideoOutput
    safety_settings: _containers.RepeatedCompositeFieldContainer[_image_pb2.SafetySetting]
    images: _containers.RepeatedCompositeFieldContainer[_image_pb2.ImageUrlContent]
    reference_images: _containers.RepeatedCompositeFieldContainer[_image_pb2.ImageUrlContent]
    storage_options: _image_pb2.StorageOptions
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, prompt: _Optional[str] = ..., image: _Optional[_Union[_image_pb2.ImageUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., duration: _Optional[int] = ..., size: _Optional[_Union[VideoSize, str]] = ..., video: _Optional[_Union[VideoUrlContent, _Mapping]] = ..., aspect_ratio: _Optional[_Union[VideoAspectRatio, str]] = ..., resolution: _Optional[_Union[VideoResolution, str]] = ..., moderation: _Optional[_Union[_image_pb2.ModerationLevel, str]] = ..., output: _Optional[_Union[VideoOutput, _Mapping]] = ..., safety_settings: _Optional[_Iterable[_Union[_image_pb2.SafetySetting, _Mapping]]] = ..., images: _Optional[_Iterable[_Union[_image_pb2.ImageUrlContent, _Mapping]]] = ..., reference_images: _Optional[_Iterable[_Union[_image_pb2.ImageUrlContent, _Mapping]]] = ..., storage_options: _Optional[_Union[_image_pb2.StorageOptions, _Mapping]] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...

class GetDeferredVideoRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class VideoResponse(_message.Message):
    __slots__ = ("video", "model", "usage", "debug_output", "block_reason", "error", "progress")
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    BLOCK_REASON_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    video: GeneratedVideo
    model: str
    usage: _usage_pb2.SamplingUsage
    debug_output: VideoDebugOutput
    block_reason: str
    error: VideoError
    progress: int
    def __init__(self, video: _Optional[_Union[GeneratedVideo, _Mapping]] = ..., model: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., debug_output: _Optional[_Union[VideoDebugOutput, _Mapping]] = ..., block_reason: _Optional[str] = ..., error: _Optional[_Union[VideoError, _Mapping]] = ..., progress: _Optional[int] = ...) -> None: ...

class GeneratedVideo(_message.Message):
    __slots__ = ("url", "duration", "respect_moderation", "file_output", "storage_error")
    URL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    RESPECT_MODERATION_FIELD_NUMBER: _ClassVar[int]
    FILE_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ERROR_FIELD_NUMBER: _ClassVar[int]
    url: str
    duration: int
    respect_moderation: bool
    file_output: _image_pb2.FileOutput
    storage_error: str
    def __init__(self, url: _Optional[str] = ..., duration: _Optional[int] = ..., respect_moderation: _Optional[bool] = ..., file_output: _Optional[_Union[_image_pb2.FileOutput, _Mapping]] = ..., storage_error: _Optional[str] = ...) -> None: ...

class GetDeferredVideoResponse(_message.Message):
    __slots__ = ("status", "response")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status: _deferred_pb2.DeferredStatus
    response: VideoResponse
    def __init__(self, status: _Optional[_Union[_deferred_pb2.DeferredStatus, str]] = ..., response: _Optional[_Union[VideoResponse, _Mapping]] = ...) -> None: ...

class VideoDebugOutput(_message.Message):
    __slots__ = ("upsampled_prompt",)
    UPSAMPLED_PROMPT_FIELD_NUMBER: _ClassVar[int]
    upsampled_prompt: str
    def __init__(self, upsampled_prompt: _Optional[str] = ...) -> None: ...

class VideoError(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ExtendVideoRequest(_message.Message):
    __slots__ = ("prompt", "video", "model", "duration", "output", "storage_options", "service_tier")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    VIDEO_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    video: VideoUrlContent
    model: str
    duration: int
    output: VideoOutput
    storage_options: _image_pb2.StorageOptions
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, prompt: _Optional[str] = ..., video: _Optional[_Union[VideoUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., duration: _Optional[int] = ..., output: _Optional[_Union[VideoOutput, _Mapping]] = ..., storage_options: _Optional[_Union[_image_pb2.StorageOptions, _Mapping]] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...
