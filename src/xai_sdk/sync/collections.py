from typing import Optional, Sequence, Union

from ..collections import (
    BaseClient,
    CollectionSortBy,
    DocumentSortBy,
    Order,
    _collection_sort_by_to_pb,
    _document_sort_by_to_pb,
    _order_to_pb,
)
from ..proto import collections_pb2, documents_pb2, shared_pb2, types_pb2


class Client(BaseClient):
    """Sync Client for interacting with the `Collections` API."""

    def create(
        self,
        name: str,
        model_name: Optional[str] = None,
        chunk_configuration: Optional[types_pb2.ChunkConfiguration] = None,
    ) -> collections_pb2.CollectionMetadata:
        """Creates a new collection for storing document embeddings.

        Args:
            name: The name of the collection.
            model_name: The name of the model to use for embedding. If not provided, the default model will be used.
            chunk_configuration: The configuration for chunking documents.
                If not provided, the default chunk configuration will be used.

        Returns:
            The metadata for the created collection.
        """
        return self._collections_stub.CreateCollection(
            collections_pb2.CreateCollectionRequest(
                collection_name=name,
                index_configuration=types_pb2.IndexConfiguration(model_name=model_name) if model_name else None,
                chunk_configuration=chunk_configuration,
            )
        )

    def list(
        self,
        limit: Optional[int] = None,
        order: Optional[Union[Order, "shared_pb2.Ordering"]] = None,
        sort_by: Optional[Union[CollectionSortBy, "collections_pb2.CollectionsSortBy"]] = None,
        pagination_token: Optional[str] = None,
    ) -> collections_pb2.ListCollectionsResponse:
        """Lists all collections.

        Args:
            limit: The maximum number of collections to return per page.
            order: The order in which to return the collections.
            sort_by: The field to sort the collections by.
            pagination_token: The token to use for pagination.

        Returns:
            A list of collections.
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

        return self._collections_stub.ListCollections(
            collections_pb2.ListCollectionsRequest(
                limit=limit, order=order_pb, sort_by=sort_by_pb, pagination_token=pagination_token
            )
        )

    def get(self, collection_id: str) -> collections_pb2.CollectionMetadata:
        """Gets the metadata for a collection.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            The metadata for the collection.
        """
        return self._collections_stub.GetCollectionMetadata(
            collections_pb2.GetCollectionMetadataRequest(collection_id=collection_id)
        )

    def update(
        self,
        collection_id: str,
        name: Optional[str] = None,
        chunk_configuration: Optional[types_pb2.ChunkConfiguration] = None,
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

        return self._collections_stub.UpdateCollection(
            collections_pb2.UpdateCollectionRequest(
                collection_id=collection_id,
                collection_name=name,
                chunk_configuration=chunk_configuration,
            )
        )

    def delete(self, collection_id: str) -> None:
        """Deletes a collection.

        Args:
            collection_id: The ID of the collection to delete.
        """
        return self._collections_stub.DeleteCollection(
            collections_pb2.DeleteCollectionRequest(collection_id=collection_id)
        )

    def search(
        self,
        query: str,
        collection_ids: Sequence[str],
        limit: Optional[int] = None,
    ) -> documents_pb2.SearchResponse:
        """Performs a semantic, embedding-based search across all documents in the provided set of collections.

        Args:
            query: The search query to use for the semantic search.
            collection_ids: The IDs of the collections to search in.
            limit: The maximum number of results to return.

        Returns:
            A SearchResponse object containing the search results.
        """
        return self._documents_stub.Search(
            documents_pb2.SearchRequest(
                query=query, source=documents_pb2.DocumentsSource(collection_ids=collection_ids), limit=limit
            )
        )

    def upload_document(
        self,
        collection_id: str,
        name: str,
        data: bytes,
        content_type: str,
        fields: Optional[dict[str, str]] = None,
    ) -> collections_pb2.DocumentMetadata:
        """Uploads a document to a collection.

        Args:
            collection_id: The ID of the collection to upload the document to.
            name: The name of the document.
            data: The data of the document.
            content_type: The content type of the document.
            fields: Additional metadata fields to store with the document.

        Returns:
            The metadata for the uploaded document.
        """
        return self._collections_stub.UploadDocument(
            collections_pb2.UploadDocumentRequest(
                collection_id=collection_id,
                name=name,
                data=data,
                content_type=content_type,
                fields=fields,
            )
        )

    def add_existing_document(
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
        return self._collections_stub.AddDocumentToCollection(
            collections_pb2.AddDocumentToCollectionRequest(
                collection_id=collection_id,
                file_id=file_id,
                fields=fields,
            )
        )

    def list_documents(
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
            limit: The maximum number of documents to return per page.
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

        return self._collections_stub.ListDocuments(
            collections_pb2.ListDocumentsRequest(
                collection_id=collection_id,
                limit=limit,
                order=order_pb,
                sort_by=sort_by_pb,
                pagination_token=pagination_token,
            )
        )

    def get_document(self, file_id: str, collection_id: str) -> collections_pb2.DocumentMetadata:
        """Gets the metadata for a document.

        Args:
            file_id: The ID of the file (document) to get.
            collection_id: The ID of the collection containing the document.

        Returns:
            The metadata for the document.
        """
        return self._collections_stub.GetDocumentMetadata(
            collections_pb2.GetDocumentMetadataRequest(file_id=file_id, collection_id=collection_id)
        )

    def batch_get_documents(
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
        return self._collections_stub.BatchGetDocuments(
            collections_pb2.BatchGetDocumentsRequest(
                collection_id=collection_id,
                file_ids=file_ids,
            )
        )

    def remove_document(self, collection_id: str, file_id: str) -> None:
        """Removes a document from a collection.

        Args:
            collection_id: The ID of the collection to remove the document from.
            file_id: The ID of the file (document) to remove.
        """
        return self._collections_stub.RemoveDocumentFromCollection(
            collections_pb2.RemoveDocumentFromCollectionRequest(collection_id=collection_id, file_id=file_id)
        )

    def update_document(
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
        return self._collections_stub.UpdateDocument(
            collections_pb2.UpdateDocumentRequest(
                collection_id=collection_id,
                file_id=file_id,
                name=name,
                data=data,
                content_type=content_type,
                fields=fields,
            )
        )

    def reindex_document(self, collection_id: str, file_id: str) -> None:
        """Regenerates indices for a document.

        Use this method when you have updated the configuration of a collection and wish to
        re-index existing documents with the new configuration.

        Args:
            collection_id: The ID of the collection containing the document.
            file_id: The ID of the document to reindex.
        """
        return self._collections_stub.ReIndexDocument(
            collections_pb2.ReIndexDocumentRequest(
                collection_id=collection_id,
                file_id=file_id,
            )
        )
