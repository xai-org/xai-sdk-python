from typing import Union

import grpc

from .proto import auth_pb2_grpc


class BaseClient:
    """Base Client for interacting with `Auth` API."""

    _stub: auth_pb2_grpc.AuthStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = auth_pb2_grpc.AuthStub(channel)
