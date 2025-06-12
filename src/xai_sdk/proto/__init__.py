from packaging import version

import google.protobuf

if version.parse(google.protobuf.__version__).major == 5:
    from .v5 import (
        auth_pb2,
        auth_pb2_grpc,
        chat_pb2,
        chat_pb2_grpc,
        deferred_pb2,
        deferred_pb2_grpc,
        embed_pb2,
        embed_pb2_grpc,
        image_pb2,
        image_pb2_grpc,
        models_pb2,
        models_pb2_grpc,
        sample_pb2,
        sample_pb2_grpc,
        tokenize_pb2,
        tokenize_pb2_grpc,
        usage_pb2,
    )
elif version.parse(google.protobuf.__version__).major == 6:
    from .v6 import (
        auth_pb2,
        auth_pb2_grpc,
        chat_pb2,
        chat_pb2_grpc,
        deferred_pb2,
        deferred_pb2_grpc,
        embed_pb2,
        embed_pb2_grpc,
        image_pb2,
        image_pb2_grpc,
        models_pb2,
        models_pb2_grpc,
        sample_pb2,
        sample_pb2_grpc,
        tokenize_pb2,
        tokenize_pb2_grpc,
        usage_pb2,
    )
else:
    raise ValueError(f"Unsupported protobuf version: {google.protobuf.__version__}")