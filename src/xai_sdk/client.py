"""Wrappers around the bare gRPC bindings."""

import abc
import dataclasses
import json
import sys
from typing import Any, Optional, Sequence

import grpc

from .__about__ import __version__

USER_AGENT = f"XaiSdk/{__version__}"

# gRPC treats any `maxAttempts` above this value as this value, see https://github.com/grpc/proposal/blob/master/A6-client-retries.md
_MAX_RETRY_ATTEMPTS = 5

# Channel options that control retries, and therefore can't be combined with a `RetryPolicy`.
_RETRY_CHANNEL_OPTIONS = frozenset({"grpc.enable_retries", "grpc.service_config"})


@dataclasses.dataclass(frozen=True)
class RetryPolicy:
    """Policy for automatically retrying failed requests, passed to a client via its `retry_policy` argument.

    Retries are performed transparently by gRPC (see https://grpc.io/docs/guides/retry/). When an attempt fails
    with one of the `retryable_status_codes`, gRPC waits for a random delay between 0 and
    `min(initial_backoff * backoff_multiplier ** (n - 1), max_backoff)` seconds before making the n-th retry.

    The default values match the policy that clients use when no `retry_policy` is given: up to 5 attempts for
    requests failing with `UNAVAILABLE`.

    Example:
        >>> import grpc
        >>> from xai_sdk import Client, RetryPolicy
        >>> client = Client(
        ...     retry_policy=RetryPolicy(
        ...         max_attempts=3,
        ...         initial_backoff=0.5,
        ...         max_backoff=2.0,
        ...         backoff_multiplier=1.5,
        ...         retryable_status_codes=(grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.RESOURCE_EXHAUSTED),
        ...     )
        ... )

    Attributes:
        max_attempts: Maximum number of attempts, including the original request. Must be between 1 and 5, as
            gRPC doesn't allow more than 5 attempts. Use 1 to disable retries.
        initial_backoff: Upper bound of the delay before the first retry, in seconds. Must be positive.
        max_backoff: Upper bound of the delay before any retry, in seconds. Must be positive.
        backoff_multiplier: Factor by which the delay upper bound grows after each retry. Must be positive.
        retryable_status_codes: gRPC status codes that trigger a retry. Must not be empty or contain `OK`.
    """

    max_attempts: int = 5
    initial_backoff: float = 0.1
    max_backoff: float = 1.0
    backoff_multiplier: float = 2.0
    retryable_status_codes: Sequence[grpc.StatusCode] = (grpc.StatusCode.UNAVAILABLE,)

    def __post_init__(self) -> None:
        """Validates the policy, so that a misconfiguration fails when creating the client and not on first use."""
        # gRPC requires an integer here and would fail to parse e.g. 2.5, which `1 <= 2.5 <= 5` lets through.
        if type(self.max_attempts) is not int or not 1 <= self.max_attempts <= _MAX_RETRY_ATTEMPTS:
            raise ValueError(
                f"max_attempts must be an integer between 1 and {_MAX_RETRY_ATTEMPTS}, got {self.max_attempts!r}."
            )
        for name in ("initial_backoff", "max_backoff", "backoff_multiplier"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"{name} must be positive, got {value}.")
        # gRPC doesn't reject this, but the delay is capped at max_backoff, so initial_backoff would be ignored.
        if self.initial_backoff > self.max_backoff:
            raise ValueError(
                f"initial_backoff ({self.initial_backoff}s) can't be greater than max_backoff ({self.max_backoff}s)."
            )
        if not self.retryable_status_codes:
            raise ValueError("retryable_status_codes must not be empty.")
        if any(not isinstance(code, grpc.StatusCode) for code in self.retryable_status_codes):
            raise TypeError("All items in retryable_status_codes must be instances of grpc.StatusCode.")
        if grpc.StatusCode.OK in self.retryable_status_codes:
            raise ValueError("retryable_status_codes must not contain grpc.StatusCode.OK.")
        # Store the codes as a tuple, so that the frozen policy stays hashable when a list is passed in.
        object.__setattr__(self, "retryable_status_codes", tuple(self.retryable_status_codes))

    def _channel_options(self) -> list[tuple[str, Any]]:
        """Returns the gRPC channel options that implement this policy."""
        if self.max_attempts == 1:
            return [("grpc.enable_retries", 0)]
        return [("grpc.enable_retries", 1), ("grpc.service_config", self._service_config_json())]

    def _service_config_json(self) -> str:
        """Returns a gRPC service config that applies this policy to all methods."""
        return json.dumps(
            {
                "methodConfig": [
                    {
                        "name": [{}],
                        "retryPolicy": {
                            "maxAttempts": self.max_attempts,
                            "initialBackoff": _format_duration(self.initial_backoff),
                            "maxBackoff": _format_duration(self.max_backoff),
                            "backoffMultiplier": self.backoff_multiplier,
                            "retryableStatusCodes": [code.name for code in self.retryable_status_codes],
                        },
                    }
                ]
            }
        )


def _format_duration(seconds: float) -> str:
    """Formats a number of seconds as a protobuf JSON duration, e.g. 0.5 -> "0.5s" and 2.0 -> "2s"."""
    return f"{seconds:.9f}".rstrip("0").rstrip(".") + "s"


# Retries if the service returns an UNAVAILABLE error.
_DEFAULT_SERVICE_CONFIG_JSON = RetryPolicy()._service_config_json()

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
    ("grpc.primary_user_agent", USER_AGENT),
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
        retry_policy: Optional[RetryPolicy] = None,
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
                timeout of 27 minutes (1620 seconds) will be used.
            retry_policy: The policy for automatically retrying failed requests, see `RetryPolicy`. If not set,
                requests failing with `UNAVAILABLE` are retried up to 4 times with exponential backoff. Can't be
                combined with the `grpc.enable_retries` and `grpc.service_config` channel options.
            use_insecure_channel: Whether to use an insecure gRPC channel. If True, an insecure gRPC client
                is used for the underlying connection, though the API key will still be applied
                to outgoing requests via metadata through gRPC interceptors. Defaults to False.

        Raises:
            ValueError: If the `XAI_API_KEY` environment variable is not set.
            ValueError: If the API key is empty.
            ValueError: If `retry_policy` is combined with channel options that also configure retries.
        """
        # Copy into a list, so that any sequence of options (e.g. a tuple) can be combined with the defaults.
        channel_options = list(channel_options or [])
        user_defined_options = {option[0] for option in channel_options}
        if retry_policy is not None:
            conflicting_options = user_defined_options & _RETRY_CHANNEL_OPTIONS
            if conflicting_options:
                raise ValueError(
                    f"`retry_policy` can't be combined with the {', '.join(sorted(conflicting_options))} channel "
                    "option(s), as both configure retries."
                )
            retry_options = retry_policy._channel_options()
            channel_options = [*retry_options, *channel_options]
            user_defined_options.update(option[0] for option in retry_options)
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
