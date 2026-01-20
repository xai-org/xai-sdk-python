from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.rpc import status_pb2 as _status_pb2
from . import chat_pb2 as _chat_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Batch(_message.Message):
    __slots__ = ("batch_id", "name", "create_time", "expire_time", "create_api_key_id", "cancel_time", "cancel_by_xai_message", "state", "cost_breakdown")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATE_API_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    CANCEL_TIME_FIELD_NUMBER: _ClassVar[int]
    CANCEL_BY_XAI_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COST_BREAKDOWN_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    name: str
    create_time: _timestamp_pb2.Timestamp
    expire_time: _timestamp_pb2.Timestamp
    create_api_key_id: str
    cancel_time: _timestamp_pb2.Timestamp
    cancel_by_xai_message: str
    state: BatchState
    cost_breakdown: BatchCostBreakdown
    def __init__(self, batch_id: _Optional[str] = ..., name: _Optional[str] = ..., create_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expire_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., create_api_key_id: _Optional[str] = ..., cancel_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cancel_by_xai_message: _Optional[str] = ..., state: _Optional[_Union[BatchState, _Mapping]] = ..., cost_breakdown: _Optional[_Union[BatchCostBreakdown, _Mapping]] = ...) -> None: ...

class BatchState(_message.Message):
    __slots__ = ("num_requests", "num_pending", "num_success", "num_error", "num_cancelled")
    NUM_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    NUM_PENDING_FIELD_NUMBER: _ClassVar[int]
    NUM_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    NUM_ERROR_FIELD_NUMBER: _ClassVar[int]
    NUM_CANCELLED_FIELD_NUMBER: _ClassVar[int]
    num_requests: int
    num_pending: int
    num_success: int
    num_error: int
    num_cancelled: int
    def __init__(self, num_requests: _Optional[int] = ..., num_pending: _Optional[int] = ..., num_success: _Optional[int] = ..., num_error: _Optional[int] = ..., num_cancelled: _Optional[int] = ...) -> None: ...

class BatchCostBreakdown(_message.Message):
    __slots__ = ("total_cost_usd_ticks", "endpoint_costs", "calculation_time")
    TOTAL_COST_USD_TICKS_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_COSTS_FIELD_NUMBER: _ClassVar[int]
    CALCULATION_TIME_FIELD_NUMBER: _ClassVar[int]
    total_cost_usd_ticks: int
    endpoint_costs: _containers.RepeatedCompositeFieldContainer[EndpointCost]
    calculation_time: _timestamp_pb2.Timestamp
    def __init__(self, total_cost_usd_ticks: _Optional[int] = ..., endpoint_costs: _Optional[_Iterable[_Union[EndpointCost, _Mapping]]] = ..., calculation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class EndpointCost(_message.Message):
    __slots__ = ("endpoint", "cost_usd_ticks", "request_count")
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    COST_USD_TICKS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_COUNT_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    cost_usd_ticks: int
    request_count: int
    def __init__(self, endpoint: _Optional[str] = ..., cost_usd_ticks: _Optional[int] = ..., request_count: _Optional[int] = ...) -> None: ...

class BatchRequest(_message.Message):
    __slots__ = ("batch_request_id", "completion_request")
    BATCH_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    batch_request_id: str
    completion_request: _chat_pb2.GetCompletionsRequest
    def __init__(self, batch_request_id: _Optional[str] = ..., completion_request: _Optional[_Union[_chat_pb2.GetCompletionsRequest, _Mapping]] = ...) -> None: ...

class BatchResultData(_message.Message):
    __slots__ = ("completion_response",)
    COMPLETION_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    completion_response: _chat_pb2.GetChatCompletionResponse
    def __init__(self, completion_response: _Optional[_Union[_chat_pb2.GetChatCompletionResponse, _Mapping]] = ...) -> None: ...

class BatchResult(_message.Message):
    __slots__ = ("batch_request_id", "response", "error")
    BATCH_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    batch_request_id: str
    response: BatchResultData
    error: _status_pb2.Status
    def __init__(self, batch_request_id: _Optional[str] = ..., response: _Optional[_Union[BatchResultData, _Mapping]] = ..., error: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class BatchRequestMetadata(_message.Message):
    __slots__ = ("batch_request_id", "endpoint", "model", "state", "create_time", "finish_time")
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATE_UNKNOWN: _ClassVar[BatchRequestMetadata.State]
        STATE_PENDING: _ClassVar[BatchRequestMetadata.State]
        STATE_SUCCEEDED: _ClassVar[BatchRequestMetadata.State]
        STATE_CANCELLED: _ClassVar[BatchRequestMetadata.State]
        STATE_FAILED: _ClassVar[BatchRequestMetadata.State]
    STATE_UNKNOWN: BatchRequestMetadata.State
    STATE_PENDING: BatchRequestMetadata.State
    STATE_SUCCEEDED: BatchRequestMetadata.State
    STATE_CANCELLED: BatchRequestMetadata.State
    STATE_FAILED: BatchRequestMetadata.State
    BATCH_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    FINISH_TIME_FIELD_NUMBER: _ClassVar[int]
    batch_request_id: str
    endpoint: str
    model: str
    state: BatchRequestMetadata.State
    create_time: _timestamp_pb2.Timestamp
    finish_time: _timestamp_pb2.Timestamp
    def __init__(self, batch_request_id: _Optional[str] = ..., endpoint: _Optional[str] = ..., model: _Optional[str] = ..., state: _Optional[_Union[BatchRequestMetadata.State, str]] = ..., create_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., finish_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateBatchRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class AddBatchRequestsRequest(_message.Message):
    __slots__ = ("batch_id", "batch_requests")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_REQUESTS_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    batch_requests: _containers.RepeatedCompositeFieldContainer[BatchRequest]
    def __init__(self, batch_id: _Optional[str] = ..., batch_requests: _Optional[_Iterable[_Union[BatchRequest, _Mapping]]] = ...) -> None: ...

class GetBatchRequest(_message.Message):
    __slots__ = ("batch_id",)
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    def __init__(self, batch_id: _Optional[str] = ...) -> None: ...

class ListBatchesRequest(_message.Message):
    __slots__ = ("limit", "pagination_token")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    limit: int
    pagination_token: str
    def __init__(self, limit: _Optional[int] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class ListBatchesResponse(_message.Message):
    __slots__ = ("batches", "pagination_token")
    BATCHES_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    batches: _containers.RepeatedCompositeFieldContainer[Batch]
    pagination_token: str
    def __init__(self, batches: _Optional[_Iterable[_Union[Batch, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class CancelBatchRequest(_message.Message):
    __slots__ = ("batch_id",)
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    def __init__(self, batch_id: _Optional[str] = ...) -> None: ...

class ListBatchRequestMetadataRequest(_message.Message):
    __slots__ = ("batch_id", "limit", "pagination_token")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    limit: int
    pagination_token: str
    def __init__(self, batch_id: _Optional[str] = ..., limit: _Optional[int] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class ListBatchRequestMetadataResponse(_message.Message):
    __slots__ = ("batch_request_metadata", "pagination_token")
    BATCH_REQUEST_METADATA_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    batch_request_metadata: _containers.RepeatedCompositeFieldContainer[BatchRequestMetadata]
    pagination_token: str
    def __init__(self, batch_request_metadata: _Optional[_Iterable[_Union[BatchRequestMetadata, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class ListBatchResultsRequest(_message.Message):
    __slots__ = ("batch_id", "limit", "pagination_token")
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    batch_id: str
    limit: int
    pagination_token: str
    def __init__(self, batch_id: _Optional[str] = ..., limit: _Optional[int] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class ListBatchResultsResponse(_message.Message):
    __slots__ = ("results", "pagination_token")
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[BatchResult]
    pagination_token: str
    def __init__(self, results: _Optional[_Iterable[_Union[BatchResult, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...
