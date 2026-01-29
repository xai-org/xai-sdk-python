from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class GenerateImageRequest(_message.Message):
    __slots__ = ("prompt", "image", "model", "n", "user", "format", "aspect_ratio", "resolution")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    ASPECT_RATIO_FIELD_NUMBER: _ClassVar[int]
    RESOLUTION_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    image: ImageUrlContent
    model: str
    n: int
    user: str
    format: ImageFormat
    aspect_ratio: ImageAspectRatio
    resolution: ImageResolution
    def __init__(self, prompt: _Optional[str] = ..., image: _Optional[_Union[ImageUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., n: _Optional[int] = ..., user: _Optional[str] = ..., format: _Optional[_Union[ImageFormat, str]] = ..., aspect_ratio: _Optional[_Union[ImageAspectRatio, str]] = ..., resolution: _Optional[_Union[ImageResolution, str]] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("images", "model", "usage")
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[GeneratedImage]
    model: str
    usage: _usage_pb2.SamplingUsage
    def __init__(self, images: _Optional[_Iterable[_Union[GeneratedImage, _Mapping]]] = ..., model: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ...) -> None: ...

class GeneratedImage(_message.Message):
    __slots__ = ("base64", "url", "up_sampled_prompt", "respect_moderation")
    BASE64_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    UP_SAMPLED_PROMPT_FIELD_NUMBER: _ClassVar[int]
    RESPECT_MODERATION_FIELD_NUMBER: _ClassVar[int]
    base64: str
    url: str
    up_sampled_prompt: str
    respect_moderation: bool
    def __init__(self, base64: _Optional[str] = ..., url: _Optional[str] = ..., up_sampled_prompt: _Optional[str] = ..., respect_moderation: bool = ...) -> None: ...

class ImageUrlContent(_message.Message):
    __slots__ = ("image_url", "detail")
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    DETAIL_FIELD_NUMBER: _ClassVar[int]
    image_url: str
    detail: ImageDetail
    def __init__(self, image_url: _Optional[str] = ..., detail: _Optional[_Union[ImageDetail, str]] = ...) -> None: ...
