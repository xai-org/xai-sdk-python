from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import shared_pb2 as _shared_pb2
from . import types_pb2 as _types_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CollectionsSortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COLLECTIONS_SORT_BY_NAME: _ClassVar[CollectionsSortBy]
    COLLECTIONS_SORT_BY_AGE: _ClassVar[CollectionsSortBy]

class DocumentsSortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOCUMENTS_SORT_BY_NAME: _ClassVar[DocumentsSortBy]
    DOCUMENTS_SORT_BY_SIZE: _ClassVar[DocumentsSortBy]
    DOCUMENTS_SORT_BY_AGE: _ClassVar[DocumentsSortBy]

class DocumentStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOCUMENT_STATUS_UNKNOWN: _ClassVar[DocumentStatus]
    DOCUMENT_STATUS_PROCESSING: _ClassVar[DocumentStatus]
    DOCUMENT_STATUS_PROCESSED: _ClassVar[DocumentStatus]
    DOCUMENT_STATUS_FAILED: _ClassVar[DocumentStatus]
COLLECTIONS_SORT_BY_NAME: CollectionsSortBy
COLLECTIONS_SORT_BY_AGE: CollectionsSortBy
DOCUMENTS_SORT_BY_NAME: DocumentsSortBy
DOCUMENTS_SORT_BY_SIZE: DocumentsSortBy
DOCUMENTS_SORT_BY_AGE: DocumentsSortBy
DOCUMENT_STATUS_UNKNOWN: DocumentStatus
DOCUMENT_STATUS_PROCESSING: DocumentStatus
DOCUMENT_STATUS_PROCESSED: DocumentStatus
DOCUMENT_STATUS_FAILED: DocumentStatus

class FieldDefinition(_message.Message):
    __slots__ = ("key", "required", "inject_into_chunk", "unique", "description")
    KEY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    INJECT_INTO_CHUNK_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    key: str
    required: bool
    inject_into_chunk: bool
    unique: bool
    description: str
    def __init__(self, key: _Optional[str] = ..., required: bool = ..., inject_into_chunk: bool = ..., unique: bool = ..., description: _Optional[str] = ...) -> None: ...

class CreateCollectionRequest(_message.Message):
    __slots__ = ("team_id", "collection_name", "index_configuration", "chunk_configuration", "metric_space", "field_definitions")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    INDEX_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    METRIC_SPACE_FIELD_NUMBER: _ClassVar[int]
    FIELD_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_name: str
    index_configuration: _types_pb2.IndexConfiguration
    chunk_configuration: _types_pb2.ChunkConfiguration
    metric_space: _types_pb2.HNSWMetric
    field_definitions: _containers.RepeatedCompositeFieldContainer[FieldDefinition]
    def __init__(self, team_id: _Optional[str] = ..., collection_name: _Optional[str] = ..., index_configuration: _Optional[_Union[_types_pb2.IndexConfiguration, _Mapping]] = ..., chunk_configuration: _Optional[_Union[_types_pb2.ChunkConfiguration, _Mapping]] = ..., metric_space: _Optional[_Union[_types_pb2.HNSWMetric, str]] = ..., field_definitions: _Optional[_Iterable[_Union[FieldDefinition, _Mapping]]] = ...) -> None: ...

class CollectionMetadata(_message.Message):
    __slots__ = ("collection_id", "collection_name", "created_at", "index_configuration", "chunk_configuration", "documents_count", "field_definitions")
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    INDEX_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    FIELD_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    collection_id: str
    collection_name: str
    created_at: _timestamp_pb2.Timestamp
    index_configuration: _types_pb2.IndexConfiguration
    chunk_configuration: _types_pb2.ChunkConfiguration
    documents_count: int
    field_definitions: _containers.RepeatedCompositeFieldContainer[FieldDefinition]
    def __init__(self, collection_id: _Optional[str] = ..., collection_name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., index_configuration: _Optional[_Union[_types_pb2.IndexConfiguration, _Mapping]] = ..., chunk_configuration: _Optional[_Union[_types_pb2.ChunkConfiguration, _Mapping]] = ..., documents_count: _Optional[int] = ..., field_definitions: _Optional[_Iterable[_Union[FieldDefinition, _Mapping]]] = ...) -> None: ...

class ListCollectionsRequest(_message.Message):
    __slots__ = ("team_id", "limit", "order", "sort_by", "pagination_token", "filter")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    limit: int
    order: _shared_pb2.Ordering
    sort_by: CollectionsSortBy
    pagination_token: str
    filter: str
    def __init__(self, team_id: _Optional[str] = ..., limit: _Optional[int] = ..., order: _Optional[_Union[_shared_pb2.Ordering, str]] = ..., sort_by: _Optional[_Union[CollectionsSortBy, str]] = ..., pagination_token: _Optional[str] = ..., filter: _Optional[str] = ...) -> None: ...

class ListCollectionsResponse(_message.Message):
    __slots__ = ("collections", "pagination_token")
    COLLECTIONS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    collections: _containers.RepeatedCompositeFieldContainer[CollectionMetadata]
    pagination_token: str
    def __init__(self, collections: _Optional[_Iterable[_Union[CollectionMetadata, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class DeleteCollectionRequest(_message.Message):
    __slots__ = ("team_id", "collection_id")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ...) -> None: ...

class GetCollectionMetadataRequest(_message.Message):
    __slots__ = ("team_id", "collection_id")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ...) -> None: ...

class ListAvailableEmbeddingModelsRequest(_message.Message):
    __slots__ = ("team_id",)
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    def __init__(self, team_id: _Optional[str] = ...) -> None: ...

class ListAvailableEmbeddingModelsResponse(_message.Message):
    __slots__ = ("embedding_models",)
    EMBEDDING_MODELS_FIELD_NUMBER: _ClassVar[int]
    embedding_models: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, embedding_models: _Optional[_Iterable[str]] = ...) -> None: ...

class ListAvailableTokenEncodingsRequest(_message.Message):
    __slots__ = ("team_id",)
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    def __init__(self, team_id: _Optional[str] = ...) -> None: ...

class ListAvailableTokenEncodingsResponse(_message.Message):
    __slots__ = ("encodings",)
    ENCODINGS_FIELD_NUMBER: _ClassVar[int]
    encodings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, encodings: _Optional[_Iterable[str]] = ...) -> None: ...

class UploadDocumentRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "name", "data", "content_type", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    name: str
    data: bytes
    content_type: str
    fields: _containers.ScalarMap[str, str]
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., name: _Optional[str] = ..., data: _Optional[bytes] = ..., content_type: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FileMetadata(_message.Message):
    __slots__ = ("file_id", "name", "size_bytes", "content_type", "created_at", "expires_at", "hash", "upload_status", "upload_error_message")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_STATUS_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    name: str
    size_bytes: int
    content_type: str
    created_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    hash: str
    upload_status: str
    upload_error_message: str
    def __init__(self, file_id: _Optional[str] = ..., name: _Optional[str] = ..., size_bytes: _Optional[int] = ..., content_type: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., hash: _Optional[str] = ..., upload_status: _Optional[str] = ..., upload_error_message: _Optional[str] = ...) -> None: ...

class DocumentMetadata(_message.Message):
    __slots__ = ("file_metadata", "fields", "status", "error_message")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FILE_METADATA_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    file_metadata: FileMetadata
    fields: _containers.ScalarMap[str, str]
    status: DocumentStatus
    error_message: str
    def __init__(self, file_metadata: _Optional[_Union[FileMetadata, _Mapping]] = ..., fields: _Optional[_Mapping[str, str]] = ..., status: _Optional[_Union[DocumentStatus, str]] = ..., error_message: _Optional[str] = ...) -> None: ...

class ListDocumentsRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "limit", "order", "sort_by", "pagination_token", "name", "filter")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    limit: int
    order: _shared_pb2.Ordering
    sort_by: DocumentsSortBy
    pagination_token: str
    name: str
    filter: str
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., limit: _Optional[int] = ..., order: _Optional[_Union[_shared_pb2.Ordering, str]] = ..., sort_by: _Optional[_Union[DocumentsSortBy, str]] = ..., pagination_token: _Optional[str] = ..., name: _Optional[str] = ..., filter: _Optional[str] = ...) -> None: ...

class ListDocumentsResponse(_message.Message):
    __slots__ = ("documents", "pagination_token")
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    documents: _containers.RepeatedCompositeFieldContainer[DocumentMetadata]
    pagination_token: str
    def __init__(self, documents: _Optional[_Iterable[_Union[DocumentMetadata, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class GetDocumentMetadataRequest(_message.Message):
    __slots__ = ("file_id", "collection_id", "team_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    collection_id: str
    team_id: str
    def __init__(self, file_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., team_id: _Optional[str] = ...) -> None: ...

class AddDocumentToCollectionRequest(_message.Message):
    __slots__ = ("file_id", "team_id", "collection_id", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    team_id: str
    collection_id: str
    fields: _containers.ScalarMap[str, str]
    def __init__(self, file_id: _Optional[str] = ..., team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RemoveDocumentFromCollectionRequest(_message.Message):
    __slots__ = ("file_id", "team_id", "collection_id")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    team_id: str
    collection_id: str
    def __init__(self, file_id: _Optional[str] = ..., team_id: _Optional[str] = ..., collection_id: _Optional[str] = ...) -> None: ...

class UpdateDocumentRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "file_id", "name", "data", "content_type", "fields")
    class FieldsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    file_id: str
    name: str
    data: bytes
    content_type: str
    fields: _containers.ScalarMap[str, str]
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., file_id: _Optional[str] = ..., name: _Optional[str] = ..., data: _Optional[bytes] = ..., content_type: _Optional[str] = ..., fields: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ReIndexDocumentRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "file_id")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    file_id: str
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., file_id: _Optional[str] = ...) -> None: ...

class UpdateCollectionRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "collection_name", "chunk_configuration")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    collection_name: str
    chunk_configuration: _types_pb2.ChunkConfiguration
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., collection_name: _Optional[str] = ..., chunk_configuration: _Optional[_Union[_types_pb2.ChunkConfiguration, _Mapping]] = ...) -> None: ...

class BatchGetDocumentsRequest(_message.Message):
    __slots__ = ("team_id", "collection_id", "file_ids")
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_IDS_FIELD_NUMBER: _ClassVar[int]
    team_id: str
    collection_id: str
    file_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, team_id: _Optional[str] = ..., collection_id: _Optional[str] = ..., file_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class BatchGetDocumentsResponse(_message.Message):
    __slots__ = ("documents",)
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    documents: _containers.RepeatedCompositeFieldContainer[DocumentMetadata]
    def __init__(self, documents: _Optional[_Iterable[_Union[DocumentMetadata, _Mapping]]] = ...) -> None: ...
