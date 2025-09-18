# flake8: noqa: N802

import base64
import contextlib
import http.server
import os.path
import threading
import time
import uuid
from collections import defaultdict
from concurrent import futures
from dataclasses import dataclass
from typing import Generator, Optional

import grpc
import portpicker
from google.protobuf import empty_pb2, timestamp_pb2

from xai_sdk.proto import (
    auth_pb2,
    auth_pb2_grpc,
    chat_pb2,
    chat_pb2_grpc,
    collections_pb2,
    collections_pb2_grpc,
    deferred_pb2,
    documents_pb2,
    documents_pb2_grpc,
    image_pb2,
    image_pb2_grpc,
    models_pb2,
    models_pb2_grpc,
    sample_pb2,
    shared_pb2,
    tokenize_pb2,
    tokenize_pb2_grpc,
    usage_pb2,
)

# All valid requests should use this API key.
API_KEY = "123"
MANAGEMENT_API_KEY = "456"
IMAGE_PATH = "test.jpg"


def read_image() -> bytes:
    path = os.path.join(os.path.dirname(__file__), IMAGE_PATH)
    with open(path, "rb") as f:
        return f.read()


def _check_auth(context: grpc.ServicerContext):
    """Raises an exception if the request isn't authenticated with the test API key."""
    headers = dict(context.invocation_metadata())
    if headers.get("authorization", "") != f"Bearer {API_KEY}":
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        raise grpc.RpcError()


def _check_management_auth(context: grpc.ServicerContext):
    """Raises an exception if the request isn't authenticated with the test management API key."""
    headers = dict(context.invocation_metadata())
    if headers.get("authorization", "") != f"Bearer {MANAGEMENT_API_KEY}":
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        raise grpc.RpcError()


class AuthServicer(auth_pb2_grpc.AuthServicer):
    """A dummy implementation of the Auth service for testing."""

    def __init__(self, initial_failures: int, response_delay_seconds: int = 0):
        self._initial_failures = initial_failures
        self._response_delay_seconds = response_delay_seconds

    def get_api_key_info(self, request, context: grpc.ServicerContext) -> auth_pb2.ApiKey:
        """Returns some information about an API key."""
        del request
        if self._initial_failures > 0:
            self._initial_failures -= 1
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.abort(grpc.StatusCode.UNAVAILABLE, "RPC failed on purpose.")

        _check_auth(context)

        return auth_pb2.ApiKey(
            redacted_api_key="1**",
            name="api key 0",
        )


class ChatServicer(chat_pb2_grpc.ChatServicer):
    """A dummy implementation of the Chat service for testing."""

    def __init__(self, response_delay_seconds: int = 0):
        self._response_delay_seconds = response_delay_seconds
        self._deferred_requests = {}
        self._stored_completions = {}

    def GetCompletion(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext):
        """Returns a static completion response."""
        _check_auth(context)

        if self._response_delay_seconds > 0:
            time.sleep(self._response_delay_seconds)

        response = chat_pb2.GetChatCompletionResponse(
            id=f"test-completion-{uuid.uuid4()}",
            model="dummy-model",
            created=timestamp_pb2.Timestamp(seconds=int(time.time())),
            system_fingerprint="dummy-fingerprint",
            usage=usage_pb2.SamplingUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            settings=chat_pb2.RequestSettings(temperature=0.5, top_p=0.9),
        )

        for i in range(request.n):
            if len(request.tools) > 0:
                response.choices.add(
                    finish_reason=sample_pb2.FinishReason.REASON_TOOL_CALLS,
                    index=i,
                    message=chat_pb2.CompletionMessage(
                        content="I am retrieving the weather for London in Celsius.",
                        role=chat_pb2.ROLE_ASSISTANT,
                        tool_calls=[
                            chat_pb2.ToolCall(
                                id="test-tool-call",
                                function=chat_pb2.FunctionCall(
                                    name=request.tools[0].function.name,
                                    arguments='{"city":"London","units":"C"}',
                                ),
                            )
                        ],
                    ),
                )
            elif request.response_format.format_type == chat_pb2.FormatType.FORMAT_TYPE_JSON_SCHEMA:
                response.choices.add(
                    finish_reason=sample_pb2.FinishReason.REASON_STOP,
                    index=i,
                    message=chat_pb2.CompletionMessage(
                        content="""{"city":"London","units":"C", "temperature": 20}""", role=chat_pb2.ROLE_ASSISTANT
                    ),
                )
            else:
                response.choices.add(
                    finish_reason=sample_pb2.FinishReason.REASON_STOP,
                    index=i,
                    message=chat_pb2.CompletionMessage(
                        content="Hello, this is a test response!", role=chat_pb2.ROLE_ASSISTANT
                    ),
                )

        if (
            request.search_parameters.mode
            in [
                chat_pb2.SearchMode.ON_SEARCH_MODE,
                chat_pb2.SearchMode.AUTO_SEARCH_MODE,
            ]
            and request.search_parameters.return_citations
        ):
            response.citations.extend(
                [
                    "test-citation-123",
                    "test-citation-456",
                    "test-citation-789",
                ]
            )

        if request.store_messages:
            self._stored_completions[response.id] = response

        return response

    def GetCompletionChunk(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext):
        """Streams dummy chunks of a response."""
        _check_auth(context)

        if self._response_delay_seconds > 0:
            time.sleep(self._response_delay_seconds)

        normal_chunks = ["Hello, ", "this is ", "a test ", "response!"]
        response_id = "test-chunk-456"
        created_time = timestamp_pb2.Timestamp(seconds=int(time.time()))

        function_call_chunks = [
            "I",
            " am",
            " retrieving",
            " the",
            " weather",
            " for",
            " London",
            " in",
            " Celsius",
            ".",
        ]

        chunks = normal_chunks if len(request.tools) == 0 else function_call_chunks

        for i, chunk in enumerate(chunks):
            for j in range(request.n):
                if len(request.tools) > 0:
                    if i < len(chunks) - 1:
                        yield chat_pb2.GetChatCompletionChunk(
                            id=response_id,
                            model="dummy-model",
                            created=created_time,
                            system_fingerprint="dummy-fingerprint",
                            choices=[
                                chat_pb2.ChoiceChunk(
                                    delta=chat_pb2.Delta(content=chunk),
                                    index=j,
                                    finish_reason=None,
                                )
                            ],
                        )
                    else:
                        # Yield the final content chunk
                        yield chat_pb2.GetChatCompletionChunk(
                            id=response_id,
                            model="dummy-model",
                            created=created_time,
                            system_fingerprint="dummy-fingerprint",
                            choices=[
                                chat_pb2.ChoiceChunk(
                                    delta=chat_pb2.Delta(content=chunk),
                                    index=j,
                                    finish_reason=None,
                                )
                            ],
                        )

                        # Yield the tool call chunk
                        yield chat_pb2.GetChatCompletionChunk(
                            id=response_id,
                            model="dummy-model",
                            created=created_time,
                            system_fingerprint="dummy-fingerprint",
                            choices=[
                                chat_pb2.ChoiceChunk(
                                    delta=chat_pb2.Delta(
                                        role=chat_pb2.ROLE_ASSISTANT,
                                        tool_calls=[
                                            chat_pb2.ToolCall(
                                                id="test-tool-call",
                                                function=chat_pb2.FunctionCall(
                                                    name=request.tools[0].function.name,
                                                    arguments='{"city":"London","units":"C"}',
                                                ),
                                            )
                                        ],
                                    ),
                                    index=j,
                                    finish_reason=sample_pb2.FinishReason.REASON_TOOL_CALLS,
                                )
                            ],
                        )
                elif request.search_parameters.mode in [
                    chat_pb2.SearchMode.ON_SEARCH_MODE,
                    chat_pb2.SearchMode.AUTO_SEARCH_MODE,
                ]:
                    yield chat_pb2.GetChatCompletionChunk(
                        id=response_id,
                        model="dummy-model",
                        created=created_time,
                        system_fingerprint="dummy-fingerprint",
                        choices=[
                            chat_pb2.ChoiceChunk(
                                delta=chat_pb2.Delta(content=chunk),
                                index=j,
                                finish_reason=None,
                            )
                        ],
                    )
                    if i == len(chunks) - 1:
                        yield chat_pb2.GetChatCompletionChunk(
                            id=response_id,
                            model="dummy-model",
                            created=created_time,
                            system_fingerprint="dummy-fingerprint",
                            choices=[
                                chat_pb2.ChoiceChunk(
                                    index=j,
                                    finish_reason=sample_pb2.FinishReason.REASON_STOP,
                                )
                            ],
                            citations=["test-citation-123", "test-citation-456", "test-citation-789"]
                            if request.search_parameters.return_citations
                            else [],
                        )
                else:
                    yield chat_pb2.GetChatCompletionChunk(
                        id=response_id,
                        model="dummy-model",
                        created=created_time,
                        system_fingerprint="dummy-fingerprint",
                        choices=[
                            chat_pb2.ChoiceChunk(
                                delta=chat_pb2.Delta(content=chunk, role=chat_pb2.ROLE_ASSISTANT),
                                index=j,
                                finish_reason=None if i < len(chunks) - 1 else sample_pb2.FinishReason.REASON_MAX_LEN,
                            )
                        ],
                    )

    def StartDeferredCompletion(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext):
        """Returns a deferred response with a fake request ID."""
        _check_auth(context)

        key = f"key-{len(self._deferred_requests)}"
        self._deferred_requests[key] = [request, 0]

        return deferred_pb2.StartDeferredResponse(request_id=key)

    def GetDeferredCompletion(self, request: deferred_pb2.GetDeferredRequest, context: grpc.ServicerContext):
        """Simulates a completed deferred response."""
        _check_auth(context)

        if request.request_id not in self._deferred_requests:
            context.abort(grpc.StatusCode.NOT_FOUND, "Invalid request ID")

        # Every request need to be polled three times.
        if self._deferred_requests[request.request_id][1] < 2:
            self._deferred_requests[request.request_id][1] += 1
            return chat_pb2.GetDeferredCompletionResponse(status=deferred_pb2.DeferredStatus.PENDING)

        response = chat_pb2.GetDeferredCompletionResponse(
            status=deferred_pb2.DeferredStatus.DONE,
            response=chat_pb2.GetChatCompletionResponse(
                id="deferred-789",
                model="dummy-model",
                created=timestamp_pb2.Timestamp(seconds=int(time.time())),
                system_fingerprint="dummy-fingerprint",
                usage=usage_pb2.SamplingUsage(prompt_tokens=8, completion_tokens=6, total_tokens=14),
            ),
        )

        for i in range(self._deferred_requests[request.request_id][0].n):
            response.response.choices.add(
                finish_reason=sample_pb2.FinishReason.REASON_MAX_CONTEXT,
                index=i,
                message=chat_pb2.CompletionMessage(
                    content="Hello, this is a test response!", role=chat_pb2.ROLE_ASSISTANT
                ),
            )
        return response

    def GetStoredCompletion(self, request: chat_pb2.GetStoredCompletionRequest, context: grpc.ServicerContext):
        """Returns a stored completion response."""
        _check_auth(context)

        if request.response_id not in self._stored_completions:
            context.abort(grpc.StatusCode.NOT_FOUND, "Response not found")

        return self._stored_completions[request.response_id]

    def DeleteStoredCompletion(self, request: chat_pb2.DeleteStoredCompletionRequest, context: grpc.ServicerContext):
        """Deletes a stored completion response."""
        _check_auth(context)

        if request.response_id not in self._stored_completions:
            context.abort(grpc.StatusCode.NOT_FOUND, "Response not found")

        del self._stored_completions[request.response_id]

        return chat_pb2.DeleteStoredCompletionResponse(response_id=request.response_id)


@dataclass
class ModelLibrary:
    language_models: dict[str, models_pb2.LanguageModel]
    embedding_models: dict[str, models_pb2.EmbeddingModel]
    image_generation_models: dict[str, models_pb2.ImageGenerationModel]


class ModelServicer(models_pb2_grpc.ModelsServicer):
    """A dummy implementation of the Models service for testing."""

    def __init__(self, model_library: Optional[ModelLibrary] = None):
        if model_library is None:
            model_library = ModelLibrary(
                language_models={},
                embedding_models={},
                image_generation_models={},
            )

        self._model_library = model_library

    def ListLanguageModels(self, request: empty_pb2.Empty, context: grpc.ServicerContext):
        _check_auth(context)
        del request

        return models_pb2.ListLanguageModelsResponse(models=list(self._model_library.language_models.values()))

    def GetLanguageModel(self, request: models_pb2.GetModelRequest, context: grpc.ServicerContext):
        _check_auth(context)

        if request.name not in self._model_library.language_models:
            context.abort(grpc.StatusCode.NOT_FOUND, "Model not found")

        return self._model_library.language_models[request.name]

    def ListEmbeddingModels(self, request: empty_pb2.Empty, context: grpc.ServicerContext):
        _check_auth(context)
        del request

        return models_pb2.ListEmbeddingModelsResponse(models=list(self._model_library.embedding_models.values()))

    def GetEmbeddingModel(self, request: models_pb2.GetModelRequest, context: grpc.ServicerContext):
        _check_auth(context)

        if request.name not in self._model_library.embedding_models:
            context.abort(grpc.StatusCode.NOT_FOUND, "Model not found")

        return self._model_library.embedding_models[request.name]

    def ListImageGenerationModels(self, request: empty_pb2.Empty, context: grpc.ServicerContext):
        _check_auth(context)
        del request

        return models_pb2.ListImageGenerationModelsResponse(
            models=list(self._model_library.image_generation_models.values())
        )

    def GetImageGenerationModel(self, request: models_pb2.GetModelRequest, context: grpc.ServicerContext):
        _check_auth(context)

        if request.name not in self._model_library.image_generation_models:
            context.abort(grpc.StatusCode.NOT_FOUND, "Model not found")

        return self._model_library.image_generation_models[request.name]


class TokenizeServicer(tokenize_pb2_grpc.TokenizeServicer):
    def TokenizeText(self, request: tokenize_pb2.TokenizeTextRequest, context: grpc.ServicerContext):
        _check_auth(context)

        return tokenize_pb2.TokenizeTextResponse(
            tokens=[
                tokenize_pb2.Token(token_id=1, string_token="Hello", token_bytes=b"test"),
                tokenize_pb2.Token(token_id=2, string_token=" world", token_bytes=b"test"),
                tokenize_pb2.Token(token_id=3, string_token="!", token_bytes=b"test"),
            ],
            model=request.model,
        )


class ImageServicer(image_pb2_grpc.ImageServicer):
    def __init__(self, url):
        self._url = url

    def GenerateImage(self, request: image_pb2.GenerateImageRequest, context: grpc.ServicerContext):
        _check_auth(context)

        if request.format == image_pb2.ImageFormat.IMG_FORMAT_URL:
            return image_pb2.ImageResponse(
                model=request.model,
                images=[
                    image_pb2.GeneratedImage(up_sampled_prompt=request.prompt, url=self._url) for _ in range(request.n)
                ],
            )
        else:
            return image_pb2.ImageResponse(
                model=request.model,
                images=[
                    image_pb2.GeneratedImage(
                        up_sampled_prompt=request.prompt,
                        base64="data:image/jpeg;base64," + base64.b64encode(read_image()).decode(),
                    )
                    for _ in range(request.n)
                ],
            )


class ImageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/foo.jpg":
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            try:
                self.wfile.write(read_image())
            except FileNotFoundError:
                self.send_error(404, "Image not found")
        else:
            self.send_error(404, "Not found")


class InMemoryStore:
    def __init__(self):
        # collection_id -> collection_metadata
        self.collections: dict[str, collections_pb2.CollectionMetadata] = {}
        # file_id -> document_metadata
        self.documents: dict[str, collections_pb2.DocumentMetadata] = {}

        # collection_id -> list of file_ids
        self.collection_documents: defaultdict[str, list[str]] = defaultdict(list)

    def clear(self):
        # Clear the collections and documents dictionaries.
        self.collections.clear()
        self.documents.clear()
        self.collection_documents.clear()


class CollectionsServicer(collections_pb2_grpc.CollectionsServicer):
    def __init__(self, store: Optional[InMemoryStore] = None):
        if store is None:
            store = InMemoryStore()

        self._store = store

        # Initialize the store with some dummy collections.
        self._store.collections = {
            "test-collection-1": collections_pb2.CollectionMetadata(
                collection_id="test-collection-1",
                collection_name="test-collection-1",
                created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                documents_count=2,
            ),
            "test-collection-2": collections_pb2.CollectionMetadata(
                collection_id="test-collection-2",
                collection_name="test-collection-2",
                created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                documents_count=2,
            ),
        }

        # Initialize the store with some dummy documents.
        self._store.documents = {
            "test-document-1": collections_pb2.DocumentMetadata(
                file_metadata=collections_pb2.FileMetadata(
                    file_id="test-file-1",
                    name="test-file-1",
                    size_bytes=100,
                    content_type="test",
                    created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                    expires_at=timestamp_pb2.Timestamp(seconds=int(time.time()) + 1000),
                    hash="test-hash-1",
                ),
                fields={"test-field-1": "test-value-1"},
                status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
            ),
            "test-document-2": collections_pb2.DocumentMetadata(
                file_metadata=collections_pb2.FileMetadata(
                    file_id="test-file-2",
                    name="test-file-2",
                    size_bytes=200,
                    content_type="test",
                    created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                    expires_at=timestamp_pb2.Timestamp(seconds=int(time.time()) + 1000),
                    hash="test-hash-2",
                ),
                fields={"test-field-2": "test-value-2"},
                status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
            ),
            "test-document-3": collections_pb2.DocumentMetadata(
                file_metadata=collections_pb2.FileMetadata(
                    file_id="test-file-3",
                    name="test-file-3",
                    size_bytes=300,
                    content_type="test",
                    created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                    expires_at=timestamp_pb2.Timestamp(seconds=int(time.time()) + 1000),
                    hash="test-hash-3",
                ),
                fields={"test-field-3": "test-value-3"},
                status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
            ),
            "test-document-4": collections_pb2.DocumentMetadata(
                file_metadata=collections_pb2.FileMetadata(
                    file_id="test-file-4",
                    name="test-file-4",
                    size_bytes=400,
                    content_type="test",
                    created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
                    expires_at=timestamp_pb2.Timestamp(seconds=int(time.time()) + 1000),
                    hash="test-hash-4",
                ),
                fields={"test-field-4": "test-value-4"},
                status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
            ),
        }

        # collection_id -> list of document_ids
        self._store.collection_documents = defaultdict(
            list,
            {
                "test-collection-1": ["test-document-1", "test-document-3"],
                "test-collection-2": ["test-document-2", "test-document-4"],
            },
        )

    def CreateCollection(self, request: collections_pb2.CreateCollectionRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        collection_to_create = collections_pb2.CollectionMetadata(
            collection_id=str(uuid.uuid4()),
            collection_name=request.collection_name,
            created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
            index_configuration=request.index_configuration,
            chunk_configuration=request.chunk_configuration,
        )

        self._store.collections[collection_to_create.collection_id] = collection_to_create

        return collections_pb2.CollectionMetadata(
            collection_id=collection_to_create.collection_id,
            collection_name=collection_to_create.collection_name,
            created_at=timestamp_pb2.Timestamp(seconds=int(time.time())),
            index_configuration=request.index_configuration,
            chunk_configuration=collection_to_create.chunk_configuration,
            documents_count=0,
        )

    def ListCollections(self, request: collections_pb2.ListCollectionsRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        all_collections = list(self._store.collections.values())
        if request.sort_by == collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_NAME:
            all_collections.sort(
                key=lambda x: x.collection_name, reverse=request.order == shared_pb2.Ordering.ORDERING_DESCENDING
            )
        elif request.sort_by == collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_AGE:
            all_collections.sort(
                key=lambda x: x.created_at.seconds, reverse=request.order == shared_pb2.Ordering.ORDERING_DESCENDING
            )

        return collections_pb2.ListCollectionsResponse(
            collections=all_collections,
            pagination_token=None,
        )

    def DeleteCollection(self, request: collections_pb2.DeleteCollectionRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.collection_id not in self._store.collections:
            context.abort(grpc.StatusCode.NOT_FOUND, "Collection not found")

        del self._store.collections[request.collection_id]

        return empty_pb2.Empty()

    def UpdateCollection(self, request: collections_pb2.UpdateCollectionRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.collection_id not in self._store.collections:
            context.abort(grpc.StatusCode.NOT_FOUND, "Collection not found")

        current_collection = self._store.collections[request.collection_id]
        self._store.collections[request.collection_id] = collections_pb2.CollectionMetadata(
            collection_id=request.collection_id,
            collection_name=request.collection_name or current_collection.collection_name,
            created_at=current_collection.created_at,
            chunk_configuration=request.chunk_configuration or current_collection.chunk_configuration,
            index_configuration=current_collection.index_configuration,
            documents_count=current_collection.documents_count,
        )

        return self._store.collections[request.collection_id]

    def GetCollectionMetadata(
        self, request: collections_pb2.GetCollectionMetadataRequest, context: grpc.ServicerContext
    ):
        _check_management_auth(context)

        if request.collection_id not in self._store.collections:
            context.abort(grpc.StatusCode.NOT_FOUND, "Collection not found")

        return self._store.collections[request.collection_id]

    def UploadDocument(self, request: collections_pb2.UploadDocumentRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        document_id = str(uuid.uuid4())
        self._store.documents[document_id] = collections_pb2.DocumentMetadata(
            file_metadata=collections_pb2.FileMetadata(
                file_id=document_id,
                name=request.name,
                size_bytes=len(request.data),
                content_type=request.content_type,
            ),
            fields=request.fields,
            status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
        )

        self._store.collection_documents[request.collection_id].append(document_id)

        return self._store.documents[document_id]

    def ListDocuments(self, request: collections_pb2.ListDocumentsRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.collection_id not in self._store.collection_documents:
            context.abort(grpc.StatusCode.NOT_FOUND, "Collection not found")

        document_ids = self._store.collection_documents[request.collection_id]
        documents = [self._store.documents[document_id] for document_id in document_ids]

        if request.sort_by == collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_NAME:
            documents.sort(
                key=lambda x: x.file_metadata.name, reverse=request.order == shared_pb2.Ordering.ORDERING_DESCENDING
            )

        elif request.sort_by == collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_AGE:
            documents.sort(
                key=lambda x: x.file_metadata.created_at.seconds,
                reverse=request.order == shared_pb2.Ordering.ORDERING_DESCENDING,
            )

        elif request.sort_by == collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_SIZE:
            documents.sort(
                key=lambda x: x.file_metadata.size_bytes,
                reverse=request.order == shared_pb2.Ordering.ORDERING_DESCENDING,
            )

        return collections_pb2.ListDocumentsResponse(
            documents=documents,
        )

    def GetDocumentMetadata(self, request: collections_pb2.GetDocumentMetadataRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.file_id not in self._store.collection_documents[request.collection_id]:
            context.abort(grpc.StatusCode.NOT_FOUND, "Document not found")

        return self._store.documents[request.file_id]

    def BatchGetDocuments(self, request: collections_pb2.BatchGetDocumentsRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        return collections_pb2.BatchGetDocumentsResponse(
            documents=[
                self._store.documents[file_id] for file_id in request.file_ids if file_id in self._store.documents
            ],
        )

    def AddDocumentToCollection(
        self, request: collections_pb2.AddDocumentToCollectionRequest, context: grpc.ServicerContext
    ):
        _check_management_auth(context)

        if request.file_id not in self._store.documents:
            context.abort(grpc.StatusCode.NOT_FOUND, "Document not found")

        self._store.collection_documents[request.collection_id].append(request.file_id)

        return empty_pb2.Empty()

    def RemoveDocumentFromCollection(
        self, request: collections_pb2.RemoveDocumentFromCollectionRequest, context: grpc.ServicerContext
    ):
        _check_management_auth(context)

        if request.file_id not in self._store.documents:
            context.abort(grpc.StatusCode.NOT_FOUND, "Document not found")

        self._store.collection_documents[request.collection_id].remove(request.file_id)

        return empty_pb2.Empty()

    def UpdateDocument(self, request: collections_pb2.UpdateDocumentRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.file_id not in self._store.documents:
            context.abort(grpc.StatusCode.NOT_FOUND, "Document not found")

        self._store.documents[request.file_id] = collections_pb2.DocumentMetadata(
            file_metadata=collections_pb2.FileMetadata(
                file_id=request.file_id,
                name=request.name,
                size_bytes=len(request.data),
                content_type=request.content_type,
            ),
            fields=request.fields,
            status=collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED,
        )

        return self._store.documents[request.file_id]

    def ReIndexDocument(self, request: collections_pb2.ReIndexDocumentRequest, context: grpc.ServicerContext):
        _check_management_auth(context)

        if request.file_id not in self._store.documents:
            context.abort(grpc.StatusCode.NOT_FOUND, "Document not found")

        return empty_pb2.Empty()


class DocumentServicer(documents_pb2_grpc.DocumentsServicer):
    def Search(self, request: documents_pb2.SearchRequest, context: grpc.ServicerContext):
        _check_auth(context)

        potential_matches = [
            documents_pb2.SearchMatch(
                file_id="test-file-1",
                chunk_id="test-chunk-1",
                chunk_content="test-chunk-content-1",
                score=0.5,
            ),
            documents_pb2.SearchMatch(
                file_id="test-file-1",
                chunk_id="test-chunk-2",
                chunk_content="test-chunk-content-2",
                score=0.7,
            ),
            documents_pb2.SearchMatch(
                file_id="test-file-2",
                chunk_id="test-chunk-3",
                chunk_content="test-chunk-content-3",
                score=0.3,
            ),
        ]

        test_matches = []
        if request.query == "test-query-1":
            test_matches.append(potential_matches[0])
            test_matches.append(potential_matches[1])
        elif request.query == "test-query-2":
            test_matches.append(potential_matches[2])
        else:
            test_matches = potential_matches

        if request.limit:
            test_matches = test_matches[: request.limit]

        return documents_pb2.SearchResponse(
            matches=test_matches,
        )


class TestServer(threading.Thread):
    def __init__(
        self,
        port: int,
        initial_failures: int,
        response_delay_seconds: int = 0,
        model_library: Optional[ModelLibrary] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._port = port
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        self._server.add_insecure_port(f"127.0.0.1:{self._port}")

        self._image_port = portpicker.pick_unused_port()
        self._image_server = http.server.HTTPServer(("", self._image_port), ImageHandler)

        auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(initial_failures), self._server)
        chat_pb2_grpc.add_ChatServicer_to_server(ChatServicer(response_delay_seconds), self._server)
        models_pb2_grpc.add_ModelsServicer_to_server(ModelServicer(model_library), self._server)
        tokenize_pb2_grpc.add_TokenizeServicer_to_server(TokenizeServicer(), self._server)
        image_pb2_grpc.add_ImageServicer_to_server(
            ImageServicer(f"http://localhost:{self._image_port}/foo.jpg"), self._server
        )
        documents_pb2_grpc.add_DocumentsServicer_to_server(DocumentServicer(), self._server)

    def stop(self):
        self._image_server.shutdown()
        self._server.stop(grace=1.0)

    def run(self):
        self._server.start()
        self._image_server.serve_forever()
        self._server.wait_for_termination()


class TestManagementServer(threading.Thread):
    def __init__(self, port: int, in_memory_store: Optional[InMemoryStore] = None):
        super().__init__()
        self._port = port
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        self._server.add_insecure_port(f"127.0.0.1:{self._port}")

        collections_pb2_grpc.add_CollectionsServicer_to_server(CollectionsServicer(in_memory_store), self._server)

    def stop(self):
        self._server.stop(grace=1.0)

    def run(self):
        self._server.start()
        self._server.wait_for_termination()


@contextlib.contextmanager
def run_test_server(
    initial_failures: int = 0,
    response_delay_seconds: int = 0,
    model_library: Optional[ModelLibrary] = None,
    in_memory_store: Optional[InMemoryStore] = None,
) -> Generator[int, None, None]:
    """Runs the test server in a dedicated thread and yields the port that the server runs on."""
    port = portpicker.pick_unused_port()
    server = TestServer(port, initial_failures, response_delay_seconds, model_library, in_memory_store)
    try:
        server.start()
        yield port
    finally:
        server.stop()
        server.join()


@contextlib.contextmanager
def run_test_management_server(
    in_memory_store: Optional[InMemoryStore] = None,
) -> Generator[int, None, None]:
    """Runs the test management server in a dedicated thread and yields the port that the server runs on."""
    port = portpicker.pick_unused_port()
    server = TestManagementServer(port, in_memory_store)
    try:
        server.start()
        yield port
    finally:
        server.stop()
        server.join()
