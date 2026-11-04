"""Authentication client module for xAI SDK.

This module provides clients for interacting with the xAI Authentication API,
supporting both synchronous and asynchronous gRPC channels.
"""

from typing import Union

import grpc

from .proto import auth_pb2_grpc


class BaseClient:
    """Base client for interacting with the xAI Authentication API.

    This class serves as the foundation for authentication-related operations
    in the xAI SDK. It manages the underlying gRPC stub used to communicate
    with the authentication service.

    Attributes:
        _stub: The gRPC stub for communicating with the Auth API service.
    """

    _stub: auth_pb2_grpc.AuthStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]) -> None:
        """Initialize a new Auth API client.

        Creates a new client instance with the provided gRPC channel. The channel
        can be either a synchronous (grpc.Channel) or asynchronous (grpc.aio.Channel)
        channel, allowing for flexible usage patterns.

        Args:
            channel: A gRPC channel (sync or async) for communicating with the service.
                    Must be properly configured and connected before use.

        Raises:
            TypeError: If the channel is not a valid gRPC channel type.

        Example:
            ```
            import grpc
            from xai_sdk.auth import BaseClient

            # Create a synchronous channel
            channel = grpc.insecure_channel("api.xai.com:50051")
            client = BaseClient(channel)
            ```
        """
        if not isinstance(channel, (grpc.Channel, grpc.aio.Channel)):
            raise TypeError(
                f"channel must be a grpc.Channel or grpc.aio.Channel, "
                f"got {type(channel).__name__}"
            )
        self._stub = auth_pb2_grpc.AuthStub(channel)
