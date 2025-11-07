from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ordering(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASCENDING: _ClassVar[Ordering]
    DESCENDING: _ClassVar[Ordering]

class FilesSortBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FILES_SORT_BY_CREATED_AT: _ClassVar[FilesSortBy]
    FILES_SORT_BY_FILENAME: _ClassVar[FilesSortBy]
    FILES_SORT_BY_SIZE: _ClassVar[FilesSortBy]
ASCENDING: Ordering
DESCENDING: Ordering
FILES_SORT_BY_CREATED_AT: FilesSortBy
FILES_SORT_BY_FILENAME: FilesSortBy
FILES_SORT_BY_SIZE: FilesSortBy

class UploadFileInit(_message.Message):
    __slots__ = ("name", "purpose")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    name: str
    purpose: str
    def __init__(self, name: _Optional[str] = ..., purpose: _Optional[str] = ...) -> None: ...

class UploadFileChunk(_message.Message):
    __slots__ = ("init", "data")
    INIT_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    init: UploadFileInit
    data: bytes
    def __init__(self, init: _Optional[_Union[UploadFileInit, _Mapping]] = ..., data: _Optional[bytes] = ...) -> None: ...

class File(_message.Message):
    __slots__ = ("size", "created_at", "expires_at", "filename", "id", "team_id")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_ID_FIELD_NUMBER: _ClassVar[int]
    size: int
    created_at: _timestamp_pb2.Timestamp
    expires_at: _timestamp_pb2.Timestamp
    filename: str
    id: str
    team_id: str
    def __init__(self, size: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expires_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., filename: _Optional[str] = ..., id: _Optional[str] = ..., team_id: _Optional[str] = ...) -> None: ...

class ListFilesRequest(_message.Message):
    __slots__ = ("limit", "order", "pagination_token", "sort_by")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SORT_BY_FIELD_NUMBER: _ClassVar[int]
    limit: int
    order: Ordering
    pagination_token: str
    sort_by: FilesSortBy
    def __init__(self, limit: _Optional[int] = ..., order: _Optional[_Union[Ordering, str]] = ..., pagination_token: _Optional[str] = ..., sort_by: _Optional[_Union[FilesSortBy, str]] = ...) -> None: ...

class ListFilesResponse(_message.Message):
    __slots__ = ("data", "pagination_token")
    DATA_FIELD_NUMBER: _ClassVar[int]
    PAGINATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[File]
    pagination_token: str
    def __init__(self, data: _Optional[_Iterable[_Union[File, _Mapping]]] = ..., pagination_token: _Optional[str] = ...) -> None: ...

class RetrieveFileRequest(_message.Message):
    __slots__ = ("file_id",)
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    def __init__(self, file_id: _Optional[str] = ...) -> None: ...

class DeleteFileRequest(_message.Message):
    __slots__ = ("file_id",)
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    def __init__(self, file_id: _Optional[str] = ...) -> None: ...

class DeleteFileResponse(_message.Message):
    __slots__ = ("id", "deleted")
    ID_FIELD_NUMBER: _ClassVar[int]
    DELETED_FIELD_NUMBER: _ClassVar[int]
    id: str
    deleted: bool
    def __init__(self, id: _Optional[str] = ..., deleted: bool = ...) -> None: ...

class RetrieveFileContentRequest(_message.Message):
    __slots__ = ("file_id",)
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    def __init__(self, file_id: _Optional[str] = ...) -> None: ...

class FileContentChunk(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class RetrieveFileURLRequest(_message.Message):
    __slots__ = ("file_id",)
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    def __init__(self, file_id: _Optional[str] = ...) -> None: ...

class RetrieveFileURLResponse(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...
