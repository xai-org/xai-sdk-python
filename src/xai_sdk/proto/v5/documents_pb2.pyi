from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RankingMetric(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANKING_METRIC_UNKNOWN: _ClassVar[RankingMetric]
    RANKING_METRIC_L2_DISTANCE: _ClassVar[RankingMetric]
    RANKING_METRIC_COSINE_SIMILARITY: _ClassVar[RankingMetric]
RANKING_METRIC_UNKNOWN: RankingMetric
RANKING_METRIC_L2_DISTANCE: RankingMetric
RANKING_METRIC_COSINE_SIMILARITY: RankingMetric

class SearchRequest(_message.Message):
    __slots__ = ("query", "source", "limit", "ranking_metric", "instructions")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    RANKING_METRIC_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    query: str
    source: DocumentsSource
    limit: int
    ranking_metric: RankingMetric
    instructions: str
    def __init__(self, query: _Optional[str] = ..., source: _Optional[_Union[DocumentsSource, _Mapping]] = ..., limit: _Optional[int] = ..., ranking_metric: _Optional[_Union[RankingMetric, str]] = ..., instructions: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("matches",)
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    matches: _containers.RepeatedCompositeFieldContainer[SearchMatch]
    def __init__(self, matches: _Optional[_Iterable[_Union[SearchMatch, _Mapping]]] = ...) -> None: ...

class SearchMatch(_message.Message):
    __slots__ = ("file_id", "chunk_id", "chunk_content", "score", "collection_ids")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_IDS_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    chunk_id: str
    chunk_content: str
    score: float
    collection_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, file_id: _Optional[str] = ..., chunk_id: _Optional[str] = ..., chunk_content: _Optional[str] = ..., score: _Optional[float] = ..., collection_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DocumentsSource(_message.Message):
    __slots__ = ("collection_ids",)
    COLLECTION_IDS_FIELD_NUMBER: _ClassVar[int]
    collection_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, collection_ids: _Optional[_Iterable[str]] = ...) -> None: ...
