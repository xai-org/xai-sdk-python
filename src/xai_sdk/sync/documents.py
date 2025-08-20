from typing import Optional, Sequence

from ..documents import BaseClient
from ..proto import documents_pb2


class Client(BaseClient):
    """Synchronous client for interacting with the `Documents` API."""

    def search(
        self,
        query: str,
        collection_ids: Sequence[str],
        limit: Optional[int] = None,
    ) -> documents_pb2.SearchResponse:
        """Perform a semantic, embedding-based search across all documents in the given collections.

        Args:
            query: The search query.
            collection_ids: The IDs of the collections to search in.
            limit: The maximum number of results to return.

        Returns:
            A SearchResponse object containing the search results.
        """
        return self._stub.Search(
            documents_pb2.SearchRequest(
                query=query, source=documents_pb2.DocumentsSource(collection_ids=collection_ids), limit=limit
            )
        )
