from __future__ import annotations

import datetime
import re
from typing import Optional, Sequence, Union

import grpc

from .chat import Response
from .image import BaseImageResponse
from .meta import ProtoDecorator
from .proto import batch_pb2, batch_pb2_grpc
from .video import VideoResponse

# Defaults match the hand-rolled polling loops in examples/sync|aio/batch_request.py.
DEFAULT_BATCH_TIMEOUT = datetime.timedelta(hours=24)
DEFAULT_BATCH_POLL_INTERVAL = datetime.timedelta(seconds=3)

# Guidance only — not a client-side allowlist. These models are used successfully in
# SDK batch examples; the server remains the source of truth for eligibility.
BATCH_MODEL_SUGGESTIONS = (
    "grok-4.20",
    "grok-4.20-non-reasoning",
    "grok-4.3",
)

_UNSUPPORTED_BATCH_MODEL_RE = re.compile(
    r"Model\s+(?P<model>\S+)\s+is not supported for batch processing",
    re.IGNORECASE,
)


class BatchUnsupportedModelError(ValueError):
    """Raised when the Batch API rejects a model as unsupported for batch processing.

    The Batch API allowlist is enforced server-side. When ``batch.add`` fails with
    ``INVALID_ARGUMENT`` and a "not supported for batch processing" detail (for
    example ``grok-4.5``; see GitHub issue #176), the SDK remaps that gRPC error to
    this exception so callers get actionable guidance instead of a raw RpcError.
    """

    def __init__(self, model: Optional[str], details: str) -> None:
        """Initialize a new ``BatchUnsupportedModelError``.

        Args:
            model: The rejected model name, when it can be parsed from the server detail.
            details: The original gRPC status details string from the server.
        """
        self.model = model
        self.details = details
        suggestions = ", ".join(BATCH_MODEL_SUGGESTIONS)
        model_label = f"`{model}`" if model else "the requested model"
        message = (
            f"Batch API does not support {model_label} for batch processing. "
            f"Server detail: {details} "
            f"Try a batch-eligible model used in the SDK examples, such as: {suggestions}."
        )
        super().__init__(message)


def map_add_batch_error(exc: BaseException) -> BaseException:
    """Map AddBatchRequests gRPC failures to clearer SDK exceptions when possible.

    Args:
        exc: The exception raised by the gRPC stub.

    Returns:
        A ``BatchUnsupportedModelError`` when the failure is an unsupported-model
        ``INVALID_ARGUMENT``, otherwise ``exc`` unchanged.
    """
    code_fn = getattr(exc, "code", None)
    details_fn = getattr(exc, "details", None)
    if not callable(code_fn) or not callable(details_fn):
        return exc

    try:
        status = code_fn()
        raw_details = details_fn()
    except Exception:
        return exc

    if status != grpc.StatusCode.INVALID_ARGUMENT:
        return exc

    detail_str = raw_details if isinstance(raw_details, str) else ""
    match = _UNSUPPORTED_BATCH_MODEL_RE.search(detail_str)
    if match is None and "not supported for batch processing" not in detail_str.lower():
        return exc

    model = match.group("model") if match is not None else None
    return BatchUnsupportedModelError(model, detail_str)


def is_batch_complete(batch: batch_pb2.Batch) -> bool:
    """Return True when the batch has no remaining pending requests."""
    return batch.state.num_pending == 0


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
    def results(self) -> Sequence[BatchResult]:
        """All batch results regardless of success or failure."""
        return [BatchResult(result) for result in self.proto.results]

    @property
    def succeeded(self) -> Sequence[BatchResult]:
        """Returns only the successful batch results."""
        return [BatchResult(result) for result in self.proto.results if result.error.code == 0]

    @property
    def failed(self) -> Sequence[BatchResult]:
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
        """The chat completion response from processing this batch request."""
        return Response(self.proto.response.completion_response, 0)

    @property
    def image_response(self) -> BaseImageResponse:
        """The image generation response from processing this batch request."""
        return BaseImageResponse(self.proto.response.image_response, 0)

    @property
    def video_response(self) -> VideoResponse:
        """The video generation response from processing this batch request."""
        return VideoResponse(self.proto.response.video_response)

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
