from typing import Optional

import grpc


# Sync interceptors
class AuthInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
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


class TimeoutInterceptor(grpc.UnaryUnaryClientInterceptor, grpc.UnaryStreamClientInterceptor):
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


# Async interceptors

# It's not possible to create a single AsyncInterceptor that can inherit from all the different rpc variants.
# see: https://github.com/grpc/grpc/issues/31442


class UnaryUnaryAuthAioInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Async interceptor for unary-unary calls that adds the api key to the rpc metadata."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str], ...]] = None) -> None:
        """Initialize the UnaryUnaryAuthAioInterceptor with API key and optional metadata."""
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

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept async unary-unary calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request)  # type: ignore


class UnaryStreamAuthAioInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Async interceptor for unary-stream calls that adds the api key to the rpc metadata."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str], ...]] = None) -> None:
        """Initialize the UnaryStreamAuthAioInterceptor with API key and optional metadata."""
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

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercept async unary-stream calls to add authentication metadata."""
        new_details = self._add_auth_metadata(client_call_details)
        return await continuation(new_details, request)  # type: ignore[reportAwaitable]


class UnaryUnaryTimeoutAioInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Async interceptor for unary-unary calls that sets a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initialize the UnaryUnaryTimeoutAioInterceptor with timeout value."""
        self.timeout = timeout

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept async unary-unary calls to set timeout."""
        client_call_details = client_call_details._replace(timeout=self.timeout)  # type: ignore
        return await continuation(client_call_details, request)


class UnaryStreamTimeoutAioInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Async interceptor for unary-stream calls that sets a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initialize the UnaryStreamTimeoutAioInterceptor with timeout value."""
        self.timeout = timeout

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercept async unary-stream calls to set timeout."""
        client_call_details = client_call_details._replace(timeout=self.timeout)  # type: ignore
        return await continuation(client_call_details, request)  # type: ignore[reportAwaitable]
