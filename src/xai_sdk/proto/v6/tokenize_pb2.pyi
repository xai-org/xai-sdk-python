from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TokenizeTextRequest(_message.Message):
    __slots__ = ("text", "model", "user")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    text: str
    model: str
    user: str
    def __init__(self, text: _Optional[str] = ..., model: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...

class Token(_message.Message):
    __slots__ = ("token_id", "string_token", "token_bytes")
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    STRING_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_BYTES_FIELD_NUMBER: _ClassVar[int]
    token_id: int
    string_token: str
    token_bytes: bytes
    def __init__(self, token_id: _Optional[int] = ..., string_token: _Optional[str] = ..., token_bytes: _Optional[bytes] = ...) -> None: ...

class TokenizeTextResponse(_message.Message):
    __slots__ = ("tokens", "model")
    TOKENS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    tokens: _containers.RepeatedCompositeFieldContainer[Token]
    model: str
    def __init__(self, tokens: _Optional[_Iterable[_Union[Token, _Mapping]]] = ..., model: _Optional[str] = ...) -> None: ...
