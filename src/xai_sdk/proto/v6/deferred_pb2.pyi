from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DeferredStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_DEFERRED_STATUS: _ClassVar[DeferredStatus]
    DONE: _ClassVar[DeferredStatus]
    EXPIRED: _ClassVar[DeferredStatus]
    PENDING: _ClassVar[DeferredStatus]
INVALID_DEFERRED_STATUS: DeferredStatus
DONE: DeferredStatus
EXPIRED: DeferredStatus
PENDING: DeferredStatus

class StartDeferredResponse(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...

class GetDeferredRequest(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    def __init__(self, request_id: _Optional[str] = ...) -> None: ...
