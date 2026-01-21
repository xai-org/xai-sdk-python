import asyncio
import datetime
from typing import Optional, Sequence, Union

from opentelemetry.trace import SpanKind

from ..collections import (
    DEFAULT_INDEXING_POLL_INTERVAL,
    DEFAULT_INDEXING_TIMEOUT,
    BaseClient,
    ChunkConfiguration,
    CollectionSortBy,
    DocumentRetrievalMode,
    DocumentSortBy,
    FieldDefinition,
    HNSWMetric,
    Order,
    _chunk_configuration_to_pb,
    _collection_sort_by_to_pb,
    _document_sort_by_to_pb,
    _field_definition_to_pb,
    _hnsw_metric_to_pb,
    _order_to_pb,
)
from ..files import _async_chunk_file_data
from ..poll_timer import PollTimer
from ..proto import collections_pb2, documents_pb2, shared_pb2, types_pb2
from ..telemetry import get_tracer

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Async Client for interacting with the `Collections` API."""

    async def create(
        self,
        name: str,
        model_name: Optional[str] = None,
        chunk_configuration: Optional[Union[ChunkConfiguration, types_pb2.ChunkConfiguration]] = None,
        metric_space: Optional[Union[HNSWMetric, "types_pb2.HNSWMetric"]] = None,
        field_definitions: Optional[Union[Sequence[FieldDefinition], Sequence[collections_pb2.FieldDefinition]]] = None,
    ) -> collections_pb2.CollectionMetadata:
        """Creates a new collection for storing document embeddings.

        Args:
            name: The name of the collection.
            model_name: The name of the model to use for embedding. If not provided, the default model will be used.
            chunk_configuration: The configuration for chunking documents.
                If not provided, the default chunk configuration will be used.
            metric_space: The distance metric to use for the HNSW (Hierarchical Navigable Small Worlds) index
                and similarity search. Options: COSINE, EUCLIDEAN, or INNER_PRODUCT.
            field_definitions: Schema definitions for custom metadata fields that can be attached to documents.
                Each field definition specifies: `key` (field name), `required` (must be present on all
                documents), `inject_into_chunk` (prepend field value to each chunk for contextual retrieval),
                `unique` (value must be unique across all documents), and `description` (optional explanation).
                Example: [{"key": "title", "required": True, "inject_into_chunk": True, "unique": False}]

        Returns:
            The metadata for the created collection.
        """
        metric_space_pb: Optional[types_pb2.HNSWMetric] = None
        if isinstance(metric_space, str):
            metric_space_pb = _hnsw_metric_to_pb(metric_space)
        else:
            metric_space_pb = metric_space

        chunk_configuration_pb: Optional[types_pb2.ChunkConfiguration] = None
        if isinstance(chunk_configuration, dict):
            chunk_configuration_pb = _chunk_configuration_to_pb(chunk_configuration)
        else:
            chunk_configuration_pb = chunk_configuration

        field_definitions_pb: Sequence[collections_pb2.FieldDefinition] = []
        if field_definitions is not None:
            for field_definition in field_definitions:
                if isinstance(field_definition, dict):
                    field_definitions_pb.append(_field_definition_to_pb(field_definition))
                else:
                    field_definitions_pb.append(field_definition)

        with tracer.start_as_current_span(
            name="collections.create_collection",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "create_collection",
                "provider.name": "xai",
            },
        ) as span:
            collection = await self._collections_stub.CreateCollection(
                collections_pb2.CreateCollectionRequest(
                    collection_name=name,
                    index_configuration=types_pb2.IndexConfiguration(model_name=model_name) if model_name else None,
                    chunk_configuration=chunk_configuration_pb,
                    metric_space=metric_space_pb,
                    field_definitions=field_definitions_pb,
                )
            )
            span.set_attribute("collection.id", collection.collection_id)
            span.set_attribute("collection.name", collection.collection_name)
            return collection

    async def list(
        self,
        limit: Optional[int] = None,
        order: Optional[Union[Order, "shared_pb2.Ordering"]] = None,
        sort_by: Optional[Union[CollectionSortBy, "collections_pb2.CollectionsSortBy"]] = None,
        filter: Optional[str] = None,  # noqa: A002
        pagination_token: Optional[str] = None,
    ) -> collections_pb2.ListCollectionsResponse:
        """Lists all collections.

        Args:
            limit: The maximum number of collections to return per page. Maximum 100 items per request.
                Uses server default if not provided.
            order: The ordering direction for results. Options: "asc" (ascending) or "desc" (descending).
                If not provided, defaults to "desc".
            sort_by: The field to sort collections by. Options: "name" or "age".
                If not provided, defaults to "name".
            filter: Filter expression to narrow down results. Supports filtering on: collection_name,
                created_at, documents_count. Examples:
                - 'collection_name:"SEC" AND documents_count:>10'
                - 'created_at:>2025-01-01T00:00:00Z'
            pagination_token: Token to retrieve the next page. Provided by `pagination_token` in the
                previous `ListCollectionsResponse`.

        Returns:
            A response containing a list of collection metadata and an optional pagination token for
            retrieving the next page of results.
        """
        order_pb: Optional[shared_pb2.Ordering] = None
        if isinstance(order, str):
            order_pb = _order_to_pb(order)
        else:
            order_pb = order

        sort_by_pb: Optional[collections_pb2.CollectionsSortBy] = None
        if isinstance(sort_by, str):
            sort_by_pb = _collection_sort_by_to_pb(sort_by)
        else:
            sort_by_pb = sort_by

        return await self._collections_stub.ListCollections(
            collections_pb2.ListCollectionsRequest(
                limit=limit, order=order_pb, sort_by=sort_by_pb, pagination_token=pagination_token, filter=filter
            )
        )

    async def get(self, collection_id: str) -> collections_pb2.CollectionMetadata:
        """Gets the metadata for a collection.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            The metadata for the collection.
        """
        return await self._collections_stub.GetCollectionMetadata(
            collections_pb2.GetCollectionMetadataRequest(collection_id=collection_id)
        )

    async def update(
        self,
        collection_id: str,
        name: Optional[str] = None,
        chunk_configuration: Optional[Union[ChunkConfiguration, types_pb2.ChunkConfiguration]] = None,
    ) -> collections_pb2.CollectionMetadata:
        """Updates a collection's configuration.

        Args:
            collection_id: The ID of the collection to update.
            name: The new name of the collection.
            chunk_configuration: The new chunk configuration for the collection.

        Returns:
            The updated metadata for the collection.
        """
        if name is None and chunk_configuration is None:
            raise ValueError("At least one of name or chunk_configuration must be provided to update a collection")

        chunk_configuration_pb: Optional[types_pb2.ChunkConfiguration] = None
        if isinstance(chunk_configuration, dict):
            chunk_configuration_pb = _chunk_configuration_to_pb(chunk_configuration)
        else:
            chunk_configuration_pb = chunk_configuration
        with tracer.start_as_current_span(
            name="collections.update_collection",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "update_collection",
                "provider.name": "xai",
            },
        ) as span:
            collection = await self._collections_stub.UpdateCollection(
                collections_pb2.UpdateCollectionRequest(
                    collection_id=collection_id,
                    collection_name=name,
                    chunk_configuration=chunk_configuration_pb,
                )
            )
            span.set_attribute("collection.id", collection.collection_id)
            span.set_attribute("collection.name", collection.collection_name)
            return collection

    async def delete(self, collection_id: str) -> None:
        """Deletes a collection.

        Args:
            collection_id: The ID of the collection to delete.
        """
        with tracer.start_as_current_span(
            name="collections.delete_collection",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "delete_collection",
                "provider.name": "xai",
            },
        ) as _span:
            return await self._collections_stub.DeleteCollection(
                collections_pb2.DeleteCollectionRequest(collection_id=collection_id)
            )

    async def search(
        self,
        query: str,
        collection_ids: Sequence[str],
        limit: Optional[int] = None,
        *,
        instructions: Optional[str] = None,
        retrieval_mode: Optional[
            Union[
                DocumentRetrievalMode,
                documents_pb2.HybridRetrieval,
                documents_pb2.SemanticRetrieval,
                documents_pb2.KeywordRetrieval,
            ]
        ] = None,
    ) -> documents_pb2.SearchResponse:
        """Performs a search across all documents in the provided set of collections.

        Args:
            query: The search query to use for the semantic or keyword search.
            collection_ids: The IDs of the collections to search in.
            limit: The maximum number of results to return. Uses server default if not provided.
            instructions: Optional, user-defined instructions that guide how the search
                should be interpreted and ranked. If not provided, the server will use
                its default generic search instructions.
            retrieval_mode: Optional retrieval strategy to use for the search. When
                omitted, the server defaults to hybrid retrieval. Valid values are:
                - "hybrid" or documents_pb2.HybridRetrieval(): Use hybrid retrieval.
                - "semantic" or documents_pb2.SemanticRetrieval(): Use semantic retrieval.
                - "keyword" or documents_pb2.KeywordRetrieval(): Use keyword-based retrieval.

        Returns:
            A SearchResponse object containing the search results.
        """
        search_request_kwargs: dict = {
            "query": query,
            "source": documents_pb2.DocumentsSource(collection_ids=collection_ids),
        }

        if limit is not None:
            search_request_kwargs["limit"] = limit

        if instructions is not None:
            search_request_kwargs["instructions"] = instructions

        if retrieval_mode is not None:
            match retrieval_mode:
                case "hybrid" | documents_pb2.HybridRetrieval():
                    search_request_kwargs["hybrid_retrieval"] = (
                        retrieval_mode
                        if isinstance(retrieval_mode, documents_pb2.HybridRetrieval)
                        else documents_pb2.HybridRetrieval()
                    )
                case "semantic" | documents_pb2.SemanticRetrieval():
                    search_request_kwargs["semantic_retrieval"] = (
                        retrieval_mode
                        if isinstance(retrieval_mode, documents_pb2.SemanticRetrieval)
                        else documents_pb2.SemanticRetrieval()
                    )
                case "keyword" | documents_pb2.KeywordRetrieval():
                    search_request_kwargs["keyword_retrieval"] = (
                        retrieval_mode
                        if isinstance(retrieval_mode, documents_pb2.KeywordRetrieval)
                        else documents_pb2.KeywordRetrieval()
                    )
                case _:
                    raise ValueError(
                        f"Unsupported retrieval_mode {retrieval_mode!r}. Expected 'hybrid', 'semantic', 'keyword', "
                        "or a proto retrieval type."
                    )

        return await self._documents_stub.Search(documents_pb2.SearchRequest(**search_request_kwargs))

    async def upload_document(
        self,
        collection_id: str,
        name: str,
        data: bytes,
        fields: Optional[dict[str, str]] = None,
        *,
        wait_for_indexing: bool = False,
        poll_interval: Optional[datetime.timedelta] = None,
        timeout: Optional[datetime.timedelta] = None,
    ) -> collections_pb2.DocumentMetadata:
        """Uploads a document to a collection.

        Args:
            collection_id: The ID of the collection to upload the document to.
            name: The name of the document.
            data: The data of the document.
            fields: Additional metadata fields to store with the document.
            wait_for_indexing: Whether to wait for the document to be indexed.
            poll_interval: The interval to poll for when checking whether the document has been indexed.
            timeout: The total time to wait for the document to be indexed before returning.

        Returns:
            The metadata for the uploaded document.
        """
        # Upload the raw bytes via the streaming Files API, then attach to the collection.
        upload_chunks = _async_chunk_file_data(filename=name, data=data)
        with tracer.start_as_current_span(
            name="collections.upload_document",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "upload_document",
                "provider.name": "xai",
            },
        ) as span:
            uploaded_file = await self._files_stub.UploadFile(upload_chunks)
            span.set_attribute("file.id", uploaded_file.id)
            span.set_attribute("file.name", uploaded_file.filename)

        # Attach the uploaded file to the target collection as a document.
        await self._collections_stub.AddDocumentToCollection(
            collections_pb2.AddDocumentToCollectionRequest(
                collection_id=collection_id,
                file_id=uploaded_file.id,
                fields=fields,
            )
        )

        # Either wait for indexing to complete or return the current metadata.
        if wait_for_indexing:
            return await self._wait_for_indexing(
                collection_id,
                uploaded_file.id,
                poll_interval or DEFAULT_INDEXING_POLL_INTERVAL,
                timeout or DEFAULT_INDEXING_TIMEOUT,
            )

        return await self.get_document(
            uploaded_file.id,
            collection_id,
        )

    async def _wait_for_indexing(
        self,
        collection_id: str,
        file_id: str,
        poll_interval: datetime.timedelta,
        timeout: datetime.timedelta,
    ) -> collections_pb2.DocumentMetadata:
        """Waits for a document to be indexed.

        Args:
            collection_id: The ID of the collection containing the document.
            file_id: The ID of the document to wait for.
            poll_interval: The interval to poll for when checking whether the document has been indexed.
            timeout: The total time to wait for the document to be indexed before returning.

        Returns:
            The metadata for the document.

        Raises:
            ValueError: If the document indexing fails.
            ValueError: If the document status is unknown.
            TimeoutError: If polling times out before document is processed.
        """
        timer = PollTimer(timeout, poll_interval)
        while True:
            document_metadata = await self.get_document(
                file_id,
                collection_id,
            )
            match document_metadata.status:
                case collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED:
                    return document_metadata
                case collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSING:
                    await asyncio.sleep(timer.sleep_interval_or_raise())
                case collections_pb2.DocumentStatus.DOCUMENT_STATUS_FAILED:
                    raise ValueError(f"Document indexing failed: {document_metadata.error_message}")
                case unknown_status:
                    raise ValueError(f"Unknown document status: {unknown_status}")

    async def add_existing_document(
        self,
        collection_id: str,
        file_id: str,
        fields: Optional[dict[str, str]] = None,
    ) -> None:
        """Adds an existing document to a collection.

        Args:
            collection_id: The ID of the collection to add the document to.
            file_id: The ID of the file (document) to add.
            fields: Additional metadata fields to store with the document in this collection.
        """
        with tracer.start_as_current_span(
            name="collections.add_existing_document",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "add_existing_document",
                "provider.name": "xai",
            },
        ) as _span:
            await self._collections_stub.AddDocumentToCollection(
                collections_pb2.AddDocumentToCollectionRequest(
                    collection_id=collection_id,
                    file_id=file_id,
                    fields=fields,
                )
            )

    async def list_documents(
        self,
        collection_id: str,
        limit: Optional[int] = None,
        order: Optional[Union[Order, "shared_pb2.Ordering"]] = None,
        sort_by: Optional[Union[DocumentSortBy, "collections_pb2.DocumentsSortBy"]] = None,
        pagination_token: Optional[str] = None,
    ) -> collections_pb2.ListDocumentsResponse:
        """Lists all documents in a collection.

        Args:
            collection_id: The ID of the collection to list the documents from.
            limit: The maximum number of documents to return per page. Uses server default if not provided.
            order: The order in which to return the documents.
            sort_by: The field to sort the documents by.
            pagination_token: The token to use for pagination.

        Returns:
            A list of documents.
        """
        order_pb: Optional[shared_pb2.Ordering] = None
        if isinstance(order, str):
            order_pb = _order_to_pb(order)
        else:
            order_pb = order

        sort_by_pb: Optional[collections_pb2.DocumentsSortBy] = None
        if isinstance(sort_by, str):
            sort_by_pb = _document_sort_by_to_pb(sort_by)
        else:
            sort_by_pb = sort_by

        return await self._collections_stub.ListDocuments(
            collections_pb2.ListDocumentsRequest(
                collection_id=collection_id,
                limit=limit,
                order=order_pb,
                sort_by=sort_by_pb,
                pagination_token=pagination_token,
            )
        )

    async def get_document(self, file_id: str, collection_id: str) -> collections_pb2.DocumentMetadata:
        """Gets the metadata for a document.

        Args:
            file_id: The ID of the file (document) to get.
            collection_id: The ID of the collection containing the document.

        Returns:
            The metadata for the document.
        """
        return await self._collections_stub.GetDocumentMetadata(
            collections_pb2.GetDocumentMetadataRequest(file_id=file_id, collection_id=collection_id)
        )

    async def batch_get_documents(
        self,
        collection_id: str,
        file_ids: Sequence[str],
    ) -> collections_pb2.BatchGetDocumentsResponse:
        """Gets metadata for multiple documents in batch.

        Args:
            collection_id: The ID of the collection containing the documents.
            file_ids: The IDs of the documents to retrieve metadata for.

        Returns:
            A batch response containing metadata for all requested documents.
        """
        return await self._collections_stub.BatchGetDocuments(
            collections_pb2.BatchGetDocumentsRequest(
                collection_id=collection_id,
                file_ids=file_ids,
            )
        )

    async def remove_document(self, collection_id: str, file_id: str) -> None:
        """Removes a document from a collection.

        Args:
            collection_id: The ID of the collection to remove the document from.
            file_id: The ID of the file (document) to remove.
        """
        with tracer.start_as_current_span(
            name="collections.remove_document",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "remove_document",
                "provider.name": "xai",
            },
        ) as _span:
            return await self._collections_stub.RemoveDocumentFromCollection(
                collections_pb2.RemoveDocumentFromCollectionRequest(collection_id=collection_id, file_id=file_id)
            )

    async def update_document(
        self,
        collection_id: str,
        file_id: str,
        name: Optional[str] = None,
        data: Optional[bytes] = None,
        content_type: Optional[str] = None,
        fields: Optional[dict[str, str]] = None,
    ) -> collections_pb2.DocumentMetadata:
        """Updates a document's data and metadata.

        Args:
            collection_id: The ID of the collection containing the document.
            file_id: The ID of the document to update.
            name: The new name of the document.
            data: The new data of the document.
            content_type: The new content type of the document.
            fields: Additional metadata fields to update.

        Returns:
            The updated metadata for the document.
        """
        with tracer.start_as_current_span(
            name="collections.update_document",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "update_document",
                "provider.name": "xai",
            },
        ) as span:
            document = await self._collections_stub.UpdateDocument(
                collections_pb2.UpdateDocumentRequest(
                    collection_id=collection_id,
                    file_id=file_id,
                    name=name,
                    data=data,
                    content_type=content_type,
                    fields=fields,
                )
            )
            span.set_attribute("document.id", document.file_metadata.file_id)
            span.set_attribute("document.name", document.file_metadata.name)
            return document

    async def reindex_document(self, collection_id: str, file_id: str) -> None:
        """Regenerates indices for a document.

        Use this method when you have updated the configuration of a collection and wish to
        re-index existing documents with the new configuration.

        Args:
            collection_id: The ID of the collection containing the document.
            file_id: The ID of the document to reindex.
        """
        return await self._collections_stub.ReIndexDocument(
            collections_pb2.ReIndexDocumentRequest(
                collection_id=collection_id,
                file_id=file_id,
            )
        )
