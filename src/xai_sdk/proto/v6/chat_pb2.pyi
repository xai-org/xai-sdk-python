from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import deferred_pb2 as _deferred_pb2
from . import documents_pb2 as _documents_pb2
from . import image_pb2 as _image_pb2
from . import sample_pb2 as _sample_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IncludeOption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INCLUDE_OPTION_INVALID: _ClassVar[IncludeOption]
    INCLUDE_OPTION_WEB_SEARCH_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_X_SEARCH_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_CODE_EXECUTION_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_COLLECTIONS_SEARCH_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_ATTACHMENT_SEARCH_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_MCP_CALL_OUTPUT: _ClassVar[IncludeOption]
    INCLUDE_OPTION_INLINE_CITATIONS: _ClassVar[IncludeOption]
    INCLUDE_OPTION_VERBOSE_STREAMING: _ClassVar[IncludeOption]

class MessageRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_ROLE: _ClassVar[MessageRole]
    ROLE_USER: _ClassVar[MessageRole]
    ROLE_ASSISTANT: _ClassVar[MessageRole]
    ROLE_SYSTEM: _ClassVar[MessageRole]
    ROLE_FUNCTION: _ClassVar[MessageRole]
    ROLE_TOOL: _ClassVar[MessageRole]
    ROLE_DEVELOPER: _ClassVar[MessageRole]

class ReasoningEffort(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_EFFORT: _ClassVar[ReasoningEffort]
    EFFORT_LOW: _ClassVar[ReasoningEffort]
    EFFORT_MEDIUM: _ClassVar[ReasoningEffort]
    EFFORT_HIGH: _ClassVar[ReasoningEffort]

class ToolMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TOOL_MODE_INVALID: _ClassVar[ToolMode]
    TOOL_MODE_AUTO: _ClassVar[ToolMode]
    TOOL_MODE_NONE: _ClassVar[ToolMode]
    TOOL_MODE_REQUIRED: _ClassVar[ToolMode]

class FormatType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORMAT_TYPE_INVALID: _ClassVar[FormatType]
    FORMAT_TYPE_TEXT: _ClassVar[FormatType]
    FORMAT_TYPE_JSON_OBJECT: _ClassVar[FormatType]
    FORMAT_TYPE_JSON_SCHEMA: _ClassVar[FormatType]

class ToolCallType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TOOL_CALL_TYPE_INVALID: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_CLIENT_SIDE_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_WEB_SEARCH_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_X_SEARCH_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_CODE_EXECUTION_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_COLLECTIONS_SEARCH_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_MCP_TOOL: _ClassVar[ToolCallType]
    TOOL_CALL_TYPE_ATTACHMENT_SEARCH_TOOL: _ClassVar[ToolCallType]

class ToolCallStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TOOL_CALL_STATUS_IN_PROGRESS: _ClassVar[ToolCallStatus]
    TOOL_CALL_STATUS_COMPLETED: _ClassVar[ToolCallStatus]
    TOOL_CALL_STATUS_INCOMPLETE: _ClassVar[ToolCallStatus]
    TOOL_CALL_STATUS_FAILED: _ClassVar[ToolCallStatus]

class SearchMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_SEARCH_MODE: _ClassVar[SearchMode]
    OFF_SEARCH_MODE: _ClassVar[SearchMode]
    ON_SEARCH_MODE: _ClassVar[SearchMode]
    AUTO_SEARCH_MODE: _ClassVar[SearchMode]
INCLUDE_OPTION_INVALID: IncludeOption
INCLUDE_OPTION_WEB_SEARCH_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_X_SEARCH_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_CODE_EXECUTION_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_COLLECTIONS_SEARCH_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_ATTACHMENT_SEARCH_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_MCP_CALL_OUTPUT: IncludeOption
INCLUDE_OPTION_INLINE_CITATIONS: IncludeOption
INCLUDE_OPTION_VERBOSE_STREAMING: IncludeOption
INVALID_ROLE: MessageRole
ROLE_USER: MessageRole
ROLE_ASSISTANT: MessageRole
ROLE_SYSTEM: MessageRole
ROLE_FUNCTION: MessageRole
ROLE_TOOL: MessageRole
ROLE_DEVELOPER: MessageRole
INVALID_EFFORT: ReasoningEffort
EFFORT_LOW: ReasoningEffort
EFFORT_MEDIUM: ReasoningEffort
EFFORT_HIGH: ReasoningEffort
TOOL_MODE_INVALID: ToolMode
TOOL_MODE_AUTO: ToolMode
TOOL_MODE_NONE: ToolMode
TOOL_MODE_REQUIRED: ToolMode
FORMAT_TYPE_INVALID: FormatType
FORMAT_TYPE_TEXT: FormatType
FORMAT_TYPE_JSON_OBJECT: FormatType
FORMAT_TYPE_JSON_SCHEMA: FormatType
TOOL_CALL_TYPE_INVALID: ToolCallType
TOOL_CALL_TYPE_CLIENT_SIDE_TOOL: ToolCallType
TOOL_CALL_TYPE_WEB_SEARCH_TOOL: ToolCallType
TOOL_CALL_TYPE_X_SEARCH_TOOL: ToolCallType
TOOL_CALL_TYPE_CODE_EXECUTION_TOOL: ToolCallType
TOOL_CALL_TYPE_COLLECTIONS_SEARCH_TOOL: ToolCallType
TOOL_CALL_TYPE_MCP_TOOL: ToolCallType
TOOL_CALL_TYPE_ATTACHMENT_SEARCH_TOOL: ToolCallType
TOOL_CALL_STATUS_IN_PROGRESS: ToolCallStatus
TOOL_CALL_STATUS_COMPLETED: ToolCallStatus
TOOL_CALL_STATUS_INCOMPLETE: ToolCallStatus
TOOL_CALL_STATUS_FAILED: ToolCallStatus
INVALID_SEARCH_MODE: SearchMode
OFF_SEARCH_MODE: SearchMode
ON_SEARCH_MODE: SearchMode
AUTO_SEARCH_MODE: SearchMode

class GetCompletionsRequest(_message.Message):
    __slots__ = ("messages", "model", "user", "n", "max_tokens", "seed", "stop", "temperature", "top_p", "logprobs", "top_logprobs", "tools", "tool_choice", "response_format", "frequency_penalty", "presence_penalty", "reasoning_effort", "search_parameters", "parallel_tool_calls", "previous_response_id", "store_messages", "use_encrypted_content", "max_turns", "include")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    TOP_P_FIELD_NUMBER: _ClassVar[int]
    LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    TOP_LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    TOOL_CHOICE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_PENALTY_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_PENALTY_FIELD_NUMBER: _ClassVar[int]
    REASONING_EFFORT_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    STORE_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    USE_ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    MAX_TURNS_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    model: str
    user: str
    n: int
    max_tokens: int
    seed: int
    stop: _containers.RepeatedScalarFieldContainer[str]
    temperature: float
    top_p: float
    logprobs: bool
    top_logprobs: int
    tools: _containers.RepeatedCompositeFieldContainer[Tool]
    tool_choice: ToolChoice
    response_format: ResponseFormat
    frequency_penalty: float
    presence_penalty: float
    reasoning_effort: ReasoningEffort
    search_parameters: SearchParameters
    parallel_tool_calls: bool
    previous_response_id: str
    store_messages: bool
    use_encrypted_content: bool
    max_turns: int
    include: _containers.RepeatedScalarFieldContainer[IncludeOption]
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., model: _Optional[str] = ..., user: _Optional[str] = ..., n: _Optional[int] = ..., max_tokens: _Optional[int] = ..., seed: _Optional[int] = ..., stop: _Optional[_Iterable[str]] = ..., temperature: _Optional[float] = ..., top_p: _Optional[float] = ..., logprobs: bool = ..., top_logprobs: _Optional[int] = ..., tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ..., tool_choice: _Optional[_Union[ToolChoice, _Mapping]] = ..., response_format: _Optional[_Union[ResponseFormat, _Mapping]] = ..., frequency_penalty: _Optional[float] = ..., presence_penalty: _Optional[float] = ..., reasoning_effort: _Optional[_Union[ReasoningEffort, str]] = ..., search_parameters: _Optional[_Union[SearchParameters, _Mapping]] = ..., parallel_tool_calls: bool = ..., previous_response_id: _Optional[str] = ..., store_messages: bool = ..., use_encrypted_content: bool = ..., max_turns: _Optional[int] = ..., include: _Optional[_Iterable[_Union[IncludeOption, str]]] = ...) -> None: ...

class GetChatCompletionResponse(_message.Message):
    __slots__ = ("id", "outputs", "created", "model", "system_fingerprint", "usage", "citations", "settings", "debug_output")
    ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    id: str
    outputs: _containers.RepeatedCompositeFieldContainer[CompletionOutput]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    settings: RequestSettings
    debug_output: DebugOutput
    def __init__(self, id: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[CompletionOutput, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ..., settings: _Optional[_Union[RequestSettings, _Mapping]] = ..., debug_output: _Optional[_Union[DebugOutput, _Mapping]] = ...) -> None: ...

class GetChatCompletionChunk(_message.Message):
    __slots__ = ("id", "outputs", "created", "model", "system_fingerprint", "usage", "citations", "debug_output")
    ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    id: str
    outputs: _containers.RepeatedCompositeFieldContainer[CompletionOutputChunk]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    debug_output: DebugOutput
    def __init__(self, id: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[CompletionOutputChunk, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ..., debug_output: _Optional[_Union[DebugOutput, _Mapping]] = ...) -> None: ...

class GetDeferredCompletionResponse(_message.Message):
    __slots__ = ("status", "response")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status: _deferred_pb2.DeferredStatus
    response: GetChatCompletionResponse
    def __init__(self, status: _Optional[_Union[_deferred_pb2.DeferredStatus, str]] = ..., response: _Optional[_Union[GetChatCompletionResponse, _Mapping]] = ...) -> None: ...

class CompletionOutput(_message.Message):
    __slots__ = ("finish_reason", "index", "message", "logprobs")
    FINISH_REASON_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    finish_reason: _sample_pb2.FinishReason
    index: int
    message: CompletionMessage
    logprobs: LogProbs
    def __init__(self, finish_reason: _Optional[_Union[_sample_pb2.FinishReason, str]] = ..., index: _Optional[int] = ..., message: _Optional[_Union[CompletionMessage, _Mapping]] = ..., logprobs: _Optional[_Union[LogProbs, _Mapping]] = ...) -> None: ...

class CompletionMessage(_message.Message):
    __slots__ = ("content", "reasoning_content", "role", "tool_calls", "encrypted_content", "citations")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    encrypted_content: str
    citations: _containers.RepeatedCompositeFieldContainer[InlineCitation]
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., citations: _Optional[_Iterable[_Union[InlineCitation, _Mapping]]] = ...) -> None: ...

class CompletionOutputChunk(_message.Message):
    __slots__ = ("delta", "logprobs", "finish_reason", "index")
    DELTA_FIELD_NUMBER: _ClassVar[int]
    LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    FINISH_REASON_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    delta: Delta
    logprobs: LogProbs
    finish_reason: _sample_pb2.FinishReason
    index: int
    def __init__(self, delta: _Optional[_Union[Delta, _Mapping]] = ..., logprobs: _Optional[_Union[LogProbs, _Mapping]] = ..., finish_reason: _Optional[_Union[_sample_pb2.FinishReason, str]] = ..., index: _Optional[int] = ...) -> None: ...

class Delta(_message.Message):
    __slots__ = ("content", "reasoning_content", "role", "tool_calls", "encrypted_content", "citations")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    encrypted_content: str
    citations: _containers.RepeatedCompositeFieldContainer[InlineCitation]
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., citations: _Optional[_Iterable[_Union[InlineCitation, _Mapping]]] = ...) -> None: ...

class InlineCitation(_message.Message):
    __slots__ = ("id", "start_index", "end_index", "web_citation", "x_citation", "collections_citation")
    ID_FIELD_NUMBER: _ClassVar[int]
    START_INDEX_FIELD_NUMBER: _ClassVar[int]
    END_INDEX_FIELD_NUMBER: _ClassVar[int]
    WEB_CITATION_FIELD_NUMBER: _ClassVar[int]
    X_CITATION_FIELD_NUMBER: _ClassVar[int]
    COLLECTIONS_CITATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    start_index: int
    end_index: int
    web_citation: WebCitation
    x_citation: XCitation
    collections_citation: CollectionsCitation
    def __init__(self, id: _Optional[str] = ..., start_index: _Optional[int] = ..., end_index: _Optional[int] = ..., web_citation: _Optional[_Union[WebCitation, _Mapping]] = ..., x_citation: _Optional[_Union[XCitation, _Mapping]] = ..., collections_citation: _Optional[_Union[CollectionsCitation, _Mapping]] = ...) -> None: ...

class WebCitation(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class XCitation(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class CollectionsCitation(_message.Message):
    __slots__ = ("file_id", "chunk_id", "chunk_content", "score", "collection_ids")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_CONTENT_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_IDS_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    chunk_id: str
    chunk_content: str
    score: float
    collection_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, file_id: _Optional[str] = ..., chunk_id: _Optional[str] = ..., chunk_content: _Optional[str] = ..., score: _Optional[float] = ..., collection_ids: _Optional[_Iterable[str]] = ...) -> None: ...

class LogProbs(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: _containers.RepeatedCompositeFieldContainer[LogProb]
    def __init__(self, content: _Optional[_Iterable[_Union[LogProb, _Mapping]]] = ...) -> None: ...

class LogProb(_message.Message):
    __slots__ = ("token", "logprob", "bytes", "top_logprobs")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    LOGPROB_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    TOP_LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    token: str
    logprob: float
    bytes: bytes
    top_logprobs: _containers.RepeatedCompositeFieldContainer[TopLogProb]
    def __init__(self, token: _Optional[str] = ..., logprob: _Optional[float] = ..., bytes: _Optional[bytes] = ..., top_logprobs: _Optional[_Iterable[_Union[TopLogProb, _Mapping]]] = ...) -> None: ...

class TopLogProb(_message.Message):
    __slots__ = ("token", "logprob", "bytes")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    LOGPROB_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    token: str
    logprob: float
    bytes: bytes
    def __init__(self, token: _Optional[str] = ..., logprob: _Optional[float] = ..., bytes: _Optional[bytes] = ...) -> None: ...

class Content(_message.Message):
    __slots__ = ("text", "image_url", "file")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    text: str
    image_url: _image_pb2.ImageUrlContent
    file: FileContent
    def __init__(self, text: _Optional[str] = ..., image_url: _Optional[_Union[_image_pb2.ImageUrlContent, _Mapping]] = ..., file: _Optional[_Union[FileContent, _Mapping]] = ...) -> None: ...

class FileContent(_message.Message):
    __slots__ = ("file_id",)
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    def __init__(self, file_id: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("content", "reasoning_content", "role", "name", "tool_calls", "encrypted_content", "tool_call_id")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    content: _containers.RepeatedCompositeFieldContainer[Content]
    reasoning_content: str
    role: MessageRole
    name: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    encrypted_content: str
    tool_call_id: str
    def __init__(self, content: _Optional[_Iterable[_Union[Content, _Mapping]]] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., name: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., tool_call_id: _Optional[str] = ...) -> None: ...

class ToolChoice(_message.Message):
    __slots__ = ("mode", "function_name")
    MODE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    mode: ToolMode
    function_name: str
    def __init__(self, mode: _Optional[_Union[ToolMode, str]] = ..., function_name: _Optional[str] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("function", "web_search", "x_search", "code_execution", "collections_search", "mcp", "attachment_search")
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    WEB_SEARCH_FIELD_NUMBER: _ClassVar[int]
    X_SEARCH_FIELD_NUMBER: _ClassVar[int]
    CODE_EXECUTION_FIELD_NUMBER: _ClassVar[int]
    COLLECTIONS_SEARCH_FIELD_NUMBER: _ClassVar[int]
    MCP_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENT_SEARCH_FIELD_NUMBER: _ClassVar[int]
    function: Function
    web_search: WebSearch
    x_search: XSearch
    code_execution: CodeExecution
    collections_search: CollectionsSearch
    mcp: MCP
    attachment_search: AttachmentSearch
    def __init__(self, function: _Optional[_Union[Function, _Mapping]] = ..., web_search: _Optional[_Union[WebSearch, _Mapping]] = ..., x_search: _Optional[_Union[XSearch, _Mapping]] = ..., code_execution: _Optional[_Union[CodeExecution, _Mapping]] = ..., collections_search: _Optional[_Union[CollectionsSearch, _Mapping]] = ..., mcp: _Optional[_Union[MCP, _Mapping]] = ..., attachment_search: _Optional[_Union[AttachmentSearch, _Mapping]] = ...) -> None: ...

class MCP(_message.Message):
    __slots__ = ("server_label", "server_description", "server_url", "allowed_tool_names", "authorization", "extra_headers")
    class ExtraHeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVER_LABEL_FIELD_NUMBER: _ClassVar[int]
    SERVER_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SERVER_URL_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_TOOL_NAMES_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_FIELD_NUMBER: _ClassVar[int]
    EXTRA_HEADERS_FIELD_NUMBER: _ClassVar[int]
    server_label: str
    server_description: str
    server_url: str
    allowed_tool_names: _containers.RepeatedScalarFieldContainer[str]
    authorization: str
    extra_headers: _containers.ScalarMap[str, str]
    def __init__(self, server_label: _Optional[str] = ..., server_description: _Optional[str] = ..., server_url: _Optional[str] = ..., allowed_tool_names: _Optional[_Iterable[str]] = ..., authorization: _Optional[str] = ..., extra_headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class WebSearch(_message.Message):
    __slots__ = ("excluded_domains", "allowed_domains", "enable_image_understanding", "user_location")
    EXCLUDED_DOMAINS_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_DOMAINS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_IMAGE_UNDERSTANDING_FIELD_NUMBER: _ClassVar[int]
    USER_LOCATION_FIELD_NUMBER: _ClassVar[int]
    excluded_domains: _containers.RepeatedScalarFieldContainer[str]
    allowed_domains: _containers.RepeatedScalarFieldContainer[str]
    enable_image_understanding: bool
    user_location: WebSearchUserLocation
    def __init__(self, excluded_domains: _Optional[_Iterable[str]] = ..., allowed_domains: _Optional[_Iterable[str]] = ..., enable_image_understanding: bool = ..., user_location: _Optional[_Union[WebSearchUserLocation, _Mapping]] = ...) -> None: ...

class WebSearchUserLocation(_message.Message):
    __slots__ = ("country", "city", "region", "timezone")
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    country: str
    city: str
    region: str
    timezone: str
    def __init__(self, country: _Optional[str] = ..., city: _Optional[str] = ..., region: _Optional[str] = ..., timezone: _Optional[str] = ...) -> None: ...

class XSearch(_message.Message):
    __slots__ = ("from_date", "to_date", "allowed_x_handles", "excluded_x_handles", "enable_image_understanding", "enable_video_understanding")
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_X_HANDLES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_X_HANDLES_FIELD_NUMBER: _ClassVar[int]
    ENABLE_IMAGE_UNDERSTANDING_FIELD_NUMBER: _ClassVar[int]
    ENABLE_VIDEO_UNDERSTANDING_FIELD_NUMBER: _ClassVar[int]
    from_date: _timestamp_pb2.Timestamp
    to_date: _timestamp_pb2.Timestamp
    allowed_x_handles: _containers.RepeatedScalarFieldContainer[str]
    excluded_x_handles: _containers.RepeatedScalarFieldContainer[str]
    enable_image_understanding: bool
    enable_video_understanding: bool
    def __init__(self, from_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., allowed_x_handles: _Optional[_Iterable[str]] = ..., excluded_x_handles: _Optional[_Iterable[str]] = ..., enable_image_understanding: bool = ..., enable_video_understanding: bool = ...) -> None: ...

class CodeExecution(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CollectionsSearch(_message.Message):
    __slots__ = ("collection_ids", "limit", "instructions", "hybrid_retrieval", "semantic_retrieval", "keyword_retrieval")
    COLLECTION_IDS_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    HYBRID_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    SEMANTIC_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    KEYWORD_RETRIEVAL_FIELD_NUMBER: _ClassVar[int]
    collection_ids: _containers.RepeatedScalarFieldContainer[str]
    limit: int
    instructions: str
    hybrid_retrieval: _documents_pb2.HybridRetrieval
    semantic_retrieval: _documents_pb2.SemanticRetrieval
    keyword_retrieval: _documents_pb2.KeywordRetrieval
    def __init__(self, collection_ids: _Optional[_Iterable[str]] = ..., limit: _Optional[int] = ..., instructions: _Optional[str] = ..., hybrid_retrieval: _Optional[_Union[_documents_pb2.HybridRetrieval, _Mapping]] = ..., semantic_retrieval: _Optional[_Union[_documents_pb2.SemanticRetrieval, _Mapping]] = ..., keyword_retrieval: _Optional[_Union[_documents_pb2.KeywordRetrieval, _Mapping]] = ...) -> None: ...

class AttachmentSearch(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class Function(_message.Message):
    __slots__ = ("name", "description", "strict", "parameters")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STRICT_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    strict: bool
    parameters: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., strict: bool = ..., parameters: _Optional[str] = ...) -> None: ...

class ToolCall(_message.Message):
    __slots__ = ("id", "type", "status", "error_message", "function")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: ToolCallType
    status: ToolCallStatus
    error_message: str
    function: FunctionCall
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[ToolCallType, str]] = ..., status: _Optional[_Union[ToolCallStatus, str]] = ..., error_message: _Optional[str] = ..., function: _Optional[_Union[FunctionCall, _Mapping]] = ...) -> None: ...

class FunctionCall(_message.Message):
    __slots__ = ("name", "arguments")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARGUMENTS_FIELD_NUMBER: _ClassVar[int]
    name: str
    arguments: str
    def __init__(self, name: _Optional[str] = ..., arguments: _Optional[str] = ...) -> None: ...

class ResponseFormat(_message.Message):
    __slots__ = ("format_type", "schema")
    FORMAT_TYPE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    format_type: FormatType
    schema: str
    def __init__(self, format_type: _Optional[_Union[FormatType, str]] = ..., schema: _Optional[str] = ...) -> None: ...

class SearchParameters(_message.Message):
    __slots__ = ("mode", "sources", "from_date", "to_date", "return_citations", "max_search_results")
    MODE_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    RETURN_CITATIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_SEARCH_RESULTS_FIELD_NUMBER: _ClassVar[int]
    mode: SearchMode
    sources: _containers.RepeatedCompositeFieldContainer[Source]
    from_date: _timestamp_pb2.Timestamp
    to_date: _timestamp_pb2.Timestamp
    return_citations: bool
    max_search_results: int
    def __init__(self, mode: _Optional[_Union[SearchMode, str]] = ..., sources: _Optional[_Iterable[_Union[Source, _Mapping]]] = ..., from_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., return_citations: bool = ..., max_search_results: _Optional[int] = ...) -> None: ...

class Source(_message.Message):
    __slots__ = ("web", "news", "x", "rss")
    WEB_FIELD_NUMBER: _ClassVar[int]
    NEWS_FIELD_NUMBER: _ClassVar[int]
    X_FIELD_NUMBER: _ClassVar[int]
    RSS_FIELD_NUMBER: _ClassVar[int]
    web: WebSource
    news: NewsSource
    x: XSource
    rss: RssSource
    def __init__(self, web: _Optional[_Union[WebSource, _Mapping]] = ..., news: _Optional[_Union[NewsSource, _Mapping]] = ..., x: _Optional[_Union[XSource, _Mapping]] = ..., rss: _Optional[_Union[RssSource, _Mapping]] = ...) -> None: ...

class WebSource(_message.Message):
    __slots__ = ("excluded_websites", "allowed_websites", "country", "safe_search")
    EXCLUDED_WEBSITES_FIELD_NUMBER: _ClassVar[int]
    ALLOWED_WEBSITES_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    SAFE_SEARCH_FIELD_NUMBER: _ClassVar[int]
    excluded_websites: _containers.RepeatedScalarFieldContainer[str]
    allowed_websites: _containers.RepeatedScalarFieldContainer[str]
    country: str
    safe_search: bool
    def __init__(self, excluded_websites: _Optional[_Iterable[str]] = ..., allowed_websites: _Optional[_Iterable[str]] = ..., country: _Optional[str] = ..., safe_search: bool = ...) -> None: ...

class NewsSource(_message.Message):
    __slots__ = ("excluded_websites", "country", "safe_search")
    EXCLUDED_WEBSITES_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    SAFE_SEARCH_FIELD_NUMBER: _ClassVar[int]
    excluded_websites: _containers.RepeatedScalarFieldContainer[str]
    country: str
    safe_search: bool
    def __init__(self, excluded_websites: _Optional[_Iterable[str]] = ..., country: _Optional[str] = ..., safe_search: bool = ...) -> None: ...

class XSource(_message.Message):
    __slots__ = ("included_x_handles", "excluded_x_handles", "post_favorite_count", "post_view_count")
    INCLUDED_X_HANDLES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDED_X_HANDLES_FIELD_NUMBER: _ClassVar[int]
    POST_FAVORITE_COUNT_FIELD_NUMBER: _ClassVar[int]
    POST_VIEW_COUNT_FIELD_NUMBER: _ClassVar[int]
    included_x_handles: _containers.RepeatedScalarFieldContainer[str]
    excluded_x_handles: _containers.RepeatedScalarFieldContainer[str]
    post_favorite_count: int
    post_view_count: int
    def __init__(self, included_x_handles: _Optional[_Iterable[str]] = ..., excluded_x_handles: _Optional[_Iterable[str]] = ..., post_favorite_count: _Optional[int] = ..., post_view_count: _Optional[int] = ...) -> None: ...

class RssSource(_message.Message):
    __slots__ = ("links",)
    LINKS_FIELD_NUMBER: _ClassVar[int]
    links: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, links: _Optional[_Iterable[str]] = ...) -> None: ...

class RequestSettings(_message.Message):
    __slots__ = ("max_tokens", "parallel_tool_calls", "previous_response_id", "reasoning_effort", "temperature", "response_format", "tool_choice", "tools", "top_p", "user", "search_parameters", "store_messages", "use_encrypted_content", "include")
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    PARALLEL_TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    REASONING_EFFORT_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CHOICE_FIELD_NUMBER: _ClassVar[int]
    TOOLS_FIELD_NUMBER: _ClassVar[int]
    TOP_P_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STORE_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    USE_ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_FIELD_NUMBER: _ClassVar[int]
    max_tokens: int
    parallel_tool_calls: bool
    previous_response_id: str
    reasoning_effort: ReasoningEffort
    temperature: float
    response_format: ResponseFormat
    tool_choice: ToolChoice
    tools: _containers.RepeatedCompositeFieldContainer[Tool]
    top_p: float
    user: str
    search_parameters: SearchParameters
    store_messages: bool
    use_encrypted_content: bool
    include: _containers.RepeatedScalarFieldContainer[IncludeOption]
    def __init__(self, max_tokens: _Optional[int] = ..., parallel_tool_calls: bool = ..., previous_response_id: _Optional[str] = ..., reasoning_effort: _Optional[_Union[ReasoningEffort, str]] = ..., temperature: _Optional[float] = ..., response_format: _Optional[_Union[ResponseFormat, _Mapping]] = ..., tool_choice: _Optional[_Union[ToolChoice, _Mapping]] = ..., tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ..., top_p: _Optional[float] = ..., user: _Optional[str] = ..., search_parameters: _Optional[_Union[SearchParameters, _Mapping]] = ..., store_messages: bool = ..., use_encrypted_content: bool = ..., include: _Optional[_Iterable[_Union[IncludeOption, str]]] = ...) -> None: ...

class GetStoredCompletionRequest(_message.Message):
    __slots__ = ("response_id",)
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    response_id: str
    def __init__(self, response_id: _Optional[str] = ...) -> None: ...

class DeleteStoredCompletionRequest(_message.Message):
    __slots__ = ("response_id",)
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    response_id: str
    def __init__(self, response_id: _Optional[str] = ...) -> None: ...

class DeleteStoredCompletionResponse(_message.Message):
    __slots__ = ("response_id",)
    RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    response_id: str
    def __init__(self, response_id: _Optional[str] = ...) -> None: ...

class DebugOutput(_message.Message):
    __slots__ = ("attempts", "request", "prompt", "engine_request", "responses", "chunks", "cache_read_count", "cache_read_input_bytes", "cache_write_count", "cache_write_input_bytes", "lb_address", "sampler_tag")
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    ENGINE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSES_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    CACHE_READ_COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHE_READ_INPUT_BYTES_FIELD_NUMBER: _ClassVar[int]
    CACHE_WRITE_COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHE_WRITE_INPUT_BYTES_FIELD_NUMBER: _ClassVar[int]
    LB_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    SAMPLER_TAG_FIELD_NUMBER: _ClassVar[int]
    attempts: int
    request: str
    prompt: str
    engine_request: str
    responses: _containers.RepeatedScalarFieldContainer[str]
    chunks: _containers.RepeatedScalarFieldContainer[str]
    cache_read_count: int
    cache_read_input_bytes: int
    cache_write_count: int
    cache_write_input_bytes: int
    lb_address: str
    sampler_tag: str
    def __init__(self, attempts: _Optional[int] = ..., request: _Optional[str] = ..., prompt: _Optional[str] = ..., engine_request: _Optional[str] = ..., responses: _Optional[_Iterable[str]] = ..., chunks: _Optional[_Iterable[str]] = ..., cache_read_count: _Optional[int] = ..., cache_read_input_bytes: _Optional[int] = ..., cache_write_count: _Optional[int] = ..., cache_write_input_bytes: _Optional[int] = ..., lb_address: _Optional[str] = ..., sampler_tag: _Optional[str] = ...) -> None: ...
