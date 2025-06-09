from typing import Union

import grpc

from .proto import tokenize_pb2_grpc


class BaseClient:
    """Base Client for interacting with the `Tokenize` API."""

    _stub: tokenize_pb2_grpc.TokenizeStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = tokenize_pb2_grpc.TokenizeStub(channel)
