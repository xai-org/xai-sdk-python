from typing import Union

import grpc

from .proto import models_pb2_grpc


class BaseClient:
    """Base Client for interacting with the `Models` API."""

    _stub: models_pb2_grpc.ModelsStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = models_pb2_grpc.ModelsStub(channel)
