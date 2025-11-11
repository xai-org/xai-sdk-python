"""Wrappers around the bare gRPC bindings."""

import abc
import json
import sys
from typing import Any, Optional, Sequence

import grpc

from .__about__ import __version__

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
        management_api_key: Optional[str] = None,
        *,
        api_host: str = "api.x.ai",
        management_api_host: str = "management-api.x.ai",
        metadata: Optional[tuple[tuple[str, str], ...]] = None,
        channel_options: Optional[list[tuple[str, Any]]] = None,
        timeout: Optional[float] = None,
        use_insecure_channel: bool = False,
    ) -> None:
        """Initializes a new instance of the `Client` class.

        Args:
            api_key: API key to use. If unspecified, the API key is read from the `XAI_API_KEY`
                environment variable.
            management_api_key: Management API key to use. If unspecified, the Management API key is read from the
                `XAI_MANAGEMENT_KEY` environment variable.
            api_host: Hostname of the API server.
            management_api_host: Hostname of the Management API server.
            metadata: Metadata to be sent with each gRPC request. Each tuple should contain a
                key/value pair.
            channel_options: Additional channel options to be sent with each gRPC request, the options defined here
                will override the default options if they have the same name.
            timeout: The timeout in seconds for all gRPC requests using this client. If not set, the default
                timeout of 15 minutes (900 seconds) will be used.
            use_insecure_channel: Whether to use an insecure gRPC channel. If True, an insecure gRPC client
                is used for the underlying connection, though the API key will still be applied
                to outgoing requests via metadata through gRPC interceptors. Defaults to False.

        Raises:
            ValueError: If the `XAI_API_KEY` environment variable is not set.
            ValueError: If the API key is empty.
        """
        channel_options = channel_options or []
        user_defined_options = {option[0] for option in channel_options}
        default_options = [option for option in _DEFAULT_CHANNEL_OPTIONS if option[0] not in user_defined_options]
        timeout = timeout or _DEFAULT_RPC_TIMEOUT_SECONDS

        # Add the xAI SDK version and language to the metadata
        metadata = (metadata or ()) + (
            ("xai-sdk-version", f"python/{__version__}"),
            ("xai-sdk-language", f"python/{sys.version_info.major}.{sys.version_info.minor}"),
        )

        self._init(
            api_key,
            management_api_key,
            api_host,
            management_api_host,
            metadata,
            default_options + channel_options,
            timeout,
            use_insecure_channel,
        )

    @abc.abstractmethod
    def _init(
        self,
        api_key: Optional[str],
        management_api_key: Optional[str],
        api_host: str,
        management_api_host: str,
        metadata: Optional[tuple[tuple[str, str], ...]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
        use_insecure_channel: bool,  # noqa: FBT001
    ) -> None:
        """Initializes the client instance."""


def create_channel_credentials(
    api_key: str, api_host: str, metadata: Optional[tuple[tuple[str, str], ...]]
) -> grpc.ChannelCredentials:
    """Creates the credentials for the gRPC channel.

    Args:
        api_key: The API key to use for authentication.
        api_host: The host of the API server.
        metadata: Metadata to be sent with each gRPC request.

    Returns:
        The credentials for the gRPC channel.
    """
    if not api_key:
        raise ValueError("Empty xAI API key provided.")

    # Create a channel to connect to the API host. Use the API key for authentication.
    call_credentials = grpc.metadata_call_credentials(_APIAuthPlugin(api_key, metadata))
    if api_host.startswith("localhost:"):
        channel_credentials = grpc.local_channel_credentials()
    else:
        channel_credentials = grpc.ssl_channel_credentials()
    return grpc.composite_channel_credentials(channel_credentials, call_credentials)


class _APIAuthPlugin(grpc.AuthMetadataPlugin):
    """A specification for API-key based authentication."""

    def __init__(self, api_key: str, metadata: Optional[tuple[tuple[str, str], ...]]) -> None:
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
