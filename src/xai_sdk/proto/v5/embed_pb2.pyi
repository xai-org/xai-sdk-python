from . import image_pb2 as _image_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmbedEncodingFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMAT_INVALID: _ClassVar[EmbedEncodingFormat]
    FORMAT_FLOAT: _ClassVar[EmbedEncodingFormat]
    FORMAT_BASE64: _ClassVar[EmbedEncodingFormat]
FORMAT_INVALID: EmbedEncodingFormat
FORMAT_FLOAT: EmbedEncodingFormat
FORMAT_BASE64: EmbedEncodingFormat

class EmbedRequest(_message.Message):
    __slots__ = ("input", "model", "encoding_format", "user")
    INPUT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    ENCODING_FORMAT_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    input: _containers.RepeatedCompositeFieldContainer[EmbedInput]
    model: str
    encoding_format: EmbedEncodingFormat
    user: str
    def __init__(self, input: _Optional[_Iterable[_Union[EmbedInput, _Mapping]]] = ..., model: _Optional[str] = ..., encoding_format: _Optional[_Union[EmbedEncodingFormat, str]] = ..., user: _Optional[str] = ...) -> None: ...

class EmbedInput(_message.Message):
    __slots__ = ("string", "image_url")
    STRING_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    string: str
    image_url: _image_pb2.ImageUrlContent
    def __init__(self, string: _Optional[str] = ..., image_url: _Optional[_Union[_image_pb2.ImageUrlContent, _Mapping]] = ...) -> None: ...

class EmbedResponse(_message.Message):
    __slots__ = ("id", "embeddings", "usage", "model", "system_fingerprint")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    id: str
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    usage: _usage_pb2.EmbeddingUsage
    model: str
    system_fingerprint: str
    def __init__(self, id: _Optional[str] = ..., embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ..., usage: _Optional[_Union[_usage_pb2.EmbeddingUsage, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ("index", "embeddings")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    index: int
    embeddings: _containers.RepeatedCompositeFieldContainer[FeatureVector]
    def __init__(self, index: _Optional[int] = ..., embeddings: _Optional[_Iterable[_Union[FeatureVector, _Mapping]]] = ...) -> None: ...

class FeatureVector(_message.Message):
    __slots__ = ("float_array", "base64_array")
    FLOAT_ARRAY_FIELD_NUMBER: _ClassVar[int]
    BASE64_ARRAY_FIELD_NUMBER: _ClassVar[int]
    float_array: _containers.RepeatedScalarFieldContainer[float]
    base64_array: str
    def __init__(self, float_array: _Optional[_Iterable[float]] = ..., base64_array: _Optional[str] = ...) -> None: ...
