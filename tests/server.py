# flake8: noqa: N802

import base64
import contextlib
import http.server
import os.path
import threading
import time
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
    deferred_pb2,
    image_pb2,
    image_pb2_grpc,
    models_pb2,
    models_pb2_grpc,
    sample_pb2,
    tokenize_pb2,
    tokenize_pb2_grpc,
    usage_pb2,
)

# All valid requests should use this API key.
API_KEY = "123"
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

    def GetCompletion(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext):
        """Returns a static completion response."""
        _check_auth(context)

        if self._response_delay_seconds > 0:
            time.sleep(self._response_delay_seconds)

        response = chat_pb2.GetChatCompletionResponse(
            id="test-completion-123",
            model="dummy-model",
            created=timestamp_pb2.Timestamp(seconds=int(time.time())),
            system_fingerprint="dummy-fingerprint",
            usage=usage_pb2.SamplingUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
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
                                delta=chat_pb2.Delta(content=chunk),
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

    def stop(self):
        self._image_server.shutdown()
        self._server.stop(grace=0)

    def run(self):
        self._server.start()
        self._image_server.serve_forever()
        self._server.wait_for_termination()


@contextlib.contextmanager
def run_test_server(
    initial_failures: int = 0, response_delay_seconds: int = 0, model_library: Optional[ModelLibrary] = None
) -> Generator[int, None, None]:
    """Runs the test server in a dedicated thread and yields the port that the server runs on."""
    port = portpicker.pick_unused_port()
    server = TestServer(port, initial_failures, response_delay_seconds, model_library)
    try:
        server.start()
        yield port
    finally:
        server.stop()
        server.join()
