from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HNSWMetric(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HNSW_METRIC_UNKNOWN: _ClassVar[HNSWMetric]
    HNSW_METRIC_COSINE: _ClassVar[HNSWMetric]
    HNSW_METRIC_EUCLIDEAN: _ClassVar[HNSWMetric]
    HNSW_METRIC_INNER_PRODUCT: _ClassVar[HNSWMetric]
HNSW_METRIC_UNKNOWN: HNSWMetric
HNSW_METRIC_COSINE: HNSWMetric
HNSW_METRIC_EUCLIDEAN: HNSWMetric
HNSW_METRIC_INNER_PRODUCT: HNSWMetric

class IndexConfiguration(_message.Message):
    __slots__ = ("model_name",)
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    model_name: str
    def __init__(self, model_name: _Optional[str] = ...) -> None: ...

class ChunkConfiguration(_message.Message):
    __slots__ = ("chars_configuration", "tokens_configuration", "bytes_configuration", "strip_whitespace", "inject_name_into_chunks")
    CHARS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    TOKENS_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    BYTES_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    STRIP_WHITESPACE_FIELD_NUMBER: _ClassVar[int]
    INJECT_NAME_INTO_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    chars_configuration: CharsConfiguration
    tokens_configuration: TokensConfiguration
    bytes_configuration: BytesConfiguration
    strip_whitespace: bool
    inject_name_into_chunks: bool
    def __init__(self, chars_configuration: _Optional[_Union[CharsConfiguration, _Mapping]] = ..., tokens_configuration: _Optional[_Union[TokensConfiguration, _Mapping]] = ..., bytes_configuration: _Optional[_Union[BytesConfiguration, _Mapping]] = ..., strip_whitespace: bool = ..., inject_name_into_chunks: bool = ...) -> None: ...

class CharsConfiguration(_message.Message):
    __slots__ = ("max_chunk_size_chars", "chunk_overlap_chars")
    MAX_CHUNK_SIZE_CHARS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_OVERLAP_CHARS_FIELD_NUMBER: _ClassVar[int]
    max_chunk_size_chars: int
    chunk_overlap_chars: int
    def __init__(self, max_chunk_size_chars: _Optional[int] = ..., chunk_overlap_chars: _Optional[int] = ...) -> None: ...

class TokensConfiguration(_message.Message):
    __slots__ = ("max_chunk_size_tokens", "chunk_overlap_tokens", "encoding_name")
    MAX_CHUNK_SIZE_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CHUNK_OVERLAP_TOKENS_FIELD_NUMBER: _ClassVar[int]
    ENCODING_NAME_FIELD_NUMBER: _ClassVar[int]
    max_chunk_size_tokens: int
    chunk_overlap_tokens: int
    encoding_name: str
    def __init__(self, max_chunk_size_tokens: _Optional[int] = ..., chunk_overlap_tokens: _Optional[int] = ..., encoding_name: _Optional[str] = ...) -> None: ...

class BytesConfiguration(_message.Message):
    __slots__ = ("max_chunk_size_bytes", "chunk_overlap_bytes")
    MAX_CHUNK_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CHUNK_OVERLAP_BYTES_FIELD_NUMBER: _ClassVar[int]
    max_chunk_size_bytes: int
    chunk_overlap_bytes: int
    def __init__(self, max_chunk_size_bytes: _Optional[int] = ..., chunk_overlap_bytes: _Optional[int] = ...) -> None: ...
