import datetime
from typing import Literal, Optional, Union

import grpc
from pydantic import TypeAdapter
from typing_extensions import NotRequired, TypedDict

from .proto import (
    collections_pb2,
    collections_pb2_grpc,
    documents_pb2_grpc,
    files_pb2_grpc,
    shared_pb2,
    types_pb2,
)

Order = Literal["asc", "desc"]

CollectionSortBy = Literal["name", "age"]
DocumentSortBy = Literal["name", "age", "size"]
HNSWMetric = Literal["cosine", "euclidean", "inner_product"]
DocumentRetrievalMode = Literal["hybrid", "semantic", "keyword"]

DEFAULT_INDEXING_POLL_INTERVAL = datetime.timedelta(seconds=10)
DEFAULT_INDEXING_TIMEOUT = datetime.timedelta(minutes=2)


class FieldDefinition(TypedDict):
    """Definition of a field that can be attached to documents in a collection.

    Field definitions specify constraints and behaviors for document metadata:

    - key: The name of the field (e.g., "title", "author", "isbn")
    - required: If True, documents missing this field will be rejected at upload time
    - inject_into_chunk: If True, the field's value is prepended to each chunk for
      contextual retrieval, improving search accuracy
    - unique: If True, the field's value must be unique across all documents in the
      collection; duplicates will be rejected
    - description: Optional explanation of what this field represents
    """

    key: str
    required: bool
    inject_into_chunk: bool
    unique: bool
    description: NotRequired[str]


class FieldDefinitionAdd(TypedDict):
    """Add a field definition to a collection.

    - field_definition: The full field definition to add.
    - operation: Must be "add".
    """

    field_definition: FieldDefinition
    operation: Literal["add"]


class FieldDefinitionDelete(TypedDict):
    """Delete a field definition from a collection by key.

    Removes the field definition and the field's value from every document
    in the collection. Only the field's `key` is needed.

    - key: The key of the field definition to delete.
    - operation: Must be "delete".
    """

    key: str
    operation: Literal["delete"]


FieldDefinitionUpdate = Union[FieldDefinitionAdd, FieldDefinitionDelete]


class ChunkConfiguration(TypedDict, total=False):
    """Configuration for chunking documents.

    Note: You must specify exactly one of `chars_configuration`, `tokens_configuration`,
    or `bytes_configuration`.
    """

    chars_configuration: "CharsConfiguration"
    tokens_configuration: "TokensConfiguration"
    bytes_configuration: "BytesConfiguration"
    strip_whitespace: bool
    inject_name_into_chunks: bool


class CharsConfiguration(TypedDict):
    """Configuration for character-based chunking."""

    max_chunk_size_chars: int
    chunk_overlap_chars: int


class TokensConfiguration(TypedDict):
    """Configuration for token-based chunking."""

    max_chunk_size_tokens: int
    chunk_overlap_tokens: int
    encoding_name: str


class BytesConfiguration(TypedDict):
    """Configuration for byte-based chunking."""

    max_chunk_size_bytes: int
    chunk_overlap_bytes: int


# Create TypeAdapter instances for validation
FieldDefinitionValidator = TypeAdapter(FieldDefinition)
FieldDefinitionAddValidator = TypeAdapter(FieldDefinitionAdd)
FieldDefinitionDeleteValidator = TypeAdapter(FieldDefinitionDelete)
ChunkConfigurationValidator = TypeAdapter(ChunkConfiguration)


class BaseClient:
    """Base Client for interacting with the `Collections` API."""

    _documents_stub: documents_pb2_grpc.DocumentsStub
    _files_stub: files_pb2_grpc.FilesStub
    _management_api_channel: Optional[Union[grpc.Channel, grpc.aio.Channel]]

    def __init__(
        self,
        api_channel: Union[grpc.Channel, grpc.aio.Channel],
        management_api_channel: Optional[Union[grpc.Channel, grpc.aio.Channel]],
    ):
        """Creates a new client based on a gRPC channel."""
        self._documents_stub = documents_pb2_grpc.DocumentsStub(api_channel)
        self._files_stub = files_pb2_grpc.FilesStub(api_channel)
        self._management_api_channel = management_api_channel

    @property
    def _collections_stub(self) -> collections_pb2_grpc.CollectionsStub:
        if self._management_api_channel is None:
            raise ValueError("Please provide a management API key.")
        if not hasattr(self, "_cached_collections_stub"):
            self._cached_collections_stub = collections_pb2_grpc.CollectionsStub(self._management_api_channel)
        return self._cached_collections_stub


def _order_to_pb(order: Order | None) -> shared_pb2.Ordering:
    match order:
        case "asc":
            return shared_pb2.Ordering.ORDERING_ASCENDING
        case "desc":
            return shared_pb2.Ordering.ORDERING_DESCENDING
        case _:
            return shared_pb2.Ordering.ORDERING_UNKNOWN


def _collection_sort_by_to_pb(sort_by: CollectionSortBy | None) -> collections_pb2.CollectionsSortBy:
    match sort_by:
        case "name":
            return collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_NAME
        case "age":
            return collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_AGE
        case _:
            return collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_NAME


def _document_sort_by_to_pb(sort_by: DocumentSortBy | None) -> collections_pb2.DocumentsSortBy:
    match sort_by:
        case "name":
            return collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_NAME
        case "age":
            return collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_AGE
        case "size":
            return collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_SIZE
        case _:
            return collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_NAME


def _field_definition_to_pb(field_definition: FieldDefinition) -> collections_pb2.FieldDefinition:
    validated = FieldDefinitionValidator.validate_python(field_definition)
    return collections_pb2.FieldDefinition(**validated)


def _field_definition_update_to_pb(
    update: FieldDefinitionUpdate,
) -> collections_pb2.FieldDefinitionUpdate:
    op = update.get("operation")
    if op == "add":
        validated_add = FieldDefinitionAddValidator.validate_python(update)
        return collections_pb2.FieldDefinitionUpdate(
            field_definition=_field_definition_to_pb(validated_add["field_definition"]),
            operation=collections_pb2.FieldDefinitionOperation.FIELD_DEFINITION_ADD,
        )
    if op == "delete":
        validated_del = FieldDefinitionDeleteValidator.validate_python(update)
        return collections_pb2.FieldDefinitionUpdate(
            field_definition=collections_pb2.FieldDefinition(key=validated_del["key"]),
            operation=collections_pb2.FieldDefinitionOperation.FIELD_DEFINITION_DELETE,
        )
    raise ValueError(f"Unknown field definition operation: {op!r}. Expected 'add' or 'delete'.")


def _hnsw_metric_to_pb(metric: HNSWMetric) -> types_pb2.HNSWMetric:
    match metric:
        case "cosine":
            return types_pb2.HNSWMetric.HNSW_METRIC_COSINE
        case "euclidean":
            return types_pb2.HNSWMetric.HNSW_METRIC_EUCLIDEAN
        case "inner_product":
            return types_pb2.HNSWMetric.HNSW_METRIC_INNER_PRODUCT
        case _:
            return types_pb2.HNSWMetric.HNSW_METRIC_UNKNOWN


def _validate_chunk_configuration(chunk_config: ChunkConfiguration) -> None:
    """Validate that exactly one of chars_configuration, tokens_configuration, or bytes_configuration is set.

    Args:
        chunk_config: The chunk configuration dict to validate.

    Raises:
        ValueError: If zero or more than one chunking strategy is specified.
    """
    strategies = [
        key for key in ("chars_configuration", "tokens_configuration", "bytes_configuration") if chunk_config.get(key)
    ]

    if len(strategies) == 0:
        raise ValueError(
            "Must specify exactly one chunking strategy "
            "('chars_configuration', 'tokens_configuration', or 'bytes_configuration')."
        )

    if len(strategies) > 1:
        raise ValueError(
            f"Cannot specify multiple chunking strategies ({', '.join(repr(s) for s in strategies)}). "
            "Please specify only one chunking strategy."
        )


def _chunk_configuration_to_pb(chunk_config: ChunkConfiguration) -> types_pb2.ChunkConfiguration:
    """Convert ChunkConfiguration to protobuf with validation.

    Args:
        chunk_config: A dict containing chunk configuration.

    Returns:
        A protobuf ChunkConfiguration.

    Raises:
        ValueError: If zero or multiple chunking strategies are specified.
        pydantic.ValidationError: If the provided dict doesn't match the expected schema.
    """
    validated = ChunkConfigurationValidator.validate_python(chunk_config)
    _validate_chunk_configuration(validated)
    return types_pb2.ChunkConfiguration(**validated)
