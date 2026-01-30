from typing import Literal, TypeAlias, Union

__all__ = ["AllModels", "ChatModel", "ImageGenerationModel", "VideoGenerationModel"]

ChatModel: TypeAlias = Literal[
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast-non-reasoning",
    "grok-code-fast-1",
]

ImageGenerationModel: TypeAlias = Literal["grok-imagine-image"]

VideoGenerationModel: TypeAlias = Literal["grok-imagine-video"]

AllModels: TypeAlias = Union[
    ChatModel,
    ImageGenerationModel,
    VideoGenerationModel,
    str,
]
