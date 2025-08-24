# flake8: noqa: N802

import base64
import contextlib
import io
import json
import os
import random
import re
import sys
import threading
import time
import traceback
import types
import uuid
from concurrent import futures
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from http import server as http_server
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Type, Union, TYPE_CHECKING, cast, TypeVar, Callable

import grpc
import portpicker

# Define protocol buffer message classes for type hints
class Empty:
    pass

class Timestamp:
    def GetCurrentTime(self) -> 'Timestamp':
        return self
    
    @staticmethod
    def FromDatetime(dt: datetime) -> 'Timestamp':
        return Timestamp()

class Status:
    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get('code', 0)
        self.message = kwargs.get('message', '')
        self.details = kwargs.get('details', [])

# Mock protocol buffer modules
empty_pb2 = types.SimpleNamespace(Empty=Empty)
timestamp_pb2 = types.SimpleNamespace(Timestamp=Timestamp)
status_pb2 = types.SimpleNamespace(Status=Status)

# Define mock protobuf modules to avoid import errors
try:
    from google.protobuf import empty_pb2 as _empty_pb2
    from google.protobuf import timestamp_pb2 as _timestamp_pb2
except ImportError:
    # Use our mocks if protobuf is not available
    empty_pb2 = types.SimpleNamespace(Empty=Empty)
    timestamp_pb2 = types.SimpleNamespace(Timestamp=Timestamp)

# Try to import PIL for image generation, but make it optional
try:
    from PIL import Image, ImageDraw  # type: ignore
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Import protocol buffer modules with fallback to mocks
try:
    from xai_sdk.proto import (
        auth_pb2,
        chat_pb2,
        chat_pb2_grpc,
        documents_pb2,
        documents_pb2_grpc,
        image_pb2,
        image_pb2_grpc,
        models_pb2,
        models_pb2_grpc,
        tokenize_pb2,
        tokenize_pb2_grpc,
    )
    
    # Import Protocol for type hints
    from typing import (
        Any, 
        Dict, 
        Iterable, 
        Iterator, 
        List, 
        Mapping, 
        Optional, 
        Protocol, 
        Type, 
        TypeVar, 
        Union,
        runtime_checkable,
        TYPE_CHECKING,
    )
    import sys

    # Protocol for protobuf message objects
    class _ProtoMessage(Protocol):
        def CopyFrom(self, other: Any) -> None: ...
        def MergeFrom(self, other: Any) -> None: ...
        def ParseFromString(self, data: bytes) -> None: ...
        def SerializeToString(self) -> bytes: ...
        def MergeFromString(self, data: bytes) -> None: ...
        def Clear(self) -> None: ...
        def IsInitialized(self) -> bool: ...
        def ListFields(self) -> list[Any]: ...
        def HasField(self, field_name: str) -> bool: ...
        def ClearField(self, field_name: str) -> None: ...
        def WhichOneof(self, oneof_group: str) -> str | None: ...
        def ByteSize(self) -> int: ...
        def ClearExtension(self, extension_handle: Any) -> None: ...
        def DiscardUnknownFields(self) -> None: ...

    # Protocol for repeated composite field containers
    class _RepeatedCompositeField(Protocol):
        def __getitem__(self, index: int) -> _ProtoMessage: ...
        def __len__(self) -> int: ...
        def __iter__(self) -> Iterator[_ProtoMessage]: ...
        def add(self, **kwargs: Any) -> _ProtoMessage: ...
    
    # Protocol for repeated scalar field containers
    class _RepeatedScalarField(Protocol):
        def __getitem__(self, index: int) -> Any: ...
        def __len__(self) -> int: ...
        def __iter__(self) -> Iterator[Any]: ...
        def append(self, value: Any) -> None: ...
        def extend(self, values: Iterable[Any]) -> None: ...

    # Type aliases for container types
    from typing import Any, TypeVar
    
    # Define type variables for the container types
    _T = TypeVar('_T')
    _M = TypeVar('_M', bound=_ProtoMessage)
    
    # Use Any for the container types to avoid complex generic type issues
    RepeatedCompositeFieldContainer = Any  # type: ignore
    RepeatedScalarFieldContainer = Any  # type: ignore

    # Fallback Protocol-based stubs when protobuf is not available
    class _FallbackRepeatedCompositeField(_RepeatedCompositeField):
        def __init__(self) -> None:
            self._items: list[_ProtoMessage] = []
    
        def __getitem__(self, index: int) -> _ProtoMessage:
            return self._items[index]
        
        def __len__(self) -> int:
            return len(self._items)
        
        def __iter__(self) -> Iterator[_ProtoMessage]:
            return iter(self._items)
        
        def add(self, **kwargs: Any) -> _ProtoMessage:
            # Create a simple dict-like object that can be used as a proto message
            msg = type('_ProtoMessage', (), {**kwargs, 'CopyFrom': lambda x: None})
            self._items.append(msg)  # type: ignore
            return msg  # type: ignore
    
    class _FallbackRepeatedScalarField(_RepeatedScalarField):
        def __init__(self) -> None:
            self._items: list[Any] = []
    
        def __getitem__(self, index: int) -> Any:
            return self._items[index]
        
        def __len__(self) -> int:
            return len(self._items)
        
        def __iter__(self) -> Iterator[Any]:
            return iter(self._items)
        
        def append(self, value: Any) -> None:
            self._items.append(value)
        
        def extend(self, values: Iterable[Any]) -> None:
            self._items.extend(values)
    
    # Export the appropriate implementations based on availability
    try:
        from google.protobuf.internal.containers import (
            RepeatedCompositeFieldContainer as _ProtoRepeatedCompositeField,
            RepeatedScalarFieldContainer as _ProtoRepeatedScalarField,
        )
        RepeatedCompositeFieldContainer = _ProtoRepeatedCompositeField  # type: ignore
        RepeatedScalarFieldContainer = _ProtoRepeatedScalarField  # type: ignore
    except ImportError:
        RepeatedCompositeFieldContainer = _FallbackRepeatedCompositeField  # type: ignore
        RepeatedScalarFieldContainer = _FallbackRepeatedScalarField  # type: ignore

except ImportError:
    # Create mock protocol buffer modules if imports fail
    from typing import Any, Dict, Generic, List, TypeVar, Union
    
    # Mock protobuf module for testing
    class MockPB2Module:
        # Role constants
        ROLE_ASSISTANT = "assistant"
        ROLE_USER = "user"
        ROLE_SYSTEM = "system"
        
        # Finish reason constants
        class FinishReason:
            REASON_STOP = "stop"
            REASON_LENGTH = "length"
            REASON_TOOL_CALLS = "tool_calls"
        
        class Message:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
                
            def CopyFrom(self, other):
                self.__dict__.update(other.__dict__)
                
            def MergeFrom(self, other):
                self.__dict__.update(other.__dict__)
                
            def ParseFromString(self, data):
                pass
                
            def SerializeToString(self):
                return b''
                
            def IsInitialized(self):
                return True
                
            def ListFields(self):
                return []
                
            def ClearField(self, field_name):
                if hasattr(self, field_name):
                    delattr(self, field_name)
                    
            def WhichOneof(self, oneof_group):
                return None
                
            def HasField(self, field_name):
                return hasattr(self, field_name)
                
            def Clear(self):
                self.__dict__.clear()
                
            def MergeFromString(self, data):
                pass
                
            def ByteSize(self):
                return 0
                
            def ClearExtension(self, extension_handle):
                pass
                
            def DiscardUnknownFields(self):
                pass
        
        # Chat message class
        class ChatMessage(Message):
            def __init__(self, role: str = "", content: str = "", **kwargs):
                super().__init__(**kwargs)
                self.role = role
                self.content = content
        
        # Completion message class
        class CompletionMessage(Message):
            def __init__(self, role: str = "", content: str = "", **kwargs):
                super().__init__(**kwargs)
                self.role = role
                self.content = content
        
        # Tool call class
        class ToolCall(Message):
            def __init__(self, id: str = "", type: str = "function", **kwargs):
                super().__init__(**kwargs)
                self.id = id
                self.type = type
        
        # Function call class
        class FunctionCall(Message):
            def __init__(self, name: str = "", arguments: str = "", **kwargs):
                super().__init__(**kwargs)
                self.name = name
                self.arguments = arguments
        
        # Format type class
        class FormatType:
            FORMAT_TYPE_UNSPECIFIED = 0
            FORMAT_TYPE_JSON = 1
            FORMAT_TYPE_JSON_SCHEMA = 2
        
        # Delta class for streaming
        class Delta(Message):
            def __init__(self, content: str = "", **kwargs):
                super().__init__(**kwargs)
                self.content = content
        
        # Choice chunk class for streaming
        class ChoiceChunk(Message):
            def __init__(self, index: int = 0, delta: Optional['MockPB2Module.Delta'] = None, **kwargs):
                super().__init__(**kwargs)
                self.index = index
                self.delta = delta or MockPB2Module.Delta()
        
        # Chat completion response class
        class GetChatCompletionResponse(Message):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.choices = []
                self.usage = None
        
        # Chat completion chunk class
        class GetChatCompletionChunk(Message):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.choices = []
        
        # Search mode class
        class SearchMode:
            SEARCH_MODE_UNSPECIFIED = 0
            SEARCH_MODE_SEMANTIC = 1
            SEARCH_MODE_KEYWORD = 2
        
        # Sampling usage class
        class SamplingUsage:
            def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0):
                self.prompt_tokens = prompt_tokens
                self.completion_tokens = completion_tokens
                self.total_tokens = total_tokens
        
        # Finish reason class
        class FinishReason:
            REASON_MAX_LEN = 'length'
        
        # Model class
        class Model:
            def __init__(self, name: str = ""):
                self.name = name
        
        # Language model class
        class LanguageModel(Model):
            pass
        
        # Embedding model class
        class EmbeddingModel(Model):
            pass
        
        # Image generation model class
        class ImageGenerationModel(Model):
            pass
        
        # List language models response class
        class ListLanguageModelsResponse:
            def __init__(self):
                self.models = []
        
        # List embedding models response class
        class ListEmbeddingModelsResponse:
            def __init__(self):
                self.models = []
        
        # List image generation models response class
        class ListImageGenerationModelsResponse:
            def __init__(self):
                self.models = []
        
        # Tokenize request class
        class TokenizeRequest:
            def __init__(self, text: str = ""):
                self.text = text
        
        # Token class
        class Token:
            def __init__(self, token_id: int = 0, string_token: str = "", token_bytes: bytes = b""):
                self.token_id = token_id
                self.string_token = string_token
                self.token_bytes = token_bytes
        
        # Tokenize response class
        class TokenizeResponse:
            def __init__(self):
                self.tokens = []
        
        # Generate image request class
        class GenerateImageRequest:
            def __init__(self, prompt: str = ""):
                self.prompt = prompt
        
        # Image response class
        class ImageResponse:
            class Image:
                def __init__(self, data: bytes = b""):
                    self.data = data
            
            def __init__(self):
                self.images = []
        
        # Image format class
        class ImageFormat:
            PNG = 0
            JPEG = 1
        
        # Generated image class
        class GeneratedImage:
            def __init__(self, data: bytes = b""):
                self.data = data
        
        # Document class
        class Document:
            def __init__(self, doc_id: str = ""):
                self.id = doc_id
        
        # List documents response class
        class ListDocumentsResponse:
            def __init__(self):
                self.documents = []
        
        # Search match class
        class SearchMatch:
            def __init__(self, score: float = 0.0, text: str = ""):
                self.score = score
                self.text = text
        
        # Search response class
        class SearchResponse:
            def __init__(self):
                self.matches = []
        
        # Get deferred request class
        class GetDeferredRequest:
            def __init__(self, request_id: str = ""):
                self.request_id = request_id
        
        # Cancel deferred request class
        class CancelDeferredRequest:
            def __init__(self, request_id: str = ""):
                self.request_id = request_id
        
        # Deferred status class
        class DeferredStatus:
            PENDING = 1
            COMPLETED = 2
            FAILED = 3
    
    # Initialize mock modules
    auth_pb2 = MockPB2Module()
    chat_pb2 = MockPB2Module()
    
    class MockGRPCModule:
        def __init__(self, name):
            self.__name__ = name
    
    # Initialize gRPC service stubs
    chat_pb2_grpc = MockGRPCModule('chat_pb2_grpc')
    documents_pb2 = MockPB2Module()
    documents_pb2_grpc = MockGRPCModule('documents_pb2_grpc')
    image_pb2 = MockPB2Module()
    image_pb2_grpc = MockGRPCModule('image_pb2_grpc')
    models_pb2 = MockPB2Module()
    models_pb2_grpc = MockGRPCModule('models_pb2_grpc')
    tokenize_pb2 = MockPB2Module()
    tokenize_pb2_grpc = MockGRPCModule('tokenize_pb2_grpc')
    
    # Add service classes
    class ChatServiceServicer:
        pass
        
    class ModelsServiceServicer:
        pass
        
    class TokenizeServicer:
        pass
        
    class ImageServiceServicer:
        pass
        
    class DocumentsServiceServicer:
        pass
    
    # Add service registration functions
    def add_ChatServiceServicer_to_server(servicer, server):
        pass
        
    def add_ModelsServiceServicer_to_server(servicer, server):
        pass
        
    def add_TokenizeServicer_to_server(servicer, server):
        pass
        
    def add_ImageServiceServicer_to_server(servicer, server):
        pass
        
    def add_DocumentsServiceServicer_to_server(servicer, server):
        pass
    
    # Add service references to gRPC modules
    chat_pb2_grpc.add_ChatServiceServicer_to_server = add_ChatServiceServicer_to_server
    models_pb2_grpc.add_ModelsServiceServicer_to_server = add_ModelsServiceServicer_to_server
    tokenize_pb2_grpc.add_TokenizeServicer_to_server = add_TokenizeServicer_to_server
    image_pb2_grpc.add_ImageServiceServicer_to_server = add_ImageServiceServicer_to_server
    documents_pb2_grpc.add_DocumentsServiceServicer_to_server = add_DocumentsServiceServicer_to_server
    
    # Add API key class
    class ApiKey:
        def __init__(self, key_id: str = "", key_secret: str = ""):
            self.key_id = key_id
            self.key_secret = key_secret
    
    # Add common enums and constants
    chat_pb2.ROLE_ASSISTANT = 'assistant'
    chat_pb2.ROLE_USER = 'user'
    chat_pb2.ROLE_SYSTEM = 'system'
    
    # Add mock classes for commonly used message types
    class MockChatMessage:
        def __init__(self, role='', content=''):
            self.role = role
            self.content = content
            
    chat_pb2.ChatMessage = MockChatMessage
    
    # Add mock enums
    class MockFormatType:
        TEXT = 0
        JSON = 1
        
    chat_pb2.FormatType = MockFormatType
    
    # Add mock message classes
    class MockDelta:
        def __init__(self, content='', role=''):
            self.content = content
            self.role = role
            
    class MockChoiceChunk:
        def __init__(self, index=0, delta=None, finish_reason=None):
            self.index = index
            self.delta = delta or MockDelta()
            self.finish_reason = finish_reason
            
    chat_pb2.Delta = MockDelta
    chat_pb2.ChoiceChunk = MockChoiceChunk
    
    # Add mock for sampling usage
    class MockSamplingUsage:
        def __init__(self, prompt_tokens=0, completion_tokens=0, total_tokens=0):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens
            
    usage_pb2 = type('usage_pb2', (), {'SamplingUsage': MockSamplingUsage})()
    
    # Add mock for finish reason
    class MockFinishReason:
        REASON_MAX_LEN = 'length'
        
    sample_pb2 = type('sample_pb2', (), {'FinishReason': MockFinishReason})()

# Mock any missing protobuf classes for testing
class MockDeferredPB2:
    class GetDeferredRequest:
        def __init__(self, request_id: str = ""):
            self.request_id = request_id
            
    class CancelDeferredRequest:
        def __init__(self, request_id: str = ""):
            self.request_id = request_id
            
    class DeferredStatus:
        PENDING = 1
        COMPLETED = 2
        FAILED = 3

# Create mock protobuf classes if not available
try:
    from xai_sdk.proto import deferred_pb2
except ImportError:
    deferred_pb2 = MockDeferredPB2()

# Create mock classes for other missing protobufs
class MockModelsPB2:
    class Model:
        def __init__(self, name: str = ""):
            self.name = name
    
    class LanguageModel(Model):
        pass
        
    class EmbeddingModel(Model):
        pass
        
    class ImageGenerationModel(Model):
        pass
    
    class ListLanguageModelsResponse:
        def __init__(self):
            self.models = []
            
    class ListEmbeddingModelsResponse:
        def __init__(self):
            self.models = []
            
    class ListImageGenerationModelsResponse:
        def __init__(self):
            self.models = []

class MockTokenizePB2:
    class TokenizeRequest:
        def __init__(self, text: str = ""):
            self.text = text
        
    class Token:
        def __init__(self, token_id: int = 0, string_token: str = "", token_bytes: bytes = b""):
            self.token_id = token_id
            self.string_token = string_token
            self.token_bytes = token_bytes
    
    class TokenizeResponse:
        def __init__(self):
            self.tokens = []
            
        def add(self):
            return self.tokens.append(MockTokenizePB2.Token())

class MockImagePB2:
    class GenerateImageRequest:
        def __init__(self, prompt: str = ""):
            self.prompt = prompt
            
    class ImageResponse:
        class Image:
            def __init__(self, data: bytes = b""):
                self.data = data
                
        def __init__(self):
            self.images = []
            
    class ImageFormat:
        PNG = 0
        JPEG = 1
        
    class GeneratedImage:
        def __init__(self, data: bytes = b""):
            self.data = data

class MockDocumentsPB2:
    class Document:
        def __init__(self, doc_id: str = ""):
            self.id = doc_id
            
    class ListDocumentsResponse:
        def __init__(self):
            self.documents = []
            
    class SearchMatch:
        def __init__(self, score: float = 0.0, text: str = ""):
            self.score = score
            self.text = text
            
    class SearchResponse:
        def __init__(self):
            self.matches = []

# Initialize mock protobufs if not available
if 'models_pb2' not in globals():
    models_pb2 = MockModelsPB2()
    
if 'tokenize_pb2' not in globals():
    tokenize_pb2 = MockTokenizePB2()
    
if 'image_pb2' not in globals():
    image_pb2 = MockImagePB2()
    
if 'documents_pb2' not in globals():
    documents_pb2 = MockDocumentsPB2()

# All valid requests should use this API key.
API_KEY = "123"
IMAGE_PATH = "test.jpg"


def read_image() -> bytes:
    path = os.path.join(os.path.dirname(__file__), IMAGE_PATH)
    with open(path, "rb") as f:
        return f.read()


def _check_auth(context: grpc.ServicerContext) -> None:
    """Raises an exception if the request isn't authenticated with the test API key."""
    headers = dict(context.invocation_metadata())
    if headers.get("authorization", "") != f"Bearer {API_KEY}":
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        raise grpc.RpcError()


class AuthServicer(auth_pb2_grpc.AuthServicer):
    """A dummy implementation of the Auth service for testing."""

    def __init__(self, initial_failures: int, response_delay_seconds: int = 0) -> None:
        self._initial_failures = initial_failures
        self._response_delay_seconds = response_delay_seconds

    def get_api_key_info(self, request: empty_pb2.Empty, context: grpc.ServicerContext) -> auth_pb2.ApiKey:
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
    """A dummy implementation of the Chat service for testing.
    
    This servicer provides mock implementations of chat completion endpoints with
    configurable response behavior including delays and error simulation.
    """

    MAX_COMPLETIONS = 10  # Maximum number of completions to return in a single request
    MAX_TOKENS = 4096     # Maximum tokens allowed in a single request
    
    def __init__(self, response_delay_seconds: int = 0):
        """Initialize the ChatServicer.
        
        Args:
            response_delay_seconds: Artificial delay to add to all responses (for testing timeouts).
        """
        if response_delay_seconds < 0:
            raise ValueError("response_delay_seconds must be non-negative")
            
        self._response_delay_seconds = response_delay_seconds
        self._deferred_requests: Dict[str, Any] = {}
        self._lock = threading.RLock()  # For thread-safe access to _deferred_requests

    def _validate_completion_request(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext) -> None:
        """Validate the completion request parameters.
        
        Args:
            request: The completion request to validate.
            context: The gRPC context for sending error responses.
            
        Raises:
            grpc.RpcError: If the request is invalid.
        """
        if not request.messages:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "At least one message is required")
            
        if request.n <= 0 or request.n > self.MAX_COMPLETIONS:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"n must be between 1 and {self.MAX_COMPLETIONS}"
            )
            
        if request.max_tokens and request.max_tokens > self.MAX_TOKENS:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"max_tokens cannot exceed {self.MAX_TOKENS}"
            )
            
        # Validate tool definitions if present
        for tool in request.tools:
            if not tool.function.name:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Tool function name is required")
                
    def _add_deferred_request(self, request_id: str, request_data: Any) -> None:
        """Thread-safely add a deferred request.
        
        Args:
            request_id: The unique identifier for the deferred request.
            request_data: The request data to store.
        """
        with self._lock:
            self._deferred_requests[request_id] = request_data
            
    def _get_deferred_request(self, request_id: str) -> Optional[Any]:
        """Thread-safely retrieve a deferred request.
        
        Args:
            request_id: The unique identifier for the deferred request.
            
        Returns:
            The stored request data, or None if not found.
        """
        with self._lock:
            return self._deferred_requests.get(request_id)
            
    def _remove_deferred_request(self, request_id: str) -> Optional[Any]:
        """Thread-safely remove and return a deferred request.
        
        Args:
            request_id: The unique identifier for the deferred request.
            
        Returns:
            The removed request data, or None if not found.
        """
        with self._lock:
            return self._deferred_requests.pop(request_id, None)
                
    def GetCompletion(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext) -> chat_pb2.GetChatCompletionResponse:
        """Returns a static completion response.
        
        Args:
            request: The completion request.
            context: The gRPC context.
            
        Returns:
            chat_pb2.GetChatCompletionResponse: The completion response.
            
        Raises:
            grpc.RpcError: If the request is invalid or an error occurs.
        """
        _check_auth(context)
        self._validate_completion_request(request, context)

        # Simulate response delay if configured
        if self._response_delay_seconds > 0:
            time.sleep(self._response_delay_seconds)
            
        # Check if context was cancelled during the delay
        if not context.is_active():
            # Context is no longer active, likely cancelled
            return chat_pb2.GetChatCompletionResponse()

        try:
            response = chat_pb2.GetChatCompletionResponse(
                id=f"test-completion-{int(time.time())}",
                model=request.model or "dummy-model",
                created=timestamp_pb2.Timestamp(seconds=int(time.time())),
                system_fingerprint="dummy-fingerprint",
                usage=usage_pb2.SamplingUsage(
                    prompt_tokens=sum(len(m.content) // 4 for m in request.messages) if request.messages else 10,
                    completion_tokens=5,  # Fixed for testing
                    total_tokens=0,  # Will be calculated below
                ),
            )
            response.usage.total_tokens = response.usage.prompt_tokens + response.usage.completion_tokens

            for i in range(request.n):
                if request.tools and len(request.tools) > 0:
                    response.choices.add(
                        finish_reason=sample_pb2.FinishReason.REASON_TOOL_CALLS,
                        index=i,
                        message=chat_pb2.CompletionMessage(
                            content="I am retrieving the weather for London in Celsius.",
                            role=chat_pb2.ROLE_ASSISTANT,
                            tool_calls=[
                                chat_pb2.ToolCall(
                                    id=f"test-tool-call-{i}",
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
                            content="""{"city":"London","units":"C", "temperature": 20}""",
                            role=chat_pb2.ROLE_ASSISTANT
                        ),
                    )
                else:
                    response.choices.add(
                        finish_reason=sample_pb2.FinishReason.REASON_STOP,
                        index=i,
                        message=chat_pb2.CompletionMessage(
                            content="Hello, this is a test response!",
                            role=chat_pb2.ROLE_ASSISTANT
                        ),
                    )
            
            return response
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return chat_pb2.GetChatCompletionResponse()

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

    def GetChatCompletionStreamResponse(self, request, context):
        """Streams a chat completion response.
        
        Args:
            request: The chat completion request.
            context: gRPC context.
            
        Yields:
            Chat completion stream responses.
        """
        _check_auth(context)
        
        if self._response_delay_seconds > 0:
            time.sleep(self._response_delay_seconds)
            
        # Create a simple response dictionary
        response = {
            'id': f"test-stream-{random.randint(1000, 9999)}",
            'created': {'seconds': int(time.time())},
            'model': getattr(request, 'model', 'dummy-model'),
            'system_fingerprint': "test-fingerprint"
        }
        
        # Add chunks
        chunks = [
            "Hello, ",
            "this is ",
            "a streaming ",
            "response!"
        ]
        
        for i, chunk in enumerate(chunks):
            # Create a chunk response
            chunk_resp = {
                'index': i,
                'delta': {'content': chunk}
            }
            
            # Create a response with the chunk
            response_with_chunk = dict(response)
            response_with_chunk['chunks'] = [chunk_resp]
            
            # Simulate network delay
            time.sleep(0.1)
            yield response_with_chunk

    def GetCompletionChunk(self, request, context):
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

    def StartDeferredChat(self, request: chat_pb2.GetCompletionsRequest, context: grpc.ServicerContext) -> chat_pb2.GetChatCompletionResponse:
        """Start a deferred chat request.
        
        Args:
            request: The chat completion request to defer.
            context: The gRPC context.
            
        Returns:
            chat_pb2.GetChatCompletionResponse: The initial response with request ID.
        """
        _check_auth(context)
        request_id = f"deferred-{int(time.time())}-{len(self._deferred_requests)}"
        self._add_deferred_request(request_id, (request, 0))  # (request, poll_count)
        
        # Return a minimal response with the request ID
        response = chat_pb2.GetChatCompletionResponse(
            id=request_id,
            model=request.model or "dummy-model",
            created=timestamp_pb2.Timestamp(seconds=int(time.time())),
            system_fingerprint="deferred-request",
            usage=usage_pb2.SamplingUsage(
                prompt_tokens=sum(len(m.content) // 4 for m in request.messages) if request.messages else 10,
                completion_tokens=0,
                total_tokens=0
            ),
        )
        return response

    def GetDeferredChatCompletion(self, request: deferred_pb2.GetDeferredRequest, context: grpc.ServicerContext) -> chat_pb2.GetChatCompletionResponse:
        """Get the completion for a deferred chat request.
        
        Args:
            request: The deferred chat request containing the request ID.
            context: The gRPC context.
            
        Returns:
            chat_pb2.GetChatCompletionResponse: The completion response.
            
        Raises:
            grpc.RpcError: If the request ID is not found.
        """
        _check_auth(context)
        deferred_request = self._get_deferred_request(request.request_id)
        if not deferred_request:
            context.abort(grpc.StatusCode.NOT_FOUND, "Request ID not found")
        return self.GetCompletion(deferred_request, context)

    def CancelDeferredChat(self, request: deferred_pb2.CancelDeferredRequest, context: grpc.ServicerContext) -> empty_pb2.Empty:
        """Cancel a deferred chat request.
        
        Args:
            request: The request containing the ID of the deferred request to cancel.
            context: The gRPC context.
            
        Returns:
            google.protobuf.empty_pb2.Empty: An empty response indicating success.
        """
        _check_auth(context)
        self._remove_deferred_request(request.request_id)
        return google.protobuf.empty_pb2.Empty()

    def GetDeferredCompletion(self, request: deferred_pb2.GetDeferredRequest, context: grpc.ServicerContext) -> chat_pb2.GetChatCompletionResponse:
        """Simulates a completed deferred response."""
        _check_auth(context)
        
        # Get the deferred request data
        deferred_data = self._get_deferred_request(request.request_id)
        if not deferred_data:
            context.abort(grpc.StatusCode.NOT_FOUND, "Invalid request ID")
            
        deferred_request, poll_count = deferred_data
        
        # Simulate processing delay by requiring multiple polls
        if poll_count < 2:
            # Update poll count
            self._add_deferred_request(request.request_id, (deferred_request, poll_count + 1))
            
            # Create a response with minimal required fields
            response = chat_pb2.GetChatCompletionResponse()
            response.id = request.request_id
            response.model = getattr(deferred_request, 'model', 'dummy-model')
            response.created.seconds = int(time.time())
            response.system_fingerprint = "deferred-pending"
            
            # Set usage if messages exist
            if hasattr(deferred_request, 'messages') and deferred_request.messages:
                prompt_tokens = sum(len(m.content) // 4 for m in deferred_request.messages)
            else:
                prompt_tokens = 10
                
            response.usage.prompt_tokens = prompt_tokens
            response.usage.completion_tokens = 0
            response.usage.total_tokens = prompt_tokens
            
            return response
            
        # On the third poll, return the actual completion and clean up
        self._remove_deferred_request(request.request_id)
        return self.GetCompletion(deferred_request, context)


# Define document service related classes first
class DocumentChunk:
    """Mock DocumentChunk message class."""
    def __init__(self) -> None:
        self.chunk_id = ""
        self.content = ""
        self.metadata: Dict[str, str] = {}

class ChunkEmbedding:
    """Mock ChunkEmbedding message class."""
    def __init__(self) -> None:
        self.document_id = ""
        self.chunk_id = ""
        self.embedding: List[float] = []
        
    def extend(self, items: List[float]) -> None:
        self.embedding.extend(items)

class ChunkSearchResult:
    """Mock ChunkSearchResult message class."""
    def __init__(self) -> None:
        self.chunk = DocumentChunk()
        self.score = 0.0
        self.matches: List[str] = []
        
    def append(self, match: str) -> None:
        self.matches.append(match)

class DocumentServicer:
    """Mock implementation of the DocumentsService."""
    
    def __init__(self) -> None:
        self.documents: Dict[str, Any] = {}
        self.chunks: Dict[str, List[DocumentChunk]] = {}
        self.embeddings: Dict[Tuple[str, str], List[float]] = {}
        self.image_generation_models: dict[str, dict] = {}
        
        # Add some test models
        self._add_test_models()
        
    def _add_test_models(self):
        """Add some test models to the library."""
        # Add a test language model
        self.image_generation_models["test-image-model"] = {
            'name': "test-image-model",
            'description': "A test image generation model",
            'max_resolution': "1024x1024"
        }


class ModelLibrary:
    """A simple in-memory model library for testing."""

    def __init__(self):
        # Initialize model stores with proper typing
        self.language_models: dict[str, dict] = {}
        self.embedding_models: dict[str, dict] = {}
        self.image_generation_models: dict[str, dict] = {}
        
        # Add some test models
        self._add_test_models()
        
    def _add_test_models(self):
        """Add some test models to the library."""
        # Add a test language model
        self.language_models["test-language-model"] = {
            'name': "test-language-model",
            'description': "A test language model",
            'max_tokens': 2048
        }
        
        # Add a test embedding model
        self.embedding_models["test-embedding-model"] = {
            'name': "test-embedding-model",
            'description': "A test embedding model",
            'dimensions': 768
        }
        
        # Add a test image generation model
        self.image_generation_models["test-image-model"] = {
            'name': "test-image-model",
            'description': "A test image generation model",
            'max_resolution': "1024x1024"
        }


class ModelServicer:
    """A dummy implementation of the Models service for testing."""

    def __init__(self, model_library: Optional[ModelLibrary] = None):
        if model_library is None:
            model_library = ModelLibrary()
        self._model_library = model_library

    def ListLanguageModels(self, request, context):
        """List all available language models."""
        response = models_pb2.ListLanguageModelsResponse()
        # Create a models list directly instead of using add()
        response.models = [
            {
                'id': model_id,
                'name': model_info.get('name', model_id),
                'description': model_info.get('description', ''),
                'max_tokens': model_info.get('max_tokens', 2048)
            }
            for model_id, model_info in self._model_library.language_models.items()
        ]
        return response

    def GetLanguageModel(self, request, context):
        """Get details for a specific language model."""
        _check_auth(context)

        model_info = self._model_library.language_models.get(request.name, {})
        
        # Return a dictionary with model details
        result = {
            'id': request.name,
            'name': request.name,
            'description': '',
            'max_tokens': 2048
        }
        
        # Update with model info if available
        if isinstance(model_info, dict):
            result.update({
                'name': model_info.get('name', request.name),
                'description': model_info.get('description', ''),
                'max_tokens': model_info.get('max_tokens', 2048)
            })
            
        return result

    def ListEmbeddingModels(self, request, context):
        """List all available embedding models."""
        _check_auth(context)
        return {
            'models': [
                {
                    'id': model_id,
                    'name': model_info.get('name', model_id),
                    'description': model_info.get('description', ''),
                    'dimensions': model_info.get('dimensions', 768)
                }
                for model_id, model_info in self._model_library.embedding_models.items()
            ]
        }

    def GetEmbeddingModel(self, request, context):
        """Get details for a specific embedding model."""
        _check_auth(context)

        model_info = self._model_library.embedding_models.get(request.name, {})
        
        # Return a dictionary with model details
        result = {
            'id': request.name,
            'name': request.name,
            'description': '',
            'dimensions': 768
        }
        
        # Update with model info if available
        if isinstance(model_info, dict):
            result.update({
                'name': model_info.get('name', request.name),
                'description': model_info.get('description', ''),
                'dimensions': model_info.get('dimensions', 768)
            })
            
        return result

    def ListImageGenerationModels(self, request, context):
        """List all available image generation models."""
        _check_auth(context)
        return {
            'models': [
                {
                    'id': model_id,
                    'name': model_info.get('name', model_id),
                    'description': model_info.get('description', ''),
                    'max_resolution': model_info.get('max_resolution', '1024x1024')
                }
                for model_id, model_info in self._model_library.image_generation_models.items()
            ]
        }

    def GetImageGenerationModel(self, request, context):
        """Get details for a specific image generation model."""
        _check_auth(context)

        model_info = self._model_library.image_generation_models.get(request.name, {})
        
        # Return a dictionary with model details
        result = {
            'id': request.name,
            'name': request.name,
            'description': '',
            'max_resolution': '1024x1024'
        }
        
        # Update with model info if available
        if isinstance(model_info, dict):
            result.update({
                'name': model_info.get('name', request.name),
                'description': model_info.get('description', ''),
                'max_resolution': model_info.get('max_resolution', '1024x1024')
            })
            
        return result


class TokenizeServicer(tokenize_pb2_grpc.TokenizeServicer):
    def TokenizeText(
        self, request: 'tokenize_pb2.TokenizeRequest', context: grpc.ServicerContext
    ) -> 'tokenize_pb2.TokenizeResponse':
        """Tokenizes the input text."""
        _check_auth(context)
        response = tokenize_pb2.TokenizeResponse()
        
        # Simple tokenization by whitespace for testing
        tokens = request.text.split()
        for i, token in enumerate(tokens):
            token_obj = tokenize_pb2.Token()
            token_obj.token_id = i
            token_obj.string_token = token
            token_obj.token_bytes = token.encode('utf-8')
            response.tokens.append(token_obj)
            
        return response


class ImageServicer(image_pb2_grpc.ImageServicer):
    def __init__(self, url):
        self._url = url

    def GenerateImage(
        self, request: 'image_pb2.GenerateImageRequest', context: grpc.ServicerContext
    ) -> 'image_pb2.ImageResponse':
        """Generates an image from a text prompt."""
        _check_auth(context)
        response = image_pb2.ImageResponse()
        
        if not HAS_PIL:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details("PIL/Pillow is not installed")
            return response
            
        try:
            # Create a simple test image
            img = Image.new('RGB', (256, 256), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            d.text((10, 10), request.prompt, fill=(255, 255, 0))
            
            # Save image to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            
            # Add to response
            img_response = response.images.add()
            img_response.data = img_byte_arr.getvalue()
            img_response.format = image_pb2.ImageFormat.PNG
            
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to generate image: {str(e)}")
            return response


class ImageRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP server for serving test images."""
    
    def do_GET(self):
        if self.path == "/test.jpg":
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.end_headers()
            
            # Generate a simple test image
            if HAS_PIL:
                img = Image.new('RGB', (100, 100), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                d.text((10, 10), "Test Image", fill=(255, 255, 0))
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                self.wfile.write(img_byte_arr.getvalue())
            else:
                # Fallback to a simple color block if PIL is not available
                self.wfile.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xd4\x00\x00\x00\x00IEND\xaeB`\x82")
            try:
                self.wfile.write(read_image())
            except FileNotFoundError:
                self.send_error(404, "Image not found")
        else:
            self.send_error(404, "Not found")


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
    """A test gRPC server for integration testing XAI SDK clients.
    
    This server runs in a dedicated thread and provides mock implementations of all
    XAI gRPC services for testing client code without requiring a real backend.
    """
    
    @staticmethod
    def add_AuthServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Auth service to the gRPC server."""
        if hasattr(auth_pb2_grpc, 'add_AuthServicer_to_server'):
            auth_pb2_grpc.add_AuthServicer_to_server(servicer, server)
        
    @staticmethod
    def add_ChatServiceServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Chat service to the gRPC server."""
        if hasattr(chat_pb2_grpc, 'add_ChatServiceServicer_to_server'):
            chat_pb2_grpc.add_ChatServiceServicer_to_server(servicer, server)
        
    @staticmethod
    def add_ModelsServiceServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Models service to the gRPC server."""
        if hasattr(models_pb2_grpc, 'add_ModelsServiceServicer_to_server'):
            models_pb2_grpc.add_ModelsServiceServicer_to_server(servicer, server)
        
    @staticmethod
    def add_TokenizeServiceServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Tokenize service to the gRPC server."""
        if hasattr(tokenize_pb2_grpc, 'add_TokenizeServicer_to_server'):
            tokenize_pb2_grpc.add_TokenizeServicer_to_server(servicer, server)
        
    @staticmethod
    def add_ImageServiceServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Image service to the gRPC server."""
        if hasattr(image_pb2_grpc, 'add_ImageServiceServicer_to_server'):
            image_pb2_grpc.add_ImageServiceServicer_to_server(servicer, server)
        
    @staticmethod
    def add_DocumentsServiceServicer_to_server(servicer: Any, server: Any) -> None:
        """Add Documents service to the gRPC server."""
        if hasattr(documents_pb2_grpc, 'add_DocumentsServiceServicer_to_server'):
            documents_pb2_grpc.add_DocumentsServiceServicer_to_server(servicer, server)

    def __init__(
        self,
        response_delay_seconds: float = 0.0,
        enable_image_server: bool = True,
        port: Optional[int] = None,
    ) -> None:
        """Initialize the test server.
        
        Args:
            response_delay_seconds: Delay in seconds before sending responses.
            enable_image_server: Whether to start an image server.
            port: Port to run the gRPC server on. If None, a random port will be chosen.
        """
        super().__init__(daemon=True)
        self._response_delay_seconds = response_delay_seconds
        self._enable_image_server = enable_image_server
        self._port = port or portpicker.pick_unused_port()
        self._image_server_port = portpicker.pick_unused_port()
        self._server: Optional[grpc.Server] = None
        self._image_server: Optional[http.server.HTTPServer] = None
        self._stop_event = threading.Event()
        self._server_thread: Optional[threading.Thread] = None
        self._image_server_thread: Optional[threading.Thread] = None

    @property
    def port(self) -> int:
        """Get the port number the server is running on."""
        return self._port

    @property
    def image_server_port(self) -> Optional[int]:
        """Get the port number the image server is running on."""
        return self._image_server_port if self._image_server else None

    def _setup_servers(self) -> None:
        """Set up the gRPC and image servers."""
        # Create gRPC server with thread pool
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),  # type: ignore
            options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ]
        )

        # Set up image server if port is specified
        if self._image_server_port is not None:
            try:
                self._image_server = ThreadingHTTPServer(('localhost', self._image_server_port), ImageRequestHandler)
                # Update image server port in case it was 0 (ephemeral port)
                self._image_server_port = self._image_server.server_port
            except Exception as e:
                print(f"Warning: Failed to start image server: {e}")
                self._image_server = None

        # Add services to the gRPC server
        auth_servicer = AuthServicer(
            response_delay_seconds=int(self._response_delay_seconds)
        )
        chat_servicer = ChatServicer(response_delay_seconds=self._response_delay_seconds)
        
        # Add servicers to server
        self.add_AuthServicer_to_server(auth_servicer, self._server)
        self.add_ChatServiceServicer_to_server(chat_servicer, self._server)
        self.add_ModelsServiceServicer_to_server(ModelServicer(), self._server)
        self.add_TokenizeServiceServicer_to_server(TokenizeServicer(), self._server)
        self.add_ImageServiceServicer_to_server(ImageServicer(self._image_server_port or 0), self._server)
        
        # Only add Documents servicer if the module is available
        try:
            from xai_sdk.proto.v6 import documents_pb2_grpc
            self.add_DocumentsServiceServicer_to_server(DocumentServicer(), self._server)
        except ImportError:
            print("Warning: Documents service not available, skipping")
            
        # Bind the server to the port
        self._server.add_insecure_port(f'[::]:{self._port}')
        
        # Start the image server in a separate thread if we have one
        if self._image_server is not None:
            def serve_forever(server: ThreadingHTTPServer, stopped: threading.Event) -> None:
                while not stopped.is_set():
                    try:
                        server.serve_forever(poll_interval=0.1)
                    except Exception as e:
                        if not stopped.is_set():
                            print(f"Error in image server: {e}")
                            time.sleep(1)  # Prevent tight loop on repeated errors
            
            self._image_server_thread = threading.Thread(
                target=serve_forever,
                args=(self._image_server, self._stop_event),
                daemon=True
            )
            self._image_server_thread.start()
        
        # Wait for stop signal
        while not self._stop_event.is_set():
            time.sleep(0.1)
            
        # Cleanup
        self._cleanup()

    def _cleanup(self) -> None:
        """Clean up server resources."""
        # Shutdown gRPC server
        if self._server is not None:
            try:
                self._server.stop(0.5)  # 500ms grace period
                self._server = None
            except Exception as e:
                print(f"Error stopping gRPC server: {e}")
        
        # Shutdown image server
        if self._image_server is not None:
            try:
                self._image_server.shutdown()
                self._image_server.server_close()
                self._image_server = None
            except Exception as e:
                print(f"Error stopping image server: {e}")
        
        # Wait for image server thread to finish
        if self._image_server_thread is not None and self._image_server_thread.is_alive():
            self._image_server_thread.join(timeout=1.0)
            self._image_server_thread = None

    def start(self) -> None:
        """Start the test server in a background thread."""
        if self.is_alive():
            return
            
        self._stop_event.clear()
        super().start()
        
        # Wait for server to be ready
        time.sleep(0.1)
    
    def stop(self, grace: float = 5.0) -> None:
        """Stop the test server.
        
        Args:
            grace: Grace period in seconds to wait for server shutdown.
        """
        if self._stop_event.is_set():
            return
            
        self._stop_event.set()
        
        # Wait for thread to finish
        if self.is_alive():
            self.join(timeout=grace)
        
        # Ensure cleanup happened
        self._cleanup()


@contextlib.contextmanager
def run_test_server(
    port: Optional[int] = None,
    response_delay_seconds: float = 0.0,
    enable_image_server: bool = True,
    host: str = "127.0.0.1",
    max_workers: int = 1,
) -> Generator[int, None, None]:
    """Run the test server in a dedicated thread and yield the port number.

    This context manager creates and starts a test server in a background thread,
    yields the port number it's running on, and ensures proper cleanup when the
    context is exited.

    Args:
        port: Port to run the server on. If None, a random port will be chosen.
        response_delay_seconds: Delay in seconds before sending responses.
        enable_image_server: Whether to start an image server.
        host: Host address to bind the server to.
        max_workers: Maximum number of worker threads for the gRPC server.

    Yields:
        int: The port number the server is running on.

    Example:
        with run_test_server() as port:
            # Use the server on localhost:{port}
            client = Client(api_key="test")
            response = client.auth.get_api_key_info()
    """
    # Create and configure the test server
    server = TestServer(
        response_delay_seconds=response_delay_seconds,
        enable_image_server=enable_image_server,
        port=port,
    )
    
    # Start the server
    server.start()
    
    # Give the server a moment to start
    time.sleep(0.1)
    
    # Verify the server is running
    if not server.is_alive():
        raise RuntimeError("Test server failed to start")
    time.sleep(0.5)
    
    try:
        # Get the actual port being used
        server_port = server.port
        yield server_port
    finally:
        server.stop()
        server.join(timeout=1.0)
