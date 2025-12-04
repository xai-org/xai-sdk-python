from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RankingMetric(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANKING_METRIC_UNKNOWN: _ClassVar[RankingMetric]
    RANKING_METRIC_L2_DISTANCE: _ClassVar[RankingMetric]
    RANKING_METRIC_COSINE_SIMILARITY: _ClassVar[RankingMetric]
RANKING_METRIC_UNKNOWN: RankingMetric
RANKING_METRIC_L2_DISTANCE: RankingMetric
RANKING_METRIC_COSINE_SIMILARITY: RankingMetric

class HybridRetrieval(_message.Message):
    __slots__ = ("search_multiplier", "reranker_model", "reciprocal_rank_fusion")
    SEARCH_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    RERANKER_MODEL_FIELD_NUMBER: _ClassVar[int]
    RECIPROCAL_RANK_FUSION_FIELD_NUMBER: _ClassVar[int]
    search_multiplier: int
    reranker_model: RerankerModel
    reciprocal_rank_fusion: ReciprocalRankFusion
    def __init__(self, search_multiplier: _Optional[int] = ..., reranker_model: _Optional[_Union[RerankerModel, _Mapping]] = ..., reciprocal_rank_fusion: _Optional[_Union[ReciprocalRankFusion, _Mapping]] = ...) -> None: ...

class KeywordRetrieval(_message.Message):
    __slots__ = ("reranker",)
    RERANKER_FIELD_NUMBER: _ClassVar[int]
    reranker: RerankerModel
    def __init__(self, reranker: _Optional[_Union[RerankerModel, _Mapping]] = ...) -> None: ...

class SemanticRetrieval(_message.Message):
    __slots__ = ("reranker",)
    RERANKER_FIELD_NUMBER: _ClassVar[int]
    reranker: RerankerModel
    def __init__(self, reranker: _Optional[_Union[RerankerModel, _Mapping]] = ...) -> None: ...

class ReciprocalRankFusion(_message.Message):
    __slots__ = ("k", "embedding_weight", "text_weight")
    K_FIELD_NUMBER: _ClassVar[int]
    EMBEDDING_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    TEXT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    k: int
    embedding_weight: float
    text_weight: float
    def __init__(self, k: _Optional[int] = ..., embedding_weight: _Optional[float] = ..., text_weight: _Optional[float] = ...) -> None: ...

class RerankerModel(_message.Message):
    __slots__ = ("model", "instructions")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    model: str
    instructions: str
    def __init__(self, model: _Optional[str] = ..., instructions: _Optional[str] = ...) -> None: ...

class SearchRequest(_message.Message):
    __slots__ = ("query", "source", "limit", "instructions", "hybrid_retrieval", "semantic_retrieval", "keyword_retrieval", "ranking_metric")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    HYBRID_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    RANKING_METRIC_FIELD_NUMBER: _ClassVar[int]
    query: str
    source: DocumentsSource
    limit: int
    instructions: str
    hybrid_retrieval: HybridRetrieval
    semantic_retrieval: SemanticRetrieval
    keyword_retrieval: KeywordRetrieval
    ranking_metric: RankingMetric
    def __init__(self, query: _Optional[str] = ..., source: _Optional[_Union[DocumentsSource, _Mapping]] = ..., limit: _Optional[int] = ..., instructions: _Optional[str] = ..., hybrid_retrieval: _Optional[_Union[HybridRetrieval, _Mapping]] = ..., semantic_retrieval: _Optional[_Union[SemanticRetrieval, _Mapping]] = ..., keyword_retrieval: _Optional[_Union[KeywordRetrieval, _Mapping]] = ..., ranking_metric: _Optional[_Union[RankingMetric, str]] = ...) -> None: ...

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
