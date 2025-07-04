# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import embed_pb2 as xai_dot_api_dot_v1_dot_embed__pb2


class EmbedderStub(object):
    """An API service for interaction with available embedding models.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Embed = channel.unary_unary(
                '/xai_api.Embedder/Embed',
                request_serializer=xai_dot_api_dot_v1_dot_embed__pb2.EmbedRequest.SerializeToString,
                response_deserializer=xai_dot_api_dot_v1_dot_embed__pb2.EmbedResponse.FromString,
                _registered_method=True)


class EmbedderServicer(object):
    """An API service for interaction with available embedding models.
    """

    def Embed(self, request, context):
        """Produces one embedding for each input object. The size of the produced
        feature vectors depends on the chosen model.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_EmbedderServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Embed': grpc.unary_unary_rpc_method_handler(
                    servicer.Embed,
                    request_deserializer=xai_dot_api_dot_v1_dot_embed__pb2.EmbedRequest.FromString,
                    response_serializer=xai_dot_api_dot_v1_dot_embed__pb2.EmbedResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'xai_api.Embedder', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('xai_api.Embedder', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Embedder(object):
    """An API service for interaction with available embedding models.
    """

    @staticmethod
    def Embed(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/xai_api.Embedder/Embed',
            xai_dot_api_dot_v1_dot_embed__pb2.EmbedRequest.SerializeToString,
            xai_dot_api_dot_v1_dot_embed__pb2.EmbedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
