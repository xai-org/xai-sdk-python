from typing import Optional

import grpc


# Sync interceptors
class AuthInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """A gRPC interceptor that adds authentication headers for insecure channels."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str], ...]] = None) -> None:
        """Initialize the AuthInterceptor with API key and optional metadata."""
        self._api_key = api_key
        self._metadata = metadata

    def _add_auth_metadata(self, client_call_details):
        """Adds authentication metadata to the call details."""
        existing_metadata = list(client_call_details.metadata or [])

        auth_header = ("authorization", f"Bearer {self._api_key}")
        existing_metadata.append(auth_header)

        if self._metadata:
            existing_metadata.extend(self._metadata)

        return client_call_details._replace(metadata=existing_metadata)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept unary-unary calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercept unary-stream calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """Intercept stream-unary calls (e.g. file uploads) to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        """Intercept stream-stream calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return continuation(new_details, request_iterator)


class TimeoutInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    """A gRPC interceptor that sets a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initializes a new instance of the `TimeoutInterceptor` class.

        Args:
            timeout: The timeout in seconds that will be applied to all requests when this interceptor is used.
        """
        self.timeout = timeout

    def _intercept_call(self, continuation, client_call_details, request):
        client_call_details = client_call_details._replace(timeout=self.timeout)
        return continuation(client_call_details, request)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercepts a unary-unary RPC call."""
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercepts a unary-stream RPC call."""
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """Intercepts a stream-unary RPC call."""
        return self._intercept_call(continuation, client_call_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        """Intercepts a stream-stream RPC call."""
        return self._intercept_call(continuation, client_call_details, request_iterator)


# Async interceptors

# It's not possible to create a single AsyncInterceptor that can inherit from all the different rpc variants.
# see: https://github.com/grpc/grpc/issues/31442
# Instead, every rpc variant gets its own interceptor class, and the shared logic lives in the base classes below.


class _AuthAioInterceptor:
    """Shared logic for the async interceptors that add the api key to the rpc metadata."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str], ...]] = None) -> None:
        """Initialize the interceptor with API key and optional metadata."""
        self._api_key = api_key
        self._metadata = metadata

    def _add_auth_metadata(self, client_call_details):
        """Adds authentication metadata to the call details."""
        existing_metadata = list(client_call_details.metadata or [])

        auth_header = ("authorization", f"Bearer {self._api_key}")
        existing_metadata.append(auth_header)

        if self._metadata:
            existing_metadata.extend(self._metadata)

        return client_call_details._replace(metadata=existing_metadata)


class UnaryUnaryAuthAioInterceptor(_AuthAioInterceptor, grpc.aio.UnaryUnaryClientInterceptor):
    """Async interceptor for unary-unary calls that adds the api key to the rpc metadata."""

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept async unary-unary calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request)  # type: ignore


class UnaryStreamAuthAioInterceptor(_AuthAioInterceptor, grpc.aio.UnaryStreamClientInterceptor):
    """Async interceptor for unary-stream calls that adds the api key to the rpc metadata."""

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercept async unary-stream calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request)  # type: ignore[reportAwaitable]


class StreamUnaryAuthAioInterceptor(_AuthAioInterceptor, grpc.aio.StreamUnaryClientInterceptor):
    """Async interceptor for stream-unary calls (e.g. file uploads) that adds the api key to the rpc metadata."""

    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """Intercept async stream-unary calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request_iterator)  # type: ignore[reportAwaitable]


class StreamStreamAuthAioInterceptor(_AuthAioInterceptor, grpc.aio.StreamStreamClientInterceptor):
    """Async interceptor for stream-stream calls that adds the api key to the rpc metadata."""

    async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        """Intercept async stream-stream calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request_iterator)  # type: ignore[reportAwaitable]


class _TimeoutAioInterceptor:
    """Shared logic for the async interceptors that set a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initialize the interceptor with timeout value."""
        self.timeout = timeout

    def _with_timeout(self, client_call_details):
        """Returns the call details with the default timeout applied."""
        return client_call_details._replace(timeout=self.timeout)


class UnaryUnaryTimeoutAioInterceptor(_TimeoutAioInterceptor, grpc.aio.UnaryUnaryClientInterceptor):
    """Async interceptor for unary-unary calls that sets a default timeout for all requests."""

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept async unary-unary calls to set timeout."""
        return await continuation(self._with_timeout(client_call_details), request)


class UnaryStreamTimeoutAioInterceptor(_TimeoutAioInterceptor, grpc.aio.UnaryStreamClientInterceptor):
    """Async interceptor for unary-stream calls that sets a default timeout for all requests."""

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercept async unary-stream calls to set timeout."""
        return await continuation(self._with_timeout(client_call_details), request)  # type: ignore[reportAwaitable]


class StreamUnaryTimeoutAioInterceptor(_TimeoutAioInterceptor, grpc.aio.StreamUnaryClientInterceptor):
    """Async interceptor for stream-unary calls that sets a default timeout for all requests."""

    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """Intercept async stream-unary calls to set timeout."""
        return await continuation(self._with_timeout(client_call_details), request_iterator)  # type: ignore[reportAwaitable]


class StreamStreamTimeoutAioInterceptor(_TimeoutAioInterceptor, grpc.aio.StreamStreamClientInterceptor):
    """Async interceptor for stream-stream calls that sets a default timeout for all requests."""

    async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        """Intercept async stream-stream calls to set timeout."""
        return await continuation(self._with_timeout(client_call_details), request_iterator)  # type: ignore[reportAwaitable]
