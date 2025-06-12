from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Modality(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_MODALITY: _ClassVar[Modality]
    TEXT: _ClassVar[Modality]
    IMAGE: _ClassVar[Modality]
    EMBEDDING: _ClassVar[Modality]
INVALID_MODALITY: Modality
TEXT: Modality
IMAGE: Modality
EMBEDDING: Modality

class GetModelRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class LanguageModel(_message.Message):
    __slots__ = ("name", "aliases", "version", "input_modalities", "output_modalities", "prompt_text_token_price", "prompt_image_token_price", "cached_prompt_token_price", "completion_text_token_price", "search_price", "created", "max_prompt_length", "system_fingerprint")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TEXT_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_IMAGE_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    CACHED_PROMPT_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_TEXT_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MAX_PROMPT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    aliases: _containers.RepeatedScalarFieldContainer[str]
    version: str
    input_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    output_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    prompt_text_token_price: int
    prompt_image_token_price: int
    cached_prompt_token_price: int
    completion_text_token_price: int
    search_price: int
    created: _timestamp_pb2.Timestamp
    max_prompt_length: int
    system_fingerprint: str
    def __init__(self, name: _Optional[str] = ..., aliases: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ..., input_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., output_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., prompt_text_token_price: _Optional[int] = ..., prompt_image_token_price: _Optional[int] = ..., cached_prompt_token_price: _Optional[int] = ..., completion_text_token_price: _Optional[int] = ..., search_price: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., max_prompt_length: _Optional[int] = ..., system_fingerprint: _Optional[str] = ...) -> None: ...

class ListLanguageModelsResponse(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[LanguageModel]
    def __init__(self, models: _Optional[_Iterable[_Union[LanguageModel, _Mapping]]] = ...) -> None: ...

class EmbeddingModel(_message.Message):
    __slots__ = ("name", "aliases", "version", "input_modalities", "output_modalities", "prompt_text_token_price", "prompt_image_token_price", "created", "system_fingerprint")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    PROMPT_TEXT_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_IMAGE_TOKEN_PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    aliases: _containers.RepeatedScalarFieldContainer[str]
    version: str
    input_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    output_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    prompt_text_token_price: int
    prompt_image_token_price: int
    created: _timestamp_pb2.Timestamp
    system_fingerprint: str
    def __init__(self, name: _Optional[str] = ..., aliases: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ..., input_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., output_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., prompt_text_token_price: _Optional[int] = ..., prompt_image_token_price: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., system_fingerprint: _Optional[str] = ...) -> None: ...

class ListEmbeddingModelsResponse(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[EmbeddingModel]
    def __init__(self, models: _Optional[_Iterable[_Union[EmbeddingModel, _Mapping]]] = ...) -> None: ...

class ImageGenerationModel(_message.Message):
    __slots__ = ("name", "aliases", "version", "input_modalities", "output_modalities", "image_price", "created", "max_prompt_length", "system_fingerprint")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALIASES_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    INPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_MODALITIES_FIELD_NUMBER: _ClassVar[int]
    IMAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    MAX_PROMPT_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    name: str
    aliases: _containers.RepeatedScalarFieldContainer[str]
    version: str
    input_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    output_modalities: _containers.RepeatedScalarFieldContainer[Modality]
    image_price: int
    created: _timestamp_pb2.Timestamp
    max_prompt_length: int
    system_fingerprint: str
    def __init__(self, name: _Optional[str] = ..., aliases: _Optional[_Iterable[str]] = ..., version: _Optional[str] = ..., input_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., output_modalities: _Optional[_Iterable[_Union[Modality, str]]] = ..., image_price: _Optional[int] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., max_prompt_length: _Optional[int] = ..., system_fingerprint: _Optional[str] = ...) -> None: ...

class ListImageGenerationModelsResponse(_message.Message):
    __slots__ = ("models",)
    MODELS_FIELD_NUMBER: _ClassVar[int]
    models: _containers.RepeatedCompositeFieldContainer[ImageGenerationModel]
    def __init__(self, models: _Optional[_Iterable[_Union[ImageGenerationModel, _Mapping]]] = ...) -> None: ...
