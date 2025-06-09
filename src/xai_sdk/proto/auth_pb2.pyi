from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApiKey(_message.Message):
    __slots__ = ("redacted_api_key", "user_id", "name", "create_time", "modify_time", "modified_by", "team_id", "acls", "api_key_id", "api_key_blocked", "team_blocked", "disabled")
    REDACTED_API_KEY_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    MODIFY_TIME_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    ACLS_FIELD_NUMBER: _ClassVar[int]
    API_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    API_KEY_BLOCKED_FIELD_NUMBER: _ClassVar[int]
    TEAM_BLOCKED_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    redacted_api_key: str
    user_id: str
    name: str
    create_time: _timestamp_pb2.Timestamp
    modify_time: _timestamp_pb2.Timestamp
    modified_by: str
    team_id: str
    acls: _containers.RepeatedScalarFieldContainer[str]
    api_key_id: str
    api_key_blocked: bool
    team_blocked: bool
    disabled: bool
    def __init__(self, redacted_api_key: _Optional[str] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., create_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modify_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., modified_by: _Optional[str] = ..., team_id: _Optional[str] = ..., acls: _Optional[_Iterable[str]] = ..., api_key_id: _Optional[str] = ..., api_key_blocked: bool = ..., team_blocked: bool = ..., disabled: bool = ...) -> None: ...
