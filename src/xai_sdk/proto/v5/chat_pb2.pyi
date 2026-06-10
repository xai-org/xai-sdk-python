from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import deferred_pb2 as _deferred_pb2
from . import sample_pb2 as _sample_pb2
from . import usage_pb2 as _usage_pb2
from . import chat_types_pb2 as _chat_types_pb2
from . import chat_bidi_v2_pb2 as _chat_bidi_v2_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
from chat_types_pb2 import Content as Content
from chat_types_pb2 import FileContent as FileContent
from chat_types_pb2 import ToolChoice as ToolChoice
from chat_types_pb2 import Tool as Tool
from chat_types_pb2 import MCP as MCP
from chat_types_pb2 import WebSearch as WebSearch
from chat_types_pb2 import WebSearchUserLocation as WebSearchUserLocation
from chat_types_pb2 import XSearch as XSearch
from chat_types_pb2 import CodeExecution as CodeExecution
from chat_types_pb2 import CollectionsSearch as CollectionsSearch
from chat_types_pb2 import AttachmentSearch as AttachmentSearch
from chat_types_pb2 import LocationsSearch as LocationsSearch
from chat_types_pb2 import Function as Function
from chat_types_pb2 import LiveSearch as LiveSearch
from chat_types_pb2 import ToolCall as ToolCall
from chat_types_pb2 import FunctionCall as FunctionCall
from chat_types_pb2 import ResponseFormat as ResponseFormat
from chat_types_pb2 import InlineCitation as InlineCitation
from chat_types_pb2 import WebCitation as WebCitation
from chat_types_pb2 import XCitation as XCitation
from chat_types_pb2 import CollectionsCitation as CollectionsCitation
from chat_types_pb2 import OutputFile as OutputFile
from chat_types_pb2 import Source as Source
from chat_types_pb2 import WebSource as WebSource
from chat_types_pb2 import NewsSource as NewsSource
from chat_types_pb2 import XSource as XSource
from chat_types_pb2 import RssSource as RssSource
from chat_types_pb2 import MessageRole as MessageRole
from chat_types_pb2 import ReasoningEffort as ReasoningEffort
from chat_types_pb2 import AgentCount as AgentCount
from chat_types_pb2 import IncludeOption as IncludeOption
from chat_types_pb2 import ToolMode as ToolMode
from chat_types_pb2 import FormatType as FormatType
from chat_types_pb2 import ToolCallType as ToolCallType
from chat_types_pb2 import ToolCallStatus as ToolCallStatus
from chat_bidi_v2_pb2 import ServerEvent as ServerEvent
from chat_bidi_v2_pb2 import ResponseCreatedEvent as ResponseCreatedEvent
from chat_bidi_v2_pb2 import ResponseCompletedEvent as ResponseCompletedEvent
from chat_bidi_v2_pb2 import ResponseFailedEvent as ResponseFailedEvent
from chat_bidi_v2_pb2 import ResponseIncompleteEvent as ResponseIncompleteEvent
from chat_bidi_v2_pb2 import AgentInfo as AgentInfo
from chat_bidi_v2_pb2 import OutputItem as OutputItem
from chat_bidi_v2_pb2 import OutputMessageContent as OutputMessageContent
from chat_bidi_v2_pb2 import OutputTextAnnotation as OutputTextAnnotation
from chat_bidi_v2_pb2 import ToolCallInfo as ToolCallInfo
from chat_bidi_v2_pb2 import ContentPart as ContentPart
from chat_bidi_v2_pb2 import OutputItemAddedEvent as OutputItemAddedEvent
from chat_bidi_v2_pb2 import OutputItemDoneEvent as OutputItemDoneEvent
from chat_bidi_v2_pb2 import OutputTextDeltaEvent as OutputTextDeltaEvent
from chat_bidi_v2_pb2 import OutputTextDoneEvent as OutputTextDoneEvent
from chat_bidi_v2_pb2 import OutputTextAnnotationAddedEvent as OutputTextAnnotationAddedEvent
from chat_bidi_v2_pb2 import ReasoningTextDeltaEvent as ReasoningTextDeltaEvent
from chat_bidi_v2_pb2 import ReasoningTextDoneEvent as ReasoningTextDoneEvent
from chat_bidi_v2_pb2 import ToolCallArgumentsDeltaEvent as ToolCallArgumentsDeltaEvent
from chat_bidi_v2_pb2 import ToolCallArgumentsDoneEvent as ToolCallArgumentsDoneEvent
from chat_bidi_v2_pb2 import ToolCallInProgressEvent as ToolCallInProgressEvent
from chat_bidi_v2_pb2 import ToolCallCompletedEvent as ToolCallCompletedEvent
from chat_bidi_v2_pb2 import ToolCallFailedEvent as ToolCallFailedEvent
from chat_bidi_v2_pb2 import ErrorEvent as ErrorEvent
from chat_bidi_v2_pb2 import StreamError as StreamError
from chat_bidi_v2_pb2 import ClientEvent as ClientEvent
from chat_bidi_v2_pb2 import ToolResultEvent as ToolResultEvent
from chat_bidi_v2_pb2 import CancelResponseEvent as CancelResponseEvent
from chat_bidi_v2_pb2 import ConversationRequest as ConversationRequest
from chat_bidi_v2_pb2 import InputItem as InputItem
from chat_bidi_v2_pb2 import InputMessage as InputMessage
from chat_bidi_v2_pb2 import FunctionCallOutput as FunctionCallOutput
from chat_bidi_v2_pb2 import AgentRole as AgentRole

DESCRIPTOR: _descriptor.FileDescriptor
INVALID_ROLE: _chat_types_pb2.MessageRole
ROLE_USER: _chat_types_pb2.MessageRole
ROLE_ASSISTANT: _chat_types_pb2.MessageRole
ROLE_SYSTEM: _chat_types_pb2.MessageRole
ROLE_FUNCTION: _chat_types_pb2.MessageRole
ROLE_TOOL: _chat_types_pb2.MessageRole
ROLE_DEVELOPER: _chat_types_pb2.MessageRole
INVALID_EFFORT: _chat_types_pb2.ReasoningEffort
EFFORT_LOW: _chat_types_pb2.ReasoningEffort
EFFORT_MEDIUM: _chat_types_pb2.ReasoningEffort
EFFORT_HIGH: _chat_types_pb2.ReasoningEffort
EFFORT_NONE: _chat_types_pb2.ReasoningEffort
AGENT_COUNT_UNSPECIFIED: _chat_types_pb2.AgentCount
AGENT_COUNT_4: _chat_types_pb2.AgentCount
AGENT_COUNT_16: _chat_types_pb2.AgentCount
INCLUDE_OPTION_INVALID: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_WEB_SEARCH_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_X_SEARCH_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_CODE_EXECUTION_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_COLLECTIONS_SEARCH_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_ATTACHMENT_SEARCH_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_MCP_CALL_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_INLINE_CITATIONS: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_VERBOSE_STREAMING: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_CODE_EXECUTION_FILES_OUTPUT: _chat_types_pb2.IncludeOption
INCLUDE_OPTION_TOOL_CALL_STREAMING: _chat_types_pb2.IncludeOption
TOOL_MODE_INVALID: _chat_types_pb2.ToolMode
TOOL_MODE_AUTO: _chat_types_pb2.ToolMode
TOOL_MODE_NONE: _chat_types_pb2.ToolMode
TOOL_MODE_REQUIRED: _chat_types_pb2.ToolMode
FORMAT_TYPE_INVALID: _chat_types_pb2.FormatType
FORMAT_TYPE_TEXT: _chat_types_pb2.FormatType
FORMAT_TYPE_JSON_OBJECT: _chat_types_pb2.FormatType
FORMAT_TYPE_JSON_SCHEMA: _chat_types_pb2.FormatType
TOOL_CALL_TYPE_INVALID: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_CLIENT_SIDE_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_WEB_SEARCH_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_X_SEARCH_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_CODE_EXECUTION_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_COLLECTIONS_SEARCH_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_MCP_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_ATTACHMENT_SEARCH_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_CONNECTOR_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_TYPE_LOCATIONS_SEARCH_TOOL: _chat_types_pb2.ToolCallType
TOOL_CALL_STATUS_IN_PROGRESS: _chat_types_pb2.ToolCallStatus
TOOL_CALL_STATUS_COMPLETED: _chat_types_pb2.ToolCallStatus
TOOL_CALL_STATUS_INCOMPLETE: _chat_types_pb2.ToolCallStatus
TOOL_CALL_STATUS_FAILED: _chat_types_pb2.ToolCallStatus
AGENT_ROLE_UNSPECIFIED: _chat_bidi_v2_pb2.AgentRole
AGENT_ROLE_LEADER: _chat_bidi_v2_pb2.AgentRole
AGENT_ROLE_MEMBER: _chat_bidi_v2_pb2.AgentRole

class SearchMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_SEARCH_MODE: _ClassVar[SearchMode]
    OFF_SEARCH_MODE: _ClassVar[SearchMode]
    ON_SEARCH_MODE: _ClassVar[SearchMode]
    AUTO_SEARCH_MODE: _ClassVar[SearchMode]
INVALID_SEARCH_MODE: SearchMode
OFF_SEARCH_MODE: SearchMode
ON_SEARCH_MODE: SearchMode
AUTO_SEARCH_MODE: SearchMode

class GetCompletionsRequest(_message.Message):
    __slots__ = ("messages", "model", "user", "n", "max_tokens", "seed", "stop", "temperature", "top_p", "logprobs", "top_logprobs", "tools", "tool_choice", "response_format", "frequency_penalty", "presence_penalty", "reasoning_effort", "search_parameters", "parallel_tool_calls", "previous_response_id", "store_messages", "use_encrypted_content", "max_turns", "include", "bootstrap_host", "bootstrap_room", "agent_count", "cache_salt", "service_tier")
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
    BOOTSTRAP_HOST_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAP_ROOM_FIELD_NUMBER: _ClassVar[int]
    AGENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    CACHE_SALT_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
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
    tools: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.Tool]
    tool_choice: _chat_types_pb2.ToolChoice
    response_format: _chat_types_pb2.ResponseFormat
    frequency_penalty: float
    presence_penalty: float
    reasoning_effort: _chat_types_pb2.ReasoningEffort
    search_parameters: SearchParameters
    parallel_tool_calls: bool
    previous_response_id: str
    store_messages: bool
    use_encrypted_content: bool
    max_turns: int
    include: _containers.RepeatedScalarFieldContainer[_chat_types_pb2.IncludeOption]
    bootstrap_host: str
    bootstrap_room: int
    agent_count: _chat_types_pb2.AgentCount
    cache_salt: str
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., model: _Optional[str] = ..., user: _Optional[str] = ..., n: _Optional[int] = ..., max_tokens: _Optional[int] = ..., seed: _Optional[int] = ..., stop: _Optional[_Iterable[str]] = ..., temperature: _Optional[float] = ..., top_p: _Optional[float] = ..., logprobs: bool = ..., top_logprobs: _Optional[int] = ..., tools: _Optional[_Iterable[_Union[_chat_types_pb2.Tool, _Mapping]]] = ..., tool_choice: _Optional[_Union[_chat_types_pb2.ToolChoice, _Mapping]] = ..., response_format: _Optional[_Union[_chat_types_pb2.ResponseFormat, _Mapping]] = ..., frequency_penalty: _Optional[float] = ..., presence_penalty: _Optional[float] = ..., reasoning_effort: _Optional[_Union[_chat_types_pb2.ReasoningEffort, str]] = ..., search_parameters: _Optional[_Union[SearchParameters, _Mapping]] = ..., parallel_tool_calls: bool = ..., previous_response_id: _Optional[str] = ..., store_messages: bool = ..., use_encrypted_content: bool = ..., max_turns: _Optional[int] = ..., include: _Optional[_Iterable[_Union[_chat_types_pb2.IncludeOption, str]]] = ..., bootstrap_host: _Optional[str] = ..., bootstrap_room: _Optional[int] = ..., agent_count: _Optional[_Union[_chat_types_pb2.AgentCount, str]] = ..., cache_salt: _Optional[str] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...

class GetChatCompletionResponse(_message.Message):
    __slots__ = ("id", "outputs", "created", "model", "system_fingerprint", "usage", "citations", "settings", "debug_output", "output_files", "input_messages", "service_tier")
    ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    INPUT_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    id: str
    outputs: _containers.RepeatedCompositeFieldContainer[CompletionOutput]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    settings: RequestSettings
    debug_output: DebugOutput
    output_files: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.OutputFile]
    input_messages: _containers.RepeatedCompositeFieldContainer[Message]
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, id: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[CompletionOutput, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ..., settings: _Optional[_Union[RequestSettings, _Mapping]] = ..., debug_output: _Optional[_Union[DebugOutput, _Mapping]] = ..., output_files: _Optional[_Iterable[_Union[_chat_types_pb2.OutputFile, _Mapping]]] = ..., input_messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...

class GetChatCompletionChunk(_message.Message):
    __slots__ = ("id", "outputs", "created", "model", "system_fingerprint", "usage", "citations", "debug_output", "output_files", "service_tier")
    ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    DEBUG_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    SERVICE_TIER_FIELD_NUMBER: _ClassVar[int]
    id: str
    outputs: _containers.RepeatedCompositeFieldContainer[CompletionOutputChunk]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    debug_output: DebugOutput
    output_files: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.OutputFile]
    service_tier: _usage_pb2.ServiceTier
    def __init__(self, id: _Optional[str] = ..., outputs: _Optional[_Iterable[_Union[CompletionOutputChunk, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ..., debug_output: _Optional[_Union[DebugOutput, _Mapping]] = ..., output_files: _Optional[_Iterable[_Union[_chat_types_pb2.OutputFile, _Mapping]]] = ..., service_tier: _Optional[_Union[_usage_pb2.ServiceTier, str]] = ...) -> None: ...

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
    __slots__ = ("content", "reasoning_content", "role", "tool_calls", "encrypted_content", "citations", "is_reasoning_content_summarized")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_REASONING_CONTENT_SUMMARIZED_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: _chat_types_pb2.MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.ToolCall]
    encrypted_content: str
    citations: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.InlineCitation]
    is_reasoning_content_summarized: bool
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[_chat_types_pb2.MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[_chat_types_pb2.ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., citations: _Optional[_Iterable[_Union[_chat_types_pb2.InlineCitation, _Mapping]]] = ..., is_reasoning_content_summarized: bool = ...) -> None: ...

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
    __slots__ = ("content", "reasoning_content", "role", "tool_calls", "encrypted_content", "citations", "is_reasoning_content_summarized")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_REASONING_CONTENT_SUMMARIZED_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: _chat_types_pb2.MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.ToolCall]
    encrypted_content: str
    citations: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.InlineCitation]
    is_reasoning_content_summarized: bool
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[_chat_types_pb2.MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[_chat_types_pb2.ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., citations: _Optional[_Iterable[_Union[_chat_types_pb2.InlineCitation, _Mapping]]] = ..., is_reasoning_content_summarized: bool = ...) -> None: ...

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

class Message(_message.Message):
    __slots__ = ("content", "reasoning_content", "role", "name", "tool_calls", "encrypted_content", "tool_call_id")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALL_ID_FIELD_NUMBER: _ClassVar[int]
    content: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.Content]
    reasoning_content: str
    role: _chat_types_pb2.MessageRole
    name: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.ToolCall]
    encrypted_content: str
    tool_call_id: str
    def __init__(self, content: _Optional[_Iterable[_Union[_chat_types_pb2.Content, _Mapping]]] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[_chat_types_pb2.MessageRole, str]] = ..., name: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[_chat_types_pb2.ToolCall, _Mapping]]] = ..., encrypted_content: _Optional[str] = ..., tool_call_id: _Optional[str] = ...) -> None: ...

class SearchParameters(_message.Message):
    __slots__ = ("mode", "sources", "from_date", "to_date", "return_citations", "max_search_results")
    MODE_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    RETURN_CITATIONS_FIELD_NUMBER: _ClassVar[int]
    MAX_SEARCH_RESULTS_FIELD_NUMBER: _ClassVar[int]
    mode: SearchMode
    sources: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.Source]
    from_date: _timestamp_pb2.Timestamp
    to_date: _timestamp_pb2.Timestamp
    return_citations: bool
    max_search_results: int
    def __init__(self, mode: _Optional[_Union[SearchMode, str]] = ..., sources: _Optional[_Iterable[_Union[_chat_types_pb2.Source, _Mapping]]] = ..., from_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., to_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., return_citations: bool = ..., max_search_results: _Optional[int] = ...) -> None: ...

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
    reasoning_effort: _chat_types_pb2.ReasoningEffort
    temperature: float
    response_format: _chat_types_pb2.ResponseFormat
    tool_choice: _chat_types_pb2.ToolChoice
    tools: _containers.RepeatedCompositeFieldContainer[_chat_types_pb2.Tool]
    top_p: float
    user: str
    search_parameters: SearchParameters
    store_messages: bool
    use_encrypted_content: bool
    include: _containers.RepeatedScalarFieldContainer[_chat_types_pb2.IncludeOption]
    def __init__(self, max_tokens: _Optional[int] = ..., parallel_tool_calls: bool = ..., previous_response_id: _Optional[str] = ..., reasoning_effort: _Optional[_Union[_chat_types_pb2.ReasoningEffort, str]] = ..., temperature: _Optional[float] = ..., response_format: _Optional[_Union[_chat_types_pb2.ResponseFormat, _Mapping]] = ..., tool_choice: _Optional[_Union[_chat_types_pb2.ToolChoice, _Mapping]] = ..., tools: _Optional[_Iterable[_Union[_chat_types_pb2.Tool, _Mapping]]] = ..., top_p: _Optional[float] = ..., user: _Optional[str] = ..., search_parameters: _Optional[_Union[SearchParameters, _Mapping]] = ..., store_messages: bool = ..., use_encrypted_content: bool = ..., include: _Optional[_Iterable[_Union[_chat_types_pb2.IncludeOption, str]]] = ...) -> None: ...

class ResponseHistory(_message.Message):
    __slots__ = ("messages", "response", "conversation_id")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    CONVERSATION_ID_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    response: GetChatCompletionResponse
    conversation_id: str
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., response: _Optional[_Union[GetChatCompletionResponse, _Mapping]] = ..., conversation_id: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("attempts", "request", "prompt", "engine_request", "responses", "chunks", "cache_read_count", "cache_read_input_bytes", "cache_write_count", "cache_write_input_bytes", "lb_address", "sampler_tag", "sampler_checkpoint_mount")
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
    SAMPLER_CHECKPOINT_MOUNT_FIELD_NUMBER: _ClassVar[int]
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
    sampler_checkpoint_mount: str
    def __init__(self, attempts: _Optional[int] = ..., request: _Optional[str] = ..., prompt: _Optional[str] = ..., engine_request: _Optional[str] = ..., responses: _Optional[_Iterable[str]] = ..., chunks: _Optional[_Iterable[str]] = ..., cache_read_count: _Optional[int] = ..., cache_read_input_bytes: _Optional[int] = ..., cache_write_count: _Optional[int] = ..., cache_write_input_bytes: _Optional[int] = ..., lb_address: _Optional[str] = ..., sampler_tag: _Optional[str] = ..., sampler_checkpoint_mount: _Optional[str] = ...) -> None: ...

class CompactContextRequest(_message.Message):
    __slots__ = ("model", "input")
    MODEL_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    model: str
    input: _containers.RepeatedCompositeFieldContainer[Message]
    def __init__(self, model: _Optional[str] = ..., input: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...) -> None: ...

class CompactContextResponse(_message.Message):
    __slots__ = ("id", "encrypted_content", "dropped_message_count", "usage")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_CONTENT_FIELD_NUMBER: _ClassVar[int]
    DROPPED_MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    encrypted_content: str
    dropped_message_count: int
    usage: _usage_pb2.SamplingUsage
    def __init__(self, id: _Optional[str] = ..., encrypted_content: _Optional[str] = ..., dropped_message_count: _Optional[int] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ...) -> None: ...
