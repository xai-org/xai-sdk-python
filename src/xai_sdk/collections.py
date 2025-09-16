from typing import Literal, Optional, Union

import grpc

from .proto import collections_pb2, collections_pb2_grpc, documents_pb2_grpc, shared_pb2

Order = Literal["asc", "desc"]

CollectionSortBy = Literal["name", "age"]
DocumentSortBy = Literal["name", "age", "size"]


class BaseClient:
    """Base Client for interacting with the `Collections` API."""

    _documents_stub: documents_pb2_grpc.DocumentsStub
    _management_api_channel: Optional[Union[grpc.Channel, grpc.aio.Channel]]

    def __init__(
        self,
        api_channel: Union[grpc.Channel, grpc.aio.Channel],
        management_api_channel: Optional[Union[grpc.Channel, grpc.aio.Channel]],
    ):
        """Creates a new client based on a gRPC channel."""
        self._documents_stub = documents_pb2_grpc.DocumentsStub(api_channel)
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
