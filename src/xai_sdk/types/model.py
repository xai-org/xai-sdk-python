from typing import Literal, TypeAlias, Union

__all__ = ["AllModels", "ChatModel", "ImageGenerationModel", "VideoGenerationModel"]

ChatModel: TypeAlias = Literal[
    "grok-4",
    "grok-4-0709",
    "grok-4-latest",
    "grok-4-1-fast",
    "grok-4-1-fast-reasoning",
    "grok-4-1-fast-reasoning-latest",
    "grok-4-1-fast-non-reasoning",
    "grok-4-1-fast-non-reasoning-latest",
    "grok-4-fast",
    "grok-4-fast-reasoning",
    "grok-4-fast-reasoning-latest",
    "grok-4-fast-non-reasoning",
    "grok-4-fast-non-reasoning-latest",
    "grok-code-fast-1",
    "grok-3",
    "grok-3-latest",
    "grok-3-mini",
    "grok-3-fast",
    "grok-3-fast-latest",
    "grok-3-mini-fast",
    "grok-3-mini-fast-latest",
]

ImageGenerationModel: TypeAlias = Literal[
    "grok-2-image",
    "grok-2-image-1212",
    "grok-2-image-latest",
    "grok-imagine-image",
]

VideoGenerationModel: TypeAlias = Literal["grok-imagine-video"]

AllModels: TypeAlias = Union[
    ChatModel,
    ImageGenerationModel,
    VideoGenerationModel,
    str,
]
