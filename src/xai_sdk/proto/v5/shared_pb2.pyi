from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class Ordering(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDERING_UNKNOWN: _ClassVar[Ordering]
    ORDERING_ASCENDING: _ClassVar[Ordering]
    ORDERING_DESCENDING: _ClassVar[Ordering]
ORDERING_UNKNOWN: Ordering
ORDERING_ASCENDING: Ordering
ORDERING_DESCENDING: Ordering
