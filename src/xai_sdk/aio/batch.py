from typing import Optional, Sequence, Union

from ..batch import (
    BaseClient,
    ListBatchResultsResponse,
)
from ..chat import BaseChat
from ..proto import batch_pb2


class Client(BaseClient):
    """Async Client for interacting with the `Batch` API."""

    async def create(
        self,
        batch_name: str,
    ) -> batch_pb2.Batch:
        """Create a new batch.

        Args:
            batch_name: The name of the batch to create.

        Returns:
            The created `Batch`.

        Examples:
            ```
            from xai_sdk import AsyncClient


            client = AsyncClient()
            batch = await client.batch.create("my_batch")
            ```

        """
        return await self._stub.CreateBatch(batch_pb2.CreateBatchRequest(name=batch_name))

    async def add(
        self,
        batch_id: str,
        batch_requests: Sequence[Union[batch_pb2.BatchRequest, BaseChat]],
    ) -> None:
        """Add a list of batch requests to the batch with the given ID.

        Args:
            batch_id: The ID of the batch to add the requests to.
            batch_requests: A sequence of requests to add to the batch for processing. Each request can be either a
              `batch_pb2.BatchRequest` proto object or a chat object created from `client.chat.create()` containing the
              desired request parameters as well as appended messages. When using chat objects, you can optionally
              specify a `batch_request_id` to help identify and match responses with their corresponding requests
              when retrieving batch results.

        Examples:
            ```
            from xai_sdk import AsyncClient
            from xai_sdk.chat import user

            client = AsyncClient()

            # Create a new batch
            batch = await client.batch.create(batch_name="my_batch")

            # Create multiple chat objects with unique batch_request_ids for easy identification
            chats = []
            countries = ["UK", "USA", "Egypt"]
            for country in countries:
                chat = client.chat.create(
                    model="grok-3-latest",
                    max_tokens=200,
                    temperature=0.7,
                    batch_request_id=f"capital_{country.lower()}",  # Optional: helps match responses to requests
                )
                chat.append(user(f"What is the capital of {country}?"))
                chats.append(chat)

            # Add chat objects directly to batch
            await client.batch.add(batch_id=batch.batch_id, batch_requests=chats)
            ```
        """
        requests = []
        for request in batch_requests:
            if isinstance(request, batch_pb2.BatchRequest):
                requests.append(request)
            elif isinstance(request, BaseChat):
                requests.append(
                    batch_pb2.BatchRequest(completion_request=request.proto, batch_request_id=request._batch_request_id)
                )
            else:
                raise ValueError(f"Unsupported request type: {type(request)}")

        await self._stub.AddBatchRequests(
            batch_pb2.AddBatchRequestsRequest(batch_id=batch_id, batch_requests=requests),
        )

    async def get(self, batch_id: str) -> batch_pb2.Batch:
        """Get the details of a batch with the given batch ID.

        Args:
            batch_id: The ID of the batch to get.

        Returns:
            The fetched `Batch`.

        Examples:
            ```
            from xai_sdk import AsyncClient


            client = AsyncClient()

            # Assume you have created a batch with ID "batch_1234"

            batch = await client.batch.get("batch_1234")
            ```
        """
        return await self._stub.GetBatch(batch_pb2.GetBatchRequest(batch_id=batch_id))

    async def cancel(self, batch_id: str) -> batch_pb2.Batch:
        """Cancel a batch with the given ID.

        Args:
            batch_id: The ID of the batch to cancel.

        Returns:
            The cancelled batch.

        Examples:
            ```
            from xai_sdk import AsyncClient


            client = AsyncClient()

            # Assume you have created a batch with ID "batch_1234"

            cancelled_batch = await client.batch.cancel("batch_1234")
            ```
        """
        return await self._stub.CancelBatch(batch_pb2.CancelBatchRequest(batch_id=batch_id))

    async def list(
        self, limit: Optional[int] = None, pagination_token: Optional[str] = None
    ) -> batch_pb2.ListBatchesResponse:
        """List all batches for the team.

        Args:
            limit: The number of batches to return per page. Uses server default if not provided.
            pagination_token: Optional page token to retrieve the next page of results.

        Returns:
            A `ListBatchesResponse` object containing a page of batches with given `limit` and `pagination_token` to
            fetch the next page of results.

        Examples:
            ```
            from xai_sdk import AsyncClient


            client = AsyncClient()

            # List batches with a limit of 100 per page
            list_batches_response_pg1 = await client.batch.list(limit=100)
            print("Listing batches - Page 1:")
            print(list_batches_response_pg1.batches)

            # List batches with a pagination token to get the next page of results
            list_batches_response_pg2 = await client.batch.list(
                limit=100,
                pagination_token=list_batches_response_pg1.pagination_token,
            )
            print("Listing batches - Page 2:")
            print(list_batches_response_pg2.batches)
            ```
        """
        return await self._stub.ListBatches(
            batch_pb2.ListBatchesRequest(limit=limit, pagination_token=pagination_token)
        )

    async def list_batch_requests(
        self, batch_id: str, limit: Optional[int] = None, pagination_token: Optional[str] = None
    ) -> batch_pb2.ListBatchRequestMetadataResponse:
        """List the batch request metadata for the batch with given ID.

        Args:
            batch_id: The ID of the batch to list its request metadata for.
            limit: The number of batch request metadata to return per page. Uses server default if not provided.
            pagination_token: Optional page token to retrieve the next page of results.

        Returns:
            A `ListBatchRequestMetadataResponse` object containing a sequence of batch request metadata in
            `batch_request_metadata` and `pagination_token` to fetch the next page of results.

        Examples:
            ```
            from xai_sdk import AsyncClient


            client = AsyncClient()

            # Assume you have created a batch with ID "batch_1234"

            batch_request_metadata_response = await client.batch.list_batch_requests("batch_1234")
            print(batch_request_metadata_response)
            ```
        """
        return await self._stub.ListBatchRequestMetadata(
            batch_pb2.ListBatchRequestMetadataRequest(batch_id=batch_id, limit=limit, pagination_token=pagination_token)
        )

    async def list_batch_results(
        self, batch_id: str, limit: Optional[int] = None, pagination_token: Optional[str] = None
    ) -> ListBatchResultsResponse:
        """List the results of the requests in the batch with given ID.

        Args:
            batch_id: The ID of the batch to list results for.
            limit: The number of results to return per page. Uses server default if not provided.
            pagination_token: Optional page token to retrieve the next page of results.

        Returns:
            A `ListBatchResultsResponse` object containing a sequence of batch request results in `results` belonging to
            the given batch and `pagination_token` to fetch the next page of results.

        Examples:
            ```
            from xai_sdk import AsyncClient

            client = AsyncClient()

            # Assume you have created a batch with ID "batch_1234"

            batch_result_response = await client.batch.list_batch_results("batch_1234")
            print(batch_result_response)
            ```
        """
        list_batch_results_response_pb = await self._stub.ListBatchResults(
            batch_pb2.ListBatchResultsRequest(
                batch_id=batch_id,
                limit=limit,
                pagination_token=pagination_token,
            ),
        )

        return ListBatchResultsResponse(list_batch_results_response_pb)
