from typing import Optional, Sequence, Union

import grpc

from .chat import Response
from .meta import ProtoDecorator
from .proto import batch_pb2, batch_pb2_grpc


class BaseClient:
    """Base Client for interacting with the `Batch` API."""

    # Stub to send grpc requests
    _stub: batch_pb2_grpc.BatchMgmtStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = batch_pb2_grpc.BatchMgmtStub(channel)


class ListBatchResultsResponse(ProtoDecorator[batch_pb2.ListBatchResultsResponse]):
    """A page of batch results from `Client.batch.list_batch_results()`."""

    @property
    def results(self) -> Sequence["BatchResult"]:
        """All batch results regardless of success or failure."""
        return [BatchResult(result) for result in self.proto.results]

    @property
    def succeeded(self) -> Sequence["BatchResult"]:
        """Returns only the successful batch results."""
        return [BatchResult(result) for result in self.proto.results if result.error.code == 0]

    @property
    def failed(self) -> Sequence["BatchResult"]:
        """Returns only the failed batch results."""
        return [BatchResult(result) for result in self.proto.results if result.error.code != 0]

    @property
    def pagination_token(self) -> Optional[str]:
        """The pagination token to fetch the next page of results."""
        return self.proto.pagination_token if self.proto.pagination_token else None


class BatchResult(ProtoDecorator[batch_pb2.BatchResult]):
    """The processing result of a single batch request."""

    @property
    def batch_request_id(self) -> str:
        """The ID of the batch request.

        This is either supplied by user in `BatchRequest.batch_request_id`, or generated
        by Batch API service if not provided by user. It is unique within the batch.
        """
        return self.proto.batch_request_id

    @property
    def response(self) -> Response:
        """The completion response from processing this batch request.

        Returns:
            The `Response` object.
        """
        return Response(self.proto.response.completion_response, 0)

    @property
    def has_error(self) -> bool:
        """Returns True if this batch request failed."""
        return self.proto.error.code != 0

    @property
    def is_success(self) -> bool:
        """Returns True if this batch request succeeded."""
        return self.proto.error.code == 0

    @property
    def error_message(self) -> Optional[str]:
        """Returns the error message if the request failed, None otherwise."""
        if self.proto.error.code != 0:
            return self.proto.error.message
        return None
