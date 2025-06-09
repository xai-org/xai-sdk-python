from google.protobuf import timestamp_pb2 as _timestamp_pb2
from . import usage_pb2 as _usage_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FinishReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REASON_INVALID: _ClassVar[FinishReason]
    REASON_MAX_LEN: _ClassVar[FinishReason]
    REASON_MAX_CONTEXT: _ClassVar[FinishReason]
    REASON_STOP: _ClassVar[FinishReason]
    REASON_TOOL_CALLS: _ClassVar[FinishReason]
    REASON_TIME_LIMIT: _ClassVar[FinishReason]
REASON_INVALID: FinishReason
REASON_MAX_LEN: FinishReason
REASON_MAX_CONTEXT: FinishReason
REASON_STOP: FinishReason
REASON_TOOL_CALLS: FinishReason
REASON_TIME_LIMIT: FinishReason

class SampleTextRequest(_message.Message):
    __slots__ = ("prompt", "model", "n", "max_tokens", "seed", "stop", "temperature", "top_p", "frequency_penalty", "logprobs", "presence_penalty", "top_logprobs", "user")
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    N_FIELD_NUMBER: _ClassVar[int]
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    TEMPERATURE_FIELD_NUMBER: _ClassVar[int]
    TOP_P_FIELD_NUMBER: _ClassVar[int]
    FREQUENCY_PENALTY_FIELD_NUMBER: _ClassVar[int]
    LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_PENALTY_FIELD_NUMBER: _ClassVar[int]
    TOP_LOGPROBS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    prompt: _containers.RepeatedScalarFieldContainer[str]
    model: str
    n: int
    max_tokens: int
    seed: int
    stop: _containers.RepeatedScalarFieldContainer[str]
    temperature: float
    top_p: float
    frequency_penalty: float
    logprobs: bool
    presence_penalty: float
    top_logprobs: int
    user: str
    def __init__(self, prompt: _Optional[_Iterable[str]] = ..., model: _Optional[str] = ..., n: _Optional[int] = ..., max_tokens: _Optional[int] = ..., seed: _Optional[int] = ..., stop: _Optional[_Iterable[str]] = ..., temperature: _Optional[float] = ..., top_p: _Optional[float] = ..., frequency_penalty: _Optional[float] = ..., logprobs: bool = ..., presence_penalty: _Optional[float] = ..., top_logprobs: _Optional[int] = ..., user: _Optional[str] = ...) -> None: ...

class SampleTextResponse(_message.Message):
    __slots__ = ("id", "choices", "created", "model", "system_fingerprint", "usage")
    ID_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    choices: _containers.RepeatedCompositeFieldContainer[SampleChoice]
    created: _timestamp_pb2.Timestamp
    model: str
    system_fingerprint: str
    usage: _usage_pb2.SamplingUsage
    def __init__(self, id: _Optional[str] = ..., choices: _Optional[_Iterable[_Union[SampleChoice, _Mapping]]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model: _Optional[str] = ..., system_fingerprint: _Optional[str] = ..., usage: _Optional[_Union[_usage_pb2.SamplingUsage, _Mapping]] = ...) -> None: ...

class SampleChoice(_message.Message):
    __slots__ = ("finish_reason", "index", "text")
    FINISH_REASON_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    finish_reason: FinishReason
    index: int
    text: str
    def __init__(self, finish_reason: _Optional[_Union[FinishReason, str]] = ..., index: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...
