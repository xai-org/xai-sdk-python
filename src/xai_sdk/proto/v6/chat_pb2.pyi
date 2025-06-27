from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import deferred_pb2 as _deferred_pb2
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

class MessageRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_ROLE: _ClassVar[MessageRole]
    ROLE_USER: _ClassVar[MessageRole]
    ROLE_ASSISTANT: _ClassVar[MessageRole]
    ROLE_SYSTEM: _ClassVar[MessageRole]
    ROLE_FUNCTION: _ClassVar[MessageRole]
    ROLE_TOOL: _ClassVar[MessageRole]

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

class SearchMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_SEARCH_MODE: _ClassVar[SearchMode]
    OFF_SEARCH_MODE: _ClassVar[SearchMode]
    ON_SEARCH_MODE: _ClassVar[SearchMode]
    AUTO_SEARCH_MODE: _ClassVar[SearchMode]
INVALID_ROLE: MessageRole
ROLE_USER: MessageRole
ROLE_ASSISTANT: MessageRole
ROLE_SYSTEM: MessageRole
ROLE_FUNCTION: MessageRole
ROLE_TOOL: MessageRole
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
INVALID_SEARCH_MODE: SearchMode
OFF_SEARCH_MODE: SearchMode
ON_SEARCH_MODE: SearchMode
AUTO_SEARCH_MODE: SearchMode

class GetCompletionsRequest(_message.Message):
    __slots__ = ("messages", "model", "user", "n", "max_tokens", "seed", "stop", "temperature", "top_p", "logprobs", "top_logprobs", "tools", "tool_choice", "response_format", "frequency_penalty", "presence_penalty", "reasoning_effort", "search_parameters", "parallel_tool_calls")
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
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., model: _Optional[str] = ..., user: _Optional[str] = ..., n: _Optional[int] = ..., max_tokens: _Optional[int] = ..., seed: _Optional[int] = ..., stop: _Optional[_Iterable[str]] = ..., temperature: _Optional[float] = ..., top_p: _Optional[float] = ..., logprobs: bool = ..., top_logprobs: _Optional[int] = ..., tools: _Optional[_Iterable[_Union[Tool, _Mapping]]] = ..., tool_choice: _Optional[_Union[ToolChoice, _Mapping]] = ..., response_format: _Optional[_Union[ResponseFormat, _Mapping]] = ..., frequency_penalty: _Optional[float] = ..., presence_penalty: _Optional[float] = ..., reasoning_effort: _Optional[_Union[ReasoningEffort, str]] = ..., search_parameters: _Optional[_Union[SearchParameters, _Mapping]] = ..., parallel_tool_calls: bool = ...) -> None: ...

class GetChatCompletionResponse(_message.Message):
    __slots__ = ("id", "choices", "created", "model", "system_fingerprint", "usage", "citations")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    choices: _containers.RepeatedCompositeFieldContainer[Choice]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., choices: _Optional[_Iterable[_Union[Choice, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ...) -> None: ...

class GetChatCompletionChunk(_message.Message):
    __slots__ = ("id", "choices", "created", "model", "system_fingerprint", "usage", "citations")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    CITATIONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    choices: _containers.RepeatedCompositeFieldContainer[ChoiceChunk]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    citations: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, id: _Optional[str] = ..., choices: _Optional[_Iterable[_Union[ChoiceChunk, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ..., citations: _Optional[_Iterable[str]] = ...) -> None: ...

class GetDeferredCompletionResponse(_message.Message):
    __slots__ = ("status", "response")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status: _deferred_pb2.DeferredStatus
    response: GetChatCompletionResponse
    def __init__(self, status: _Optional[_Union[_deferred_pb2.DeferredStatus, str]] = ..., response: _Optional[_Union[GetChatCompletionResponse, _Mapping]] = ...) -> None: ...

class Choice(_message.Message):
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
    __slots__ = ("content", "reasoning_content", "role", "tool_calls")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ...) -> None: ...

class ChoiceChunk(_message.Message):
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
    __slots__ = ("content", "reasoning_content", "role", "tool_calls")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    content: str
    reasoning_content: str
    role: MessageRole
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    def __init__(self, content: _Optional[str] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("text", "image_url")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    text: str
    image_url: _image_pb2.ImageUrlContent
    def __init__(self, text: _Optional[str] = ..., image_url: _Optional[_Union[_image_pb2.ImageUrlContent, _Mapping]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("content", "reasoning_content", "role", "name", "tool_calls")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    REASONING_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TOOL_CALLS_FIELD_NUMBER: _ClassVar[int]
    content: _containers.RepeatedCompositeFieldContainer[Content]
    reasoning_content: str
    role: MessageRole
    name: str
    tool_calls: _containers.RepeatedCompositeFieldContainer[ToolCall]
    def __init__(self, content: _Optional[_Iterable[_Union[Content, _Mapping]]] = ..., reasoning_content: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., name: _Optional[str] = ..., tool_calls: _Optional[_Iterable[_Union[ToolCall, _Mapping]]] = ...) -> None: ...

class ToolChoice(_message.Message):
    __slots__ = ("mode", "function_name")
    MODE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_NAME_FIELD_NUMBER: _ClassVar[int]
    mode: ToolMode
    function_name: str
    def __init__(self, mode: _Optional[_Union[ToolMode, str]] = ..., function_name: _Optional[str] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("function",)
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    function: Function
    def __init__(self, function: _Optional[_Union[Function, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("id", "function")
    ID_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    function: FunctionCall
    def __init__(self, id: _Optional[str] = ..., function: _Optional[_Union[FunctionCall, _Mapping]] = ...) -> None: ...

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
