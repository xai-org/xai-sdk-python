import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageDetail(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DETAIL_INVALID: _ClassVar[ImageDetail]
    DETAIL_AUTO: _ClassVar[ImageDetail]
    DETAIL_LOW: _ClassVar[ImageDetail]
    DETAIL_HIGH: _ClassVar[ImageDetail]

class ImageFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMG_FORMAT_INVALID: _ClassVar[ImageFormat]
    IMG_FORMAT_BASE64: _ClassVar[ImageFormat]
    IMG_FORMAT_URL: _ClassVar[ImageFormat]

class ImageQuality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMG_QUALITY_INVALID: _ClassVar[ImageQuality]
    IMG_QUALITY_LOW: _ClassVar[ImageQuality]
    IMG_QUALITY_MEDIUM: _ClassVar[ImageQuality]
    IMG_QUALITY_HIGH: _ClassVar[ImageQuality]

class ImageAspectRatio(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMG_ASPECT_RATIO_INVALID: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_1_1: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_3_4: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_4_3: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_9_16: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_16_9: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_2_3: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_3_2: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_AUTO: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_9_19_5: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_19_5_9: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_9_20: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_20_9: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_1_2: _ClassVar[ImageAspectRatio]
    IMG_ASPECT_RATIO_2_1: _ClassVar[ImageAspectRatio]

class ImageResolution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMG_RESOLUTION_INVALID: _ClassVar[ImageResolution]
    IMG_RESOLUTION_1K: _ClassVar[ImageResolution]
    IMG_RESOLUTION_2K: _ClassVar[ImageResolution]

class ModerationLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODERATION_LEVEL_INVALID: _ClassVar[ModerationLevel]
    MODERATION_LEVEL_LOW: _ClassVar[ModerationLevel]
    MODERATION_LEVEL_AUTO: _ClassVar[ModerationLevel]
    MODERATION_LEVEL_HIGH: _ClassVar[ModerationLevel]

class SafetyCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SAFETY_CATEGORY_UNSPECIFIED: _ClassVar[SafetyCategory]
    SAFETY_CATEGORY_SEXUALLY_EXPLICIT: _ClassVar[SafetyCategory]
    SAFETY_CATEGORY_DANGEROUS_CONTENT: _ClassVar[SafetyCategory]

class SafetyThreshold(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BLOCK_UNSET: _ClassVar[SafetyThreshold]
    BLOCK_LOW_THRESHOLD: _ClassVar[SafetyThreshold]
    BLOCK_HIGH_THRESHOLD: _ClassVar[SafetyThreshold]
DETAIL_INVALID: ImageDetail
DETAIL_AUTO: ImageDetail
DETAIL_LOW: ImageDetail
DETAIL_HIGH: ImageDetail
IMG_FORMAT_INVALID: ImageFormat
IMG_FORMAT_BASE64: ImageFormat
IMG_FORMAT_URL: ImageFormat
IMG_QUALITY_INVALID: ImageQuality
IMG_QUALITY_LOW: ImageQuality
IMG_QUALITY_MEDIUM: ImageQuality
IMG_QUALITY_HIGH: ImageQuality
IMG_ASPECT_RATIO_INVALID: ImageAspectRatio
IMG_ASPECT_RATIO_1_1: ImageAspectRatio
IMG_ASPECT_RATIO_3_4: ImageAspectRatio
IMG_ASPECT_RATIO_4_3: ImageAspectRatio
IMG_ASPECT_RATIO_9_16: ImageAspectRatio
IMG_ASPECT_RATIO_16_9: ImageAspectRatio
IMG_ASPECT_RATIO_2_3: ImageAspectRatio
IMG_ASPECT_RATIO_3_2: ImageAspectRatio
IMG_ASPECT_RATIO_AUTO: ImageAspectRatio
IMG_ASPECT_RATIO_9_19_5: ImageAspectRatio
IMG_ASPECT_RATIO_19_5_9: ImageAspectRatio
IMG_ASPECT_RATIO_9_20: ImageAspectRatio
IMG_ASPECT_RATIO_20_9: ImageAspectRatio
IMG_ASPECT_RATIO_1_2: ImageAspectRatio
IMG_ASPECT_RATIO_2_1: ImageAspectRatio
IMG_RESOLUTION_INVALID: ImageResolution
IMG_RESOLUTION_1K: ImageResolution
IMG_RESOLUTION_2K: ImageResolution
MODERATION_LEVEL_INVALID: ModerationLevel
MODERATION_LEVEL_LOW: ModerationLevel
MODERATION_LEVEL_AUTO: ModerationLevel
MODERATION_LEVEL_HIGH: ModerationLevel
SAFETY_CATEGORY_UNSPECIFIED: SafetyCategory
SAFETY_CATEGORY_SEXUALLY_EXPLICIT: SafetyCategory
SAFETY_CATEGORY_DANGEROUS_CONTENT: SafetyCategory
BLOCK_UNSET: SafetyThreshold
BLOCK_LOW_THRESHOLD: SafetyThreshold
BLOCK_HIGH_THRESHOLD: SafetyThreshold

class GenerateImageRequest(_message.Message):
    __slots__ = ("prompt", "image", "model", "n", "user", "format", "quality", "aspect_ratio", "resolution", "moderation", "images", "safety_settings", "storage_options", "service_tier")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    QUALITY_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIO_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    MODERATION_FIELD_NUMBER: _ClassVar[int]
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    SAFETY_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    image: ImageUrlContent
    model: str
    n: int
    user: str
    format: ImageFormat
    quality: ImageQuality
    aspect_ratio: ImageAspectRatio
    resolution: ImageResolution
    moderation: ModerationLevel
    images: _containers.RepeatedCompositeFieldContainer[ImageUrlContent]
    safety_settings: _containers.RepeatedCompositeFieldContainer[SafetySetting]
    storage_options: StorageOptions
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, prompt: _Optional[str] = ..., image: _Optional[_Union[ImageUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., n: _Optional[int] = ..., user: _Optional[str] = ..., format: _Optional[_Union[ImageFormat, str]] = ..., quality: _Optional[_Union[ImageQuality, str]] = ..., aspect_ratio: _Optional[_Union[ImageAspectRatio, str]] = ..., resolution: _Optional[_Union[ImageResolution, str]] = ..., moderation: _Optional[_Union[ModerationLevel, str]] = ..., images: _Optional[_Iterable[_Union[ImageUrlContent, _Mapping]]] = ..., safety_settings: _Optional[_Iterable[_Union[SafetySetting, _Mapping]]] = ..., storage_options: _Optional[_Union[StorageOptions, _Mapping]] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...

class StorageOptions(_message.Message):
    __slots__ = ("filename", "expires_after", "public_url")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AFTER_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    filename: str
    expires_after: int
    public_url: PublicUrlOptions
    def __init__(self, filename: _Optional[str] = ..., expires_after: _Optional[int] = ..., public_url: _Optional[_Union[PublicUrlOptions, _Mapping]] = ...) -> None: ...

class PublicUrlOptions(_message.Message):
    __slots__ = ("expires_after",)
    EXPIRES_AFTER_FIELD_NUMBER: _ClassVar[int]
    expires_after: int
    def __init__(self, expires_after: _Optional[int] = ...) -> None: ...

class FileOutput(_message.Message):
    __slots__ = ("file_id", "filename", "public_url", "public_url_expires_at", "expires_at", "public_url_error")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_URL_ERROR_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    filename: str
    public_url: str
    public_url_expires_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    public_url_error: str
    def __init__(self, file_id: _Optional[str] = ..., filename: _Optional[str] = ..., public_url: _Optional[str] = ..., public_url_expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., public_url_error: _Optional[str] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("images", "model", "usage", "block_reason")
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    BLOCK_REASON_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[GeneratedImage]
    model: str
    usage: _usage_pb2.SamplingUsage
    block_reason: str
    def __init__(self, images: _Optional[_Iterable[_Union[GeneratedImage, _Mapping]]] = ..., model: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., block_reason: _Optional[str] = ...) -> None: ...

class GeneratedImage(_message.Message):
    __slots__ = ("base64", "url", "up_sampled_prompt", "respect_moderation", "debug_output", "moderation_categories", "mime_type", "file_output", "storage_error")
    BASE64_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    UP_SAMPLED_PROMPT_FIELD_NUMBER: _ClassVar[int]
    RESPECT_MODERATION_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    MODERATION_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ERROR_FIELD_NUMBER: _ClassVar[int]
    base64: str
    url: str
    up_sampled_prompt: str
    respect_moderation: bool
    debug_output: GeneratedImageDebugOutput
    moderation_categories: _containers.RepeatedCompositeFieldContainer[ModerationCategoryScore]
    mime_type: str
    file_output: FileOutput
    storage_error: str
    def __init__(self, base64: _Optional[str] = ..., url: _Optional[str] = ..., up_sampled_prompt: _Optional[str] = ..., respect_moderation: _Optional[bool] = ..., debug_output: _Optional[_Union[GeneratedImageDebugOutput, _Mapping]] = ..., moderation_categories: _Optional[_Iterable[_Union[ModerationCategoryScore, _Mapping]]] = ..., mime_type: _Optional[str] = ..., file_output: _Optional[_Union[FileOutput, _Mapping]] = ..., storage_error: _Optional[str] = ...) -> None: ...

class ModerationCategoryScore(_message.Message):
    __slots__ = ("name", "score", "threshold")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    name: str
    score: float
    threshold: float
    def __init__(self, name: _Optional[str] = ..., score: _Optional[float] = ..., threshold: _Optional[float] = ...) -> None: ...

class CandidateImage(_message.Message):
    __slots__ = ("base64", "url", "up_sampled_prompt")
    BASE64_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    UP_SAMPLED_PROMPT_FIELD_NUMBER: _ClassVar[int]
    base64: str
    url: str
    up_sampled_prompt: str
    def __init__(self, base64: _Optional[str] = ..., url: _Optional[str] = ..., up_sampled_prompt: _Optional[str] = ...) -> None: ...

class GeneratedImageDebugOutput(_message.Message):
    __slots__ = ("candidate_images", "grading_scores", "best_local_idx", "raw_grading")
    CANDIDATE_IMAGES_FIELD_NUMBER: _ClassVar[int]
    GRADING_SCORES_FIELD_NUMBER: _ClassVar[int]
    BEST_LOCAL_IDX_FIELD_NUMBER: _ClassVar[int]
    RAW_GRADING_FIELD_NUMBER: _ClassVar[int]
    candidate_images: _containers.RepeatedCompositeFieldContainer[CandidateImage]
    grading_scores: _containers.RepeatedScalarFieldContainer[int]
    best_local_idx: int
    raw_grading: str
    def __init__(self, candidate_images: _Optional[_Iterable[_Union[CandidateImage, _Mapping]]] = ..., grading_scores: _Optional[_Iterable[int]] = ..., best_local_idx: _Optional[int] = ..., raw_grading: _Optional[str] = ...) -> None: ...

class ImageUrlContent(_message.Message):
    __slots__ = ("image_url", "file_id", "detail")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    file_id: str
    detail: ImageDetail
    def __init__(self, image_url: _Optional[str] = ..., file_id: _Optional[str] = ..., detail: _Optional[_Union[ImageDetail, str]] = ...) -> None: ...

class SafetySetting(_message.Message):
    __slots__ = ("category", "threshold")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    category: SafetyCategory
    threshold: SafetyThreshold
    def __init__(self, category: _Optional[_Union[SafetyCategory, str]] = ..., threshold: _Optional[_Union[SafetyThreshold, str]] = ...) -> None: ...
