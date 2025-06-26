"""Wrappers around the bare gRPC bindings."""

import abc
import json
import os
from typing import Any, Optional, Sequence

import grpc

# Retries if the service returns an UNAVAILABLE error.
_DEFAULT_SERVICE_CONFIG_JSON = json.dumps(
    {
        "methodConfig": [
            {
                "name": [{}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "1s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }
)

_MIB = 1 << 20  # 1 MiB

_DEFAULT_CHANNEL_OPTIONS: Sequence[tuple[str, Any]] = [
    ("grpc.max_send_message_length", 20 * _MIB),
    ("grpc.max_receive_message_length", 20 * _MIB),
    ("grpc.enable_retries", 1),
    ("grpc.service_config", _DEFAULT_SERVICE_CONFIG_JSON),
    ("grpc.keepalive_time_ms", 30000),
    ("grpc.keepalive_timeout_ms", 10000),
    ("grpc.keepalive_permit_without_calls", 1),
    ("grpc.http2.max_pings_without_data", 0),
]

_DEFAULT_RPC_TIMEOUT_SECONDS = 27 * 60


class BaseClient(abc.ABC):
    """Base Client for connecting to the xAI API.

    The client uses an API key, which is either read from the environment variable `XAI_API_KEY` or
    provided by the `api_key` constructor argument. API keys can be created and managed in our API
    console, which is available under console.x.ai.

    The API is hosted on api.x.ai, and we connect via port 443.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        api_host: str = "api.x.ai",
        metadata: Optional[tuple[tuple[str, str]]] = None,
        channel_options: Optional[list[tuple[str, Any]]] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """Initializes a new instance of the `Client` class.

        Args:
            api_key: API key to use. If unspecified, the API key is read from the `XAI_API_KEY`
                environment variable.
            api_host: Hostname of the API server.
            metadata: Metadata to be sent with each gRPC request. Each tuple should contain a
                key/value pair.
            channel_options: Additional channel options to be sent with each gRPC request, the options defined here
                will override the default options if they have the same name.
            timeout: The timeout in seconds for all gRPC requests using this client. If not set, the default
                timeout of 15 minutes (900 seconds) will be used.

        Raises:
            ValueError: If the `XAI_API_KEY` environment variable is not set.
            ValueError: If the API key is empty.
        """
        channel_options = channel_options or []
        user_defined_options = {option[0] for option in channel_options}
        default_options = [option for option in _DEFAULT_CHANNEL_OPTIONS if option[0] not in user_defined_options]
        timeout = timeout or _DEFAULT_RPC_TIMEOUT_SECONDS

        self._init(api_key, api_host, metadata, default_options + channel_options, timeout)

    @abc.abstractmethod
    def _init(
        self,
        api_key: Optional[str],
        api_host: str,
        metadata: Optional[tuple[tuple[str, str]]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> None:
        """Initializes the client instance."""


def create_channel_credentials(
    api_key: Optional[str], api_host: str, metadata: Optional[tuple[tuple[str, str]]]
) -> grpc.ChannelCredentials:
    """Creates the credentials for the gRPC channel.

    Args:
        api_key: The API key to use for authentication.
        api_host: The host of the API server.
        metadata: Metadata to be sent with each gRPC request.

    Returns:
        The credentials for the gRPC channel.
    """
    if api_key is None:
        api_key = _get_api_from_env()

    if not api_key:
        raise ValueError("Empty xAI API key provided.")

    # Create a channel to connect to the API host. Use the API key for authentication.
    call_credentials = grpc.metadata_call_credentials(_APIAuthPlugin(api_key, metadata))
    if api_host.startswith("localhost:"):
        channel_credentials = grpc.local_channel_credentials()
    else:
        channel_credentials = grpc.ssl_channel_credentials()
    return grpc.composite_channel_credentials(channel_credentials, call_credentials)


def _get_api_from_env() -> str:
    """Reads the API key from the `XAI_API_KEY` environment variable.

    Returns:
        The API key.

    Raises:
        ValueError: If the `XAI_API_KEY` environment variable is not set.
    """
    api_key = os.environ.get("XAI_API_KEY")
    if api_key is None:
        raise ValueError(
            "Trying to read the xAI API key from the XAI_API_KEY environment variable but it doesn't exist."
        )
    else:
        return api_key


class _APIAuthPlugin(grpc.AuthMetadataPlugin):
    """A specification for API-key based authentication."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str]]]) -> None:
        """Initializes a new instance of the `_APIAuthPlugin` class.

        Args:
            api_key: A valid xAI API key.
            metadata: Metadata to be sent with each gRPC request. Each tuple should contain a key/value pair
        """
        self._api_key = api_key
        self._metadata = metadata

    def __call__(self, context: grpc.AuthMetadataPluginCallback, callback: grpc.AuthMetadataPluginCallback):
        """See `grpc.AuthMetadataPlugin.__call__`."""
        del context  # Unused.

        api_key = ("authorization", f"Bearer {self._api_key}")
        if self._metadata is not None:
            metadata = (*self._metadata, api_key)
        else:
            metadata = (api_key,)
        callback(metadata, None)


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


# It's not possible to create a single AsyncInterceptor that can inherit from all the different rpc variants.
# see: https://github.com/grpc/grpc/issues/31442


class UnaryUnaryAioInterceptor(
    grpc.aio.UnaryUnaryClientInterceptor,
):
    """An asynchronous gRPC interceptor that sets a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initializes a new instance of the `AsyncTimeoutInterceptor` class.

        Args:
            timeout: The timeout in seconds that will be applied to all requests when this interceptor is used.
        """
        self.timeout = timeout

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercepts a unary-unary RPC call."""
        new_details = client_call_details._replace(timeout=self.timeout)
        response = await continuation(new_details, request)
        return await response


class UnaryStreamAioInterceptor(
    grpc.aio.UnaryStreamClientInterceptor,
):
    """An asynchronous gRPC interceptor that sets a default timeout for all requests."""

    def __init__(self, timeout: float) -> None:
        """Initializes a new instance of the `AsyncTimeoutInterceptor` class.

        Args:
            timeout: The timeout in seconds that will be applied to all requests when this interceptor is used.
        """
        self.timeout = timeout

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """Intercepts a unary-stream RPC call."""
        client_call_details = client_call_details._replace(timeout=self.timeout)
        return await continuation(client_call_details, request)  # type: ignore
