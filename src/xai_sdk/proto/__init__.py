from packaging import version

import google.protobuf

_PROTOBUF_MAJOR = version.parse(google.protobuf.__version__).major

if _PROTOBUF_MAJOR == 5:
    from .v5 import (
        auth_pb2,
        auth_pb2_grpc,
        batch_pb2,
        batch_pb2_grpc,
        chat_pb2,
        chat_pb2_grpc,
        collections_pb2,
        collections_pb2_grpc,
        deferred_pb2,
        deferred_pb2_grpc,
        documents_pb2,
        documents_pb2_grpc,
        embed_pb2,
        embed_pb2_grpc,
        files_pb2,
        files_pb2_grpc,
        image_pb2,
        image_pb2_grpc,
        models_pb2,
        models_pb2_grpc,
        sample_pb2,
        sample_pb2_grpc,
        shared_pb2,
        tokenize_pb2,
        tokenize_pb2_grpc,
        types_pb2,
        usage_pb2,
        video_pb2,
        video_pb2_grpc,
    )
# The v6 gencode loads on any newer runtime: protobuf only rejects a runtime that is
# older than the gencode, so protobuf 7 (and later) can use the v6 modules as is.
elif _PROTOBUF_MAJOR >= 6:
    from .v6 import (
        auth_pb2,
        auth_pb2_grpc,
        batch_pb2,
        batch_pb2_grpc,
        chat_pb2,
        chat_pb2_grpc,
        collections_pb2,
        collections_pb2_grpc,
        deferred_pb2,
        deferred_pb2_grpc,
        documents_pb2,
        documents_pb2_grpc,
        embed_pb2,
        embed_pb2_grpc,
        files_pb2,
        files_pb2_grpc,
        image_pb2,
        image_pb2_grpc,
        models_pb2,
        models_pb2_grpc,
        sample_pb2,
        sample_pb2_grpc,
        shared_pb2,
        tokenize_pb2,
        tokenize_pb2_grpc,
        types_pb2,
        usage_pb2,
        video_pb2,
        video_pb2_grpc,
    )
else:
    raise ValueError(f"Unsupported protobuf version: {google.protobuf.__version__}")
