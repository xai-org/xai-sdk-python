from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerSideTool(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SERVER_SIDE_TOOL_INVALID: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_WEB_SEARCH: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_X_SEARCH: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_CODE_EXECUTION: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_VIEW_IMAGE: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_VIEW_X_VIDEO: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_COLLECTIONS_SEARCH: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_MCP: _ClassVar[ServerSideTool]
    SERVER_SIDE_TOOL_ATTACHMENT_SEARCH: _ClassVar[ServerSideTool]
SERVER_SIDE_TOOL_INVALID: ServerSideTool
SERVER_SIDE_TOOL_WEB_SEARCH: ServerSideTool
SERVER_SIDE_TOOL_X_SEARCH: ServerSideTool
SERVER_SIDE_TOOL_CODE_EXECUTION: ServerSideTool
SERVER_SIDE_TOOL_VIEW_IMAGE: ServerSideTool
SERVER_SIDE_TOOL_VIEW_X_VIDEO: ServerSideTool
SERVER_SIDE_TOOL_COLLECTIONS_SEARCH: ServerSideTool
SERVER_SIDE_TOOL_MCP: ServerSideTool
SERVER_SIDE_TOOL_ATTACHMENT_SEARCH: ServerSideTool

class SamplingUsage(_message.Message):
    __slots__ = ("completion_tokens", "reasoning_tokens", "prompt_tokens", "total_tokens", "prompt_text_tokens", "cached_prompt_text_tokens", "prompt_image_tokens", "num_sources_used", "server_side_tools_used")
    COMPLETION_TOKENS_FIELD_NUMBER: _ClassVar[int]
    REASONING_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TEXT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    CACHED_PROMPT_TEXT_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PROMPT_IMAGE_TOKENS_FIELD_NUMBER: _ClassVar[int]
    NUM_SOURCES_USED_FIELD_NUMBER: _ClassVar[int]
    SERVER_SIDE_TOOLS_USED_FIELD_NUMBER: _ClassVar[int]
    completion_tokens: int
    reasoning_tokens: int
    prompt_tokens: int
    total_tokens: int
    prompt_text_tokens: int
    cached_prompt_text_tokens: int
    prompt_image_tokens: int
    num_sources_used: int
    server_side_tools_used: _containers.RepeatedScalarFieldContainer[ServerSideTool]
    def __init__(self, completion_tokens: _Optional[int] = ..., reasoning_tokens: _Optional[int] = ..., prompt_tokens: _Optional[int] = ..., total_tokens: _Optional[int] = ..., prompt_text_tokens: _Optional[int] = ..., cached_prompt_text_tokens: _Optional[int] = ..., prompt_image_tokens: _Optional[int] = ..., num_sources_used: _Optional[int] = ..., server_side_tools_used: _Optional[_Iterable[_Union[ServerSideTool, str]]] = ...) -> None: ...

class EmbeddingUsage(_message.Message):
    __slots__ = ("num_text_embeddings", "num_image_embeddings")
    NUM_TEXT_EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    NUM_IMAGE_EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    num_text_embeddings: int
    num_image_embeddings: int
    def __init__(self, num_text_embeddings: _Optional[int] = ..., num_image_embeddings: _Optional[int] = ...) -> None: ...
