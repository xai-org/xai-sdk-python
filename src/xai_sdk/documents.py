from typing import Union

import grpc

from .proto import documents_pb2_grpc


class BaseClient:
    """Base Client for interacting with the `Documents` API."""

    _stub: documents_pb2_grpc.DocumentsStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = documents_pb2_grpc.DocumentsStub(channel)
