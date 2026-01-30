from typing import Literal, TypeAlias, Union

from ..proto import chat_pb2

__all__ = [
    "Content",
    "ImageDetail",
    "IncludeOption",
    "IncludeOptionMap",
    "ReasoningEffort",
    "ResponseFormat",
    "ToolMode",
]

ReasoningEffort: TypeAlias = Literal["low", "high"]
"""Reasoning effort level for models that support reasoning.

- "low": Uses fewer reasoning tokens, resulting in faster responses with less thorough analysis
- "high": Uses more reasoning tokens, resulting in slower responses with more thorough analysis
"""

ImageDetail: TypeAlias = Literal["auto", "low", "high"]
"""Image detail level for vision models.

- "auto": The system automatically selects an appropriate resolution
- "low": Uses low-resolution image processing, reducing token usage and increasing speed
- "high": Uses high-resolution image processing, increasing token usage but capturing more detail
"""

Content: TypeAlias = Union[str, chat_pb2.Content]
"""Content type for chat messages.

Can be either a plain string (automatically converted to text content) or a chat_pb2.Content
object (for images, files, or other structured content).
"""

ToolMode: TypeAlias = Literal["auto", "none", "required"]
"""Tool calling mode for chat requests.

- "auto": The model decides whether to call tools based on the conversation context (default)
- "none": The model will not call any tools and will only generate text responses
- "required": The model must call one or more tools before responding
"""


# json_schema purposefully omitted, since the `parse` method should be used when needing json_schema responses.
ResponseFormat: TypeAlias = Literal["text", "json_object"]
"""Response format type for chat completions.

- "text": The model returns plain text responses (default)
- "json_object": The model returns responses formatted as JSON objects

Note: For structured outputs with a specific JSON schema, use the `parse` method or pass a
Pydantic model to the `response_format` parameter instead.
"""

IncludeOption: TypeAlias = Literal[
    "web_search_call_output",
    "x_search_call_output",
    "code_execution_call_output",
    "collections_search_call_output",
    "attachment_search_call_output",
    "mcp_call_output",
    "inline_citations",
    "verbose_streaming",
]
"""Options for including additional information in chat responses.

- "web_search_call_output": Include detailed output from web search tool calls
- "x_search_call_output": Include detailed output from X (Twitter) search tool calls
- "code_execution_call_output": Include detailed output from code execution tool calls
- "collections_search_call_output": Include detailed output from collections search tool calls
- "attachment_search_call_output": Include detailed output from attachment search tool calls
- "mcp_call_output": Include detailed output from MCP (Model Context Protocol) tool calls
- "inline_citations": Include structured citation metadata with position information
- "verbose_streaming": Include additional streaming metadata for debugging
"""

IncludeOptionMap: dict[IncludeOption, "chat_pb2.IncludeOption"] = {
    "web_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_WEB_SEARCH_CALL_OUTPUT,
    "x_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_X_SEARCH_CALL_OUTPUT,
    "code_execution_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_CODE_EXECUTION_CALL_OUTPUT,
    "collections_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_COLLECTIONS_SEARCH_CALL_OUTPUT,
    "attachment_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_ATTACHMENT_SEARCH_CALL_OUTPUT,
    "mcp_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_MCP_CALL_OUTPUT,
    "inline_citations": chat_pb2.IncludeOption.INCLUDE_OPTION_INLINE_CITATIONS,
    "verbose_streaming": chat_pb2.IncludeOption.INCLUDE_OPTION_VERBOSE_STREAMING,
}
