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
DETAIL_INVALID: ImageDetail
DETAIL_AUTO: ImageDetail
DETAIL_LOW: ImageDetail
DETAIL_HIGH: ImageDetail
IMG_FORMAT_INVALID: ImageFormat
IMG_FORMAT_BASE64: ImageFormat
IMG_FORMAT_URL: ImageFormat

class GenerateImageRequest(_message.Message):
    __slots__ = ("prompt", "image", "model", "n", "user", "format")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    prompt: str
    image: ImageUrlContent
    model: str
    n: int
    user: str
    format: ImageFormat
    def __init__(self, prompt: _Optional[str] = ..., image: _Optional[_Union[ImageUrlContent, _Mapping]] = ..., model: _Optional[str] = ..., n: _Optional[int] = ..., user: _Optional[str] = ..., format: _Optional[_Union[ImageFormat, str]] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("images", "model")
    IMAGES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    images: _containers.RepeatedCompositeFieldContainer[GeneratedImage]
    model: str
    def __init__(self, images: _Optional[_Iterable[_Union[GeneratedImage, _Mapping]]] = ..., model: _Optional[str] = ...) -> None: ...

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
