# flake8: noqa: N802

from __future__ import annotations

def read_image(path: str | None = None) -> bytes:
    """
    Read an image file and return its contents as bytes.
    
    Args:
        path: Optional path to the image file. If not provided, returns a default test image.
    
    Returns:
        The image data as bytes.
    """
    if path is None:
        # Return a 1x1 transparent PNG as a default test image
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xfc\xff\xff?\x03\x00\x08\xfc\x02\xfe\x8b\x8c\x1e\x1e\x00\x00\x00\x00IEND\xaeB`\x82'
    
    with open(path, "rb") as f:
        return f.read()

import asyncio
import base64
import concurrent.futures
import contextlib
import dataclasses
import datetime
import io
import json
import http.server
import os
import portpicker
import pytest
import socket
import ssl
import sys
import tempfile
import threading
import time
import uuid
from concurrent import futures
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple, TypeVar, Union, cast, Type, Generic

import grpc
from google.protobuf import empty_pb2, timestamp_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.message import Message
from xai_sdk.proto.v6.sample_pb2 import FinishReason

T = TypeVar('T', bound=Message)

@dataclass
class ModelLibrary(Generic[T]):
    """A library of models for testing."""
    language_models: Dict[str, T] = field(default_factory=dict)
    embedding_models: Dict[str, T] = field(default_factory=dict)
    image_generation_models: Dict[str, T] = field(default_factory=dict)

# Test constants
API_KEY = "test-api-key-123"

# Mock gRPC modules
# Mock gRPC service stubs
class auth_pb2_grpc:
    @staticmethod
    def add_AuthServicer_to_server(servicer, server):
        pass

class chat_pb2_grpc:
    @staticmethod
    def add_ChatServicer_to_server(servicer, server):
        pass

class image_pb2_grpc:
    class ImageServicer:
        pass
        
    @staticmethod
    def add_ImageServicer_to_server(servicer, server):
        pass

# Mock servicer classes
class AuthServicer:
    def __init__(self, response_delay_seconds=0, initial_failures=0):
        self.response_delay_seconds = response_delay_seconds
        self.initial_failures = initial_failures
        self._calls = 0
        
    def get_api_key_info(self, request, context):
        """Returns some information about an API key."""
        self._calls += 1
        
        # Check API key from metadata
        metadata = dict(context.invocation_metadata())
        api_key = metadata.get('x-api-key') or metadata.get('authorization', '').replace('Bearer ', '')
        if api_key != API_KEY:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details('Invalid API key')
            return None
            
        # Simulate initial failures if configured
        if self._calls <= self.initial_failures:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details('Simulated initial failure')
            return None
            
        # Simulate response delay if configured
        if self.response_delay_seconds > 0:
            time.sleep(self.response_delay_seconds)
            
        # Create a mock API key response
        from xai_sdk.proto.v6 import auth_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        
        now = int(time.time())
        create_time = Timestamp()
        create_time.FromSeconds(now - 86400)  # Created 1 day ago
        
        return auth_pb2.ApiKey(
            redacted_api_key="1**",
            user_id="test-user-123",
            name="api key 0",
            create_time=create_time,
            modify_time=create_time,
            modified_by="test-user@example.com",
            team_id="test-team-123",
            acls=["*"],
            api_key_id="test-key-123",
            api_key_blocked=False,
            team_blocked=False,
            disabled=False
        )

class ChatServicer:
    def __init__(self, response_delay_seconds=0):
        self.response_delay_seconds = response_delay_seconds
        
    def GetCompletion(self, request, context):
        """Samples a response from the model and blocks until the response has been
        fully generated.
        """
        if self.response_delay_seconds > 0:
            import time
            time.sleep(self.response_delay_seconds)
            
        from xai_sdk.proto.v6 import chat_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        from xai_sdk.proto.v6.chat_pb2 import MessageRole
        from xai_sdk.proto.v6.sample_pb2 import FinishReason
        
        now = Timestamp()
        now.GetCurrentTime()
        
        # Create a response message using the correct message type
        response = chat_pb2.GetChatCompletionResponse()
        response.id = "test-completion-123"
        response.model = request.model
        response.created.CopyFrom(now)
        
        # Determine the number of responses to generate
        n = getattr(request, 'n', 1)
        
        # Check if this is a function calling request by looking for tools in the request
        is_function_calling = bool(getattr(request, 'tools', None))
        
        # Add choices for each response in the batch
        for i in range(n):
            choice = response.choices.add()
            choice.index = i
            
            if is_function_calling:
                # For function calling, return a tool call
                from xai_sdk.proto.v6.sample_pb2 import FinishReason
                choice.finish_reason = FinishReason.REASON_TOOL_CALLS
                choice.message.role = MessageRole.ROLE_ASSISTANT
                
                # Add tool call
                tool_call = choice.message.tool_calls.add()
                tool_call.id = "test-tool-call"
                tool_call.function.name = "get_weather"
                tool_call.function.arguments = '{"city":"London","units":"C"}'
                
                # Add content explaining the tool call
                choice.message.content = "I am retrieving the weather for London in Celsius."
                
                # Explicitly set finish reason in the choice
                choice.finish_reason = FinishReason.REASON_TOOL_CALLS
            elif hasattr(request, 'response_format') and hasattr(request.response_format, 'format_type') and \
                 request.response_format.format_type == chat_pb2.FormatType.FORMAT_TYPE_JSON_SCHEMA:
                # Handle structured output request with JSON schema
                choice.finish_reason = FinishReason.REASON_STOP
                choice.message.role = MessageRole.ROLE_ASSISTANT
                # Match the exact expected format with spaces after commas
                choice.message.content = '{"city":"London","units":"C", "temperature": 20}'
            else:
                # Check if this is a search request
                has_search = hasattr(request, 'search_parameters') and request.search_parameters is not None
                
                # Regular completion
                choice.finish_reason = FinishReason.REASON_STOP
                if n > 1:
                    # For batch requests, include the index in the response
                    choice.message.content = f"Hello, this is test response {i+1} of {n}!"
                else:
                    choice.message.content = "Hello, this is a test response!"
                choice.message.role = MessageRole.ROLE_ASSISTANT
                
                # Add citations if this is a search request with return_citations=True
                # Only add citations for the first choice in the batch to avoid duplicates
                if i == 0 and has_search and hasattr(request.search_parameters, 'return_citations') and request.search_parameters.return_citations:
                    # Add citations to the response
                    citation_ids = ["test-citation-123", "test-citation-456", "test-citation-789"]
                    for citation_id in citation_ids:
                        response.citations.append(citation_id)
        
        # Set usage
        response.usage.prompt_tokens = 10
        response.usage.completion_tokens = 8 * n  # Scale tokens with batch size
        response.usage.total_tokens = 10 + (8 * n)
        
        return response
        
    def GetCompletionChunk(self, request, context):
        from xai_sdk.proto.v6 import chat_pb2, sample_pb2, usage_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        from xai_sdk.proto.v6.chat_pb2 import MessageRole
        import sys
        import time
        
        # Apply response delay if configured
        if hasattr(self, 'response_delay_seconds') and self.response_delay_seconds > 0:
            time.sleep(self.response_delay_seconds)
        
        def debug_chunk(chunk, chunk_num):
            print(f"\n=== Sending chunk {chunk_num} ===", file=sys.stderr)
            print(f"Chunk ID: {chunk.id}", file=sys.stderr)
            print(f"Model: {chunk.model}", file=sys.stderr)
            print(f"Created: {chunk.created}", file=sys.stderr)
            print("Choices:", file=sys.stderr)
            for choice in chunk.choices:
                print(f"  - Index: {choice.index}", file=sys.stderr)
                if hasattr(choice, 'delta') and choice.delta is not None:
                    if hasattr(choice.delta, 'role'):
                        print(f"    Role: {choice.delta.role}", file=sys.stderr)
                    if hasattr(choice.delta, 'content'):
                        print(f"    Content: {choice.delta.content!r}", file=sys.stderr)
                if hasattr(choice, 'finish_reason') and choice.finish_reason is not None:
                    print(f"    Finish Reason: {choice.finish_reason}", file=sys.stderr)
            print("\n", file=sys.stderr)
        
        # Create a timestamp
        now = Timestamp()
        now.GetCurrentTime()
        
        # For streaming batch, the batch size is determined by the request's n field
        batch_size = request.n if request.n > 0 else 1
        
        # Check if this is a function calling request
        is_function_calling = bool(getattr(request, 'tools', None))
        
        # Check if this is a search request
        has_search = hasattr(request, 'search_parameters') and request.search_parameters is not None
        return_citations = has_search and hasattr(request.search_parameters, 'return_citations') and request.search_parameters.return_citations
        
        if is_function_calling:
            # For batch streaming, we need to handle multiple responses
            if batch_size > 1:
                # Define the content pieces for each chunk
                # Each tuple contains (content_for_first_item, content_for_second_item)
                chunk_contents = [
                    ("I", ""),
                    ("", "I"),
                    (" am", ""),
                    ("", " am"),
                    (" retrieving", ""),
                    ("", " retrieving"),
                    (" the", ""),
                    ("", " the"),
                    (" weather", ""),
                    ("", " weather"),
                    (" for", ""),
                    ("", " for"),
                    (" London", ""),
                    ("", " London"),
                    (" in", ""),
                    ("", " in"),
                    (" Celsius", ""),
                    ("", " Celsius"),
                    (".", ""),
                    ("", ""),  # Empty content for both in the last chunk
                ]
                
                # For batch streaming, we need to alternate between the two responses
                # Each tuple represents (delta1, delta2) for the two choices
                deltas = [
                    ("I", ""),      # First chunk: first choice gets "I", second gets nothing
                    ("", "I"),      # Second chunk: first choice gets nothing, second gets "I"
                    (" am", ""),    # Third chunk: first choice gets " am", second gets nothing
                    ("", " am"),    # And so on...
                    (" retrieving", ""),
                    ("", " retrieving"),
                    (" the", ""),
                    ("", " the"),
                    (" weather", ""),
                    ("", " weather"),
                    (" for", ""),
                    ("", " for"),
                    (" London", ""),
                    ("", " London"),
                    (" in", ""),
                    ("", " in"),
                    (" Celsius", ""),
                    ("", " Celsius"),
                    (".", ""),
                    ("", "")  # Final empty chunk for tool call
                ]
                
                for i, (delta1, delta2) in enumerate(deltas):
                    # First chunk for first choice
                    if delta1:
                        chunk = chat_pb2.GetChatCompletionChunk()
                        chunk.id = f"test-stream-id-{i}-0"
                        chunk.model = request.model
                        chunk.created.CopyFrom(now)
                        
                        choice = chunk.choices.add()
                        choice.index = 0
                        if i == 0:
                            choice.delta.role = MessageRole.ROLE_ASSISTANT
                        
                        choice.delta.content = delta1
                        
                        # Add tool call on last chunk for first choice
                        if i == len(deltas) - 1:
                            tool_call = choice.delta.tool_calls.add()
                            tool_call.function.name = "get_weather"
                            tool_call.function.arguments = '{"city":"London","units":"C"}'
                            # Set finish_reason on the chunk choice
                            choice.finish_reason = FinishReason.REASON_TOOL_CALLS
                        
                        yield chunk
                    
                    # Second chunk for second choice
                    if delta2 or (i == len(deltas) - 1):  # Always yield last chunk for finish_reason
                        chunk = chat_pb2.GetChatCompletionChunk()
                        chunk.id = f"test-stream-id-{i}-1"
                        chunk.model = request.model
                        chunk.created.CopyFrom(now)
                        
                        choice = chunk.choices.add()
                        choice.index = 1
                        if i == 0:
                            choice.delta.role = MessageRole.ROLE_ASSISTANT
                        
                        if delta2:
                            choice.delta.content = delta2
                        
                        if i == len(deltas) - 1:
                            # For function calling batch, both choices should have REASON_TOOL_CALLS
                            # as the test expects both responses to have tool calls
                            # Add tool call for the second choice
                            tool_call = choice.delta.tool_calls.add()
                            tool_call.function.name = "get_weather"
                            tool_call.function.arguments = '{"city":"London","units":"C"}'
                            # Set finish_reason on the chunk choice
                            choice.finish_reason = FinishReason.REASON_TOOL_CALLS
                            print(f"[DEBUG] Setting finish_reason for choice 1: {choice.finish_reason} ({type(choice.finish_reason).__name__})")
                        
                        yield chunk
                return
            
            # Single response function calling streaming mode
            content_pieces = [
                "I", " am", " retrieving", " the", " weather", " for", " London", " in", " Celsius", ".", ""
            ]
            
            for i, content in enumerate(content_pieces, 1):
                chunk = chat_pb2.GetChatCompletionChunk()
                chunk.id = "test-stream-id"
                chunk.model = request.model
                chunk.created.CopyFrom(now)
                
                choice = chunk.choices.add()
                choice.index = 0
                # Always set the role for each chunk
                choice.delta.role = MessageRole.ROLE_ASSISTANT
                
                if content:  # Only set content if not empty
                    choice.delta.content = content
                else:
                    # Last chunk contains the tool call
                    tool_call = choice.delta.tool_calls.add()
                    tool_call.function.name = "get_weather"
                    tool_call.function.arguments = '{"city":"London","units":"C"}'
                    choice.finish_reason = FinishReason.REASON_TOOL_CALLS
                
                print(f"\n=== Yielding function call chunk {i} ===", file=sys.stderr)
                debug_chunk(chunk, i)
                yield chunk
                
            return  # Exit early for function calling
                
        if batch_size > 1:
            # Batch streaming mode - alternate content between batch items
            content_pieces = [
                ("Hello, ", ""),  # First chunk - first item has content, second is empty
                ("", "Hello, "),  # Second chunk - first is empty, second has content
                ("this is ", ""),  # Third chunk - first has content, second is empty
                ("", "this is "),  # Fourth chunk - first is empty, second has content
                ("a test ", ""),   # Fifth chunk - first has content, second is empty
                ("", "a test "),   # Sixth chunk - first is empty, second has content
                ("response!", ""), # Seventh chunk - first has content, second is empty
                ("", "response!")  # Eighth chunk - first is empty, second has content
            ]
            
            # Track accumulated content for each batch item
            accumulated_content = ["", ""]
            
            for i, (first_content, second_content) in enumerate(content_pieces, 1):
                chunk = chat_pb2.GetChatCompletionChunk()
                chunk.id = "test-stream-id"
                chunk.model = request.model
                chunk.created.CopyFrom(now)
                
                # First batch item
                if first_content:
                    choice = chunk.choices.add()
                    choice.index = 0
                    if not accumulated_content[0]:  # Only set role for first content chunk
                        choice.delta.role = MessageRole.ROLE_ASSISTANT
                    choice.delta.content = first_content
                    accumulated_content[0] += first_content
                
                # Second batch item
                if second_content:
                    choice = chunk.choices.add()
                    choice.index = 1
                    if not accumulated_content[1]:  # Only set role for first content chunk
                        choice.delta.role = MessageRole.ROLE_ASSISTANT
                    choice.delta.content = second_content
                    accumulated_content[1] += second_content
                
                print(f"\n=== Yielding batch chunk {i} ===", file=sys.stderr)
                debug_chunk(chunk, i)
                yield chunk
        else:
            # Single stream mode - send all content in sequence
            content_pieces = ["Hello, ", "this is ", "a test ", "response!"]
            
            for i, content in enumerate(content_pieces, 1):
                chunk = chat_pb2.GetChatCompletionChunk()
                chunk.id = "test-stream-id"
                chunk.model = request.model
                chunk.created.CopyFrom(now)
                
                choice = chunk.choices.add()
                choice.index = 0
                if i == 1:  # Only set role for first chunk
                    choice.delta.role = MessageRole.ROLE_ASSISTANT
                choice.delta.content = content
                
                print(f"\n=== Yielding single chunk {i} ===", file=sys.stderr)
                debug_chunk(chunk, i)
                yield chunk
        
        # Final chunk with finish reason, citations, and usage
        chunk = chat_pb2.GetChatCompletionChunk()
        chunk.id = "test-stream-id"
        chunk.model = request.model
        chunk.created.CopyFrom(now)
        
        # Check if this is a search request with return_citations=True
        has_search = hasattr(request, 'search_parameters') and request.search_parameters is not None
        return_citations = has_search and hasattr(request.search_parameters, 'return_citations') and request.search_parameters.return_citations
        
        # Set finish reason for all choices in batch
        for i in range(batch_size):
            choice = chunk.choices.add()
            choice.index = i
            choice.finish_reason = FinishReason.REASON_STOP
            
            # Add citations if this is a search request with return_citations=True
            if return_citations:
                # Add citations to the final chunk
                citation_ids = ["test-citation-123", "test-citation-456", "test-citation-789"]
                for citation_id in citation_ids:
                    chunk.citations.append(citation_id)
        
        # Set usage
        usage = usage_pb2.SamplingUsage()
        usage.prompt_tokens = 10
        usage.completion_tokens = 10 * batch_size
        usage.total_tokens = 10 + (10 * batch_size)
        chunk.usage.CopyFrom(usage)
        
        yield chunk
        
    def StartDeferredCompletion(self, request, context):
        """Starts sampling of the model and immediately returns a response containing
        a request id. The request id may be used to poll
        the `GetDeferredCompletion` RPC.
        """
        if self.response_delay_seconds > 0:
            import time
            time.sleep(self.response_delay_seconds)
            
        from xai_sdk.proto.v6 import deferred_pb2
        
        response = deferred_pb2.StartDeferredResponse()
        
        # Check if this is a batch request by looking for the n parameter
        has_n = hasattr(request, 'n') and request.n > 1
        if has_n:
            response.request_id = f"test-request-batch-{request.n}"  # Include batch size in request ID
        else:
            response.request_id = "test-request-123"
            
        return response
        
    def GetDeferredCompletion(self, request, context):
        """Gets the result of a deferred completion started by calling `StartDeferredCompletion`.
        """
        if self.response_delay_seconds > 0:
            import time
            time.sleep(self.response_delay_seconds)
            
        from xai_sdk.proto.v6 import chat_pb2, deferred_pb2
        from google.protobuf.timestamp_pb2 import Timestamp
        
        now = Timestamp()
        now.GetCurrentTime()
        
        # Create the completion response
        completion = chat_pb2.GetChatCompletionResponse()
        completion.id = "test-completion-123"
        completion.model = "grok-3-latest"  # Hardcode the model for testing
        completion.created.CopyFrom(now)
        
        # Import enums
        from xai_sdk.proto.v6.sample_pb2 import FinishReason
        from xai_sdk.proto.v6.chat_pb2 import MessageRole
        
        # Check if this is a batch request by looking at the request_id
        # For batch requests, the request_id will contain the batch index
        is_batch = request.request_id.startswith("test-request-batch-")
        
        if is_batch:
            # For batch requests, add multiple choices with different indices
            batch_size = int(request.request_id.split("-")[-1])
            for i in range(batch_size):
                choice = completion.choices.add()
                choice.index = i
                choice.finish_reason = FinishReason.REASON_STOP
                choice.message.content = f"Hello, this is test response {i+1} of {batch_size}!"
                choice.message.role = MessageRole.ROLE_ASSISTANT
        else:
            # For single requests, add a single choice with index 0
            choice = completion.choices.add()
            choice.index = 0
            choice.finish_reason = FinishReason.REASON_STOP
            choice.message.content = "Hello, this is a test response!"
            choice.message.role = MessageRole.ROLE_ASSISTANT
        
        # Set usage
        completion.usage.prompt_tokens = 10
        completion.usage.completion_tokens = 8 * len(completion.choices)
        completion.usage.total_tokens = 18 * len(completion.choices)
        
        # Create the deferred response
        response = chat_pb2.GetDeferredCompletionResponse()
        response.response.CopyFrom(completion)
        response.status = deferred_pb2.DeferredStatus.DONE
        
        return response

class ModelServicer:
    def ListLanguageModels(self, request, context):
        """List all available language models."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        response = models_pb2.ListLanguageModelsResponse()
        
        # Add models from the test data
        model = response.models.add()
        model.name = "grok-2"
        model.aliases.extend(["grok-2"])
        model.version = "1.0.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.TEXT)
        model.prompt_text_token_price = 10
        model.created.GetCurrentTime()
        
        model = response.models.add()
        model.name = "grok-3-beta"
        model.aliases.extend(["grok-3", "grok-3-latest"])
        model.version = "1.0.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.TEXT)
        model.prompt_text_token_price = 10
        model.created.GetCurrentTime()
        
        return response
        
    def ListEmbeddingModels(self, request, context):
        """List all available embedding models."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        response = models_pb2.ListEmbeddingModelsResponse()
        
        # Add the test embedding model
        model = response.models.add()
        model.name = "embedding-beta"
        model.aliases.extend(["embedding-beta"])
        model.version = "1.0.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.EMBEDDING)
        model.prompt_text_token_price = 2
        model.created.GetCurrentTime()
        
        return response
        
    def ListImageGenerationModels(self, request, context):
        """List all available image generation models."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        response = models_pb2.ListImageGenerationModelsResponse()
        
        # Add the test image generation model
        model = response.models.add()
        model.name = "grok-2-image"
        model.aliases.extend(["grok-2-image"])
        model.version = "1.0.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.IMAGE)
        model.image_price = 100
        model.created.GetCurrentTime()
        
        return response
        
    def GetEmbeddingModel(self, request, context):
        """Get details of a specific embedding model."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        model = models_pb2.EmbeddingModel()
        model.name = request.name  # Use name field instead of id
        model.aliases.extend([request.name])
        model.version = "002"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.EMBEDDING)
        model.prompt_text_token_price = 2
        model.prompt_image_token_price = 0
        model.created.GetCurrentTime()
        model.system_fingerprint = "fp_345678"
        
        return model
        
    def GetImageGenerationModel(self, request, context):
        """Get details of a specific image generation model."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        model = models_pb2.ImageGenerationModel()
        model.name = request.name  # Use name field instead of id
        model.aliases.extend([request.name])
        model.version = "3.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.IMAGE)
        model.image_price = 100
        model.created.GetCurrentTime()
        model.max_prompt_length = 4000
        model.system_fingerprint = "fp_456789"
        
        return model
        
    def GetLanguageModel(self, request, context):
        """Get details of a specific language model."""
        from xai_sdk.proto.v6 import models_pb2
        from google.protobuf import timestamp_pb2
        
        # Get the Modality enum values
        Modality = models_pb2.Modality
        
        model = models_pb2.LanguageModel()
        model.name = request.name  # Use name field instead of id
        model.aliases.extend([request.name])
        model.version = "1.0"
        model.input_modalities.append(Modality.TEXT)
        model.output_modalities.append(Modality.TEXT)
        model.prompt_text_token_price = 10
        model.prompt_image_token_price = 100
        model.cached_prompt_token_price = 1
        model.completion_text_token_price = 30
        model.search_price = 50
        model.created.GetCurrentTime()
        model.max_prompt_length = 8000
        model.system_fingerprint = "fp_123456"
        
        return model

class TokenizeServicer:
    """A mock tokenization service for testing."""
    
    def TokenizeText(self, request, context):
        """Mock implementation of TokenizeText RPC.
        
        Args:
            request: A TokenizeTextRequest message.
            context: The gRPC context.
            
        Returns:
            A TokenizeTextResponse message with mock tokens.
        """
        from xai_sdk.proto.v6 import tokenize_pb2
        
        # Create response
        response = tokenize_pb2.TokenizeTextResponse()
        response.model = request.model or "mock-tokenizer"
        
        # Add expected tokens for the test case
        if request.text == "Hello, world!":
            # Add tokens as expected by the test
            token1 = response.tokens.add()
            token1.token_id = 1
            token1.string_token = "Hello"
            token1.token_bytes = b"test"
            
            token2 = response.tokens.add()
            token2.token_id = 2
            token2.string_token = " world"
            token2.token_bytes = b"test"
            
            token3 = response.tokens.add()
            token3.token_id = 3
            token3.string_token = "!"
            token3.token_bytes = b"test"
        else:
            # Fallback for other cases
            tokens = request.text.split()
            for i, token_text in enumerate(tokens, 1):
                token = response.tokens.add()
                token.token_id = i
                token.string_token = token_text
                token.token_bytes = token_text.encode('utf-8')

        return response

class ImageServicer(image_pb2_grpc.ImageServicer):
    """A mock image generation service for testing."""

    def __init__(self, port: int, http_port: int):
        """Initialize the image servicer with the given ports.

        Args:
            port: The gRPC server port
            http_port: The HTTP server port for serving test images
        """
        self.port = port
        self.http_port = http_port

    def GenerateImage(self, request, context):
        """Mock implementation of GenerateImage RPC.

        Args:
            request: A GenerateImageRequest message.
            context: The gRPC context.

        Returns:
            An ImageResponse message with mock image data.
        """
        from xai_sdk.proto.v6 import image_pb2
        import os

        # Create a mock image response
        response = image_pb2.ImageResponse()
        response.model = request.model or "grok-2-image"

        # Determine number of images to generate (default to 1)
        n = request.n if request.n > 0 else 1

        # Get image format (default to URL if not specified)
        # 1 = BASE64 format, 2 = URL format
        image_format = request.format if hasattr(request, 'format') and request.format is not None else 2

        for i in range(n):
            image = response.images.add()
            image.up_sampled_prompt = request.prompt or "A beautiful sunset"

            if image_format == 1:  # BASE64 format
                # Get the exact same PNG bytes as read_image() and encode as base64
                png_bytes = read_image()
                base64_encoded = base64.b64encode(png_bytes).decode('ascii')
                image.base64 = f"data:image/png;base64,{base64_encoded}"
            else:  # URL format
                # Return image URL pointing to our HTTP server
                image.url = f"http://localhost:{self.http_port}/test-image-1.png"

            # Set respect_moderation to True by default
            image.respect_moderation = True

        return response

class TestImageHandler(http.server.SimpleHTTPRequestHandler):
    """A simple HTTP request handler that serves test images."""
    
    test_image_dir = os.path.join(os.path.dirname(__file__), "test_images")
    
    def do_GET(self):
        """Handle GET requests for test images."""
        try:
            # Extract the filename from the path
            filename = os.path.basename(self.path)
            if not filename:
                self.send_error(404, "File not found")
                return
                
            # Only serve files from the test_images directory
            filepath = os.path.join(self.test_image_dir, filename)
            
            if not os.path.exists(filepath):
                self.send_error(404, f"File not found: {filename}")
                return
                
            # Serve the file
            with open(filepath, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")


class DocumentServicer:
    """A mock document service for testing document search functionality."""

    def Search(self, request, context):
        """Mock implementation of Search RPC.

        Args:
            request: A SearchRequest message.
            context: The gRPC context.

        Returns:
            A SearchResponse message with mock search results.
        """
        from xai_sdk.proto.v6 import documents_pb2

        # Create a mock search response
        response = documents_pb2.SearchResponse()

        # Handle different query cases
        if request.query == "test-query-1":
            # First match
            match = response.matches.add()
            match.file_id = "test-file-1"
            match.chunk_id = "test-chunk-1"
            match.chunk_content = "test-chunk-content-1"
            match.score = 0.5
            
            # Second match (only if not limited)
            if not request.limit or request.limit > 1:
                match = response.matches.add()
                match.file_id = "test-file-1"
                match.chunk_id = "test-chunk-2"
                match.chunk_content = "test-chunk-content-2"
                match.score = 0.4
                
        elif request.query == "test-query-2":
            # Single match for test-query-2
            match = response.matches.add()
            match.file_id = "test-file-2"
            match.chunk_id = "test-chunk-3"
            match.chunk_content = "test-chunk-content-3"
            match.score = 0.6
        else:
            # Default mock response for other queries
            match = response.matches.add()
            match.file_id = f"file_{request.query}"
            match.chunk_id = f"chunk_{request.query}"
            match.chunk_content = f"Search result for query: {request.query}"
            match.score = 0.7

        return response

class TestServer(threading.Thread):
    """A test gRPC server for integration testing XAI SDK clients.

    This server runs in a dedicated thread and provides mock implementations of all
    XAI gRPC services for testing client code without requiring a real backend.
    """

    def __init__(self, response_delay_seconds=0.0, enable_image_server=True, port=None, initial_failures=0):
        super().__init__(daemon=True)
        self._response_delay_seconds = int(response_delay_seconds)  # Convert to int for gRPC
        self._enable_image_server = enable_image_server
        self._port = int(port or portpicker.pick_unused_port())  # Ensure port is an int
        self._image_server_port = int(portpicker.pick_unused_port()) if enable_image_server else None  # Ensure port is an int
        self._initial_failures = initial_failures
        self._server = None
        self._image_server = None
        self._stop_event = threading.Event()
        self._server_thread = None
        self._startup_exception = None
        self._model_library: Optional[ModelLibrary] = None  # Will store the model library for testing

    @property
    def port(self) -> int:
        """Get the port number the server is running on."""
        return self._port

    @property
    def image_server_port(self) -> Optional[int]:
        """Get the port number the image server is running on."""
        return self._image_server_port

    @classmethod
    def add_AuthServicer_to_server(cls, servicer, server):
        """Add Auth service to the gRPC server."""
        from xai_sdk.proto.v6 import auth_pb2_grpc
        auth_pb2_grpc.add_AuthServicer_to_server(servicer, server)

    @classmethod
    def add_ChatServiceServicer_to_server(cls, servicer, server):
        """Add Chat service to the gRPC server."""
        from xai_sdk.proto.v6 import chat_pb2_grpc
        chat_pb2_grpc.add_ChatServicer_to_server(servicer, server)

    @classmethod
    def add_ModelsServiceServicer_to_server(cls, servicer, server):
        """Add Models service to the gRPC server."""
        from xai_sdk.proto.v6 import models_pb2_grpc
        models_pb2_grpc.add_ModelsServicer_to_server(servicer, server)

    @classmethod
    def add_TokenizeServiceServicer_to_server(cls, servicer, server):
        """Add Tokenize service to the gRPC server."""
        from xai_sdk.proto.v6 import tokenize_pb2_grpc
        tokenize_pb2_grpc.add_TokenizeServicer_to_server(servicer, server)

    @classmethod
    def add_ImageServiceServicer_to_server(cls, servicer, server):
        """Add Image service to the gRPC server."""
        from xai_sdk.proto.v6 import image_pb2_grpc
        image_pb2_grpc.add_ImageServicer_to_server(servicer, server)

    @classmethod
    def add_DocumentsServiceServicer_to_server(cls, servicer, server):
        """Add Documents service to the gRPC server."""
        try:
            from xai_sdk.proto.v6 import documents_pb2_grpc
            documents_pb2_grpc.add_DocumentsServicer_to_server(servicer, server)
        except ImportError:
            # Documents service is optional
            pass

    def _setup_servers(self) -> None:
        """Set up the gRPC and image servers."""
        try:
            # Create the gRPC server
            self._server = grpc.server(
                concurrent.futures.ThreadPoolExecutor(max_workers=10),  # type: ignore
                options=[
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ],
                maximum_concurrent_rpcs=10,
            )

            # Create servicers
            auth_servicer = AuthServicer(
                response_delay_seconds=self._response_delay_seconds,
                initial_failures=self._initial_failures
            )
            chat_servicer = ChatServicer(response_delay_seconds=self._response_delay_seconds)
            model_servicer = ModelServicer()
            tokenize_servicer = TokenizeServicer()

            # Register all service implementations
            self.add_AuthServicer_to_server(auth_servicer, self._server)
            self.add_ChatServiceServicer_to_server(chat_servicer, self._server)
            self.add_ModelsServiceServicer_to_server(model_servicer, self._server)
            self.add_TokenizeServiceServicer_to_server(tokenize_servicer, self._server)
            
            # Add ImageServicer if image server is enabled
            if self._enable_image_server and self._image_server_port is not None:
                image_servicer = ImageServicer(self._port, self._image_server_port)
                self.add_ImageServiceServicer_to_server(image_servicer, self._server)

            # Set up image server if enabled
            if self._enable_image_server and self._image_server_port is not None:
                try:
                    # Ensure we have a valid port as an integer
                    port = int(self._image_server_port or portpicker.pick_unused_port())
                    self._image_server_port = port

                    # Create test image directory if it doesn't exist
                    test_image_dir = os.path.join(os.path.dirname(__file__), "test_images")
                    os.makedirs(test_image_dir, exist_ok=True)
                    
                    # Create a test image file with the exact content the test expects
                    test_image_path = os.path.join(test_image_dir, "test-image-1.png")
                    if not os.path.exists(test_image_path):
                        with open(test_image_path, "wb") as f:
                            # This is the exact same PNG as in read_image()
                            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xfc\xff\xff?\x03\x00\x08\xfc\x02\xfe\x8b\x8c\x1e\x1e\x00\x00\x00\x00IEND\xaeB`\x82')

                    # Create and start the HTTP server
                    handler = TestImageHandler
                    handler.test_image_dir = test_image_dir
                    
                    self._image_server = http.server.HTTPServer(
                        ('127.0.0.1', port),
                        lambda *args, **kwargs: handler(*args, **kwargs)
                    )
                    
                    # Start the HTTP server in a separate thread
                    self._image_server_thread = threading.Thread(
                        target=self._image_server.serve_forever,
                        daemon=True
                    )
                    self._image_server_thread.start()
                    
                    print(f"Image server started on port {port}")
                except Exception as e:
                    print(f"Warning: Failed to start image server: {e}")
                    self._image_server = None
                    self._image_server_port = None
            
            # Only add Documents servicer if the module is available
            try:
                from xai_sdk.proto.v6 import documents_pb2_grpc
                self.add_DocumentsServiceServicer_to_server(DocumentServicer(), self._server)
            except ImportError:
                print("Documents service not available, skipping...")
            
            # Bind the server to the specified port and start it
            if self._server is not None:
                # Bind the server to the port first
                self._server.add_insecure_port(f'[::]:{self._port}')
                # Start the server
                self._server.start()
                print(f"gRPC server started on port {self._port}")
            
        except Exception as e:
            print(f"Error setting up servers: {e}")
            if hasattr(self, '_server') and self._server is not None:
                self._server.stop(0)
            if hasattr(self, '_image_server') and self._image_server is not None:
                self._image_server.shutdown()
                self._image_server.server_close()
            raise
        
        # Start the image server in a separate thread if we have one
        if self._image_server is not None:
            def serve_forever(server: http.server.HTTPServer, stopped: threading.Event) -> None:
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

    def run(self) -> None:
        """Run the test server in a background thread."""
        try:
            self._setup_servers()  # This now starts the gRPC server
            
            # Start image server if enabled
            if self._enable_image_server and self._image_server_port is not None and self._image_server is not None:
                try:
                    print(f"Starting image server on port {self._image_server_port}")
                    self._image_server.serve_forever(poll_interval=0.1)
                except Exception as e:
                    print(f"Warning: Failed to start image server: {e}")
                    self._image_server = None
            
            # Keep the server running until stopped
            self._stop_event.wait()
        except Exception as e:
            print(f"Error in server thread: {e}")
            import traceback
            traceback.print_exc()
            self._startup_exception = e
            raise

        # Shutdown image server
        if self._image_server is not None:
            try:
                self._image_server.shutdown()
                self._image_server.server_close()
                self._image_server = None
            except Exception as e:
                print(f"Error stopping image server: {e}")

    def _cleanup(self) -> None:
        """Clean up resources used by the server."""
        # Stop the gRPC server if it exists
        if hasattr(self, '_server') and self._server is not None:
            try:
                self._server.stop(0)
                print("gRPC server stopped")
            except Exception as e:
                print(f"Error stopping gRPC server: {e}")
        
        # Stop the image server if it exists
        if hasattr(self, '_image_server') and self._image_server is not None:
            try:
                self._image_server.shutdown()
                self._image_server.server_close()
                print("Image server stopped")
            except Exception as e:
                print(f"Error stopping image server: {e}")
            finally:
                self._image_server = None
        
        # Stop the image server thread if it exists
        if hasattr(self, '_image_server_thread') and self._image_server_thread is not None:
            if self._image_server_thread.is_alive():
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
    initial_failures: int = 0,
    model_library: Optional[ModelLibrary] = None,
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
        initial_failures: Number of initial failures to simulate before succeeding.

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
        initial_failures=initial_failures,
    )
    
    # Store the model library if provided
    if model_library is not None:
        server._model_library = model_library
    
    # Start the server
    server.start()
    
    # Give the server a moment to start
    time.sleep(0.5)  # Increased from 0.1 to 0.5 seconds
    
    # Verify the server is running
    if not server.is_alive():
        # Get server thread status if available
        if hasattr(server, '_server_thread') and server._server_thread:
            print(f"Server thread status: {server._server_thread.is_alive()}")
            if hasattr(server._server_thread, 'exception'):
                print(f"Server thread exception: {server._server_thread.exception()}")
        raise RuntimeError("Test server failed to start")
    time.sleep(0.5)
    
    try:
        # Get the actual port being used
        server_port = server.port
        yield server_port
    finally:
        server.stop()
        server.join(timeout=1.0)
