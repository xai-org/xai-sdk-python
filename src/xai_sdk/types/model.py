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
    "grok-4.20-beta-0309-reasoning",
    "grok-4.20-beta",
    "grok-4.20-beta-0309",
    "grok-4.20-beta-latest",
    "grok-4.20-beta-latest-reasoning",
    "grok-4.20-beta-0309-non-reasoning",
    "grok-4.20-beta-non-reasoning",
    "grok-4.20-beta-latest-non-reasoning",
    "grok-4.20-multi-agent-beta-0309",
    "grok-4.20-multi-agent-beta-latest",
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
    "grok-imagine-image",
    "grok-imagine-image-pro",
]

VideoGenerationModel: TypeAlias = Literal["grok-imagine-video"]

AllModels: TypeAlias = Union[
    ChatModel,
    ImageGenerationModel,
    VideoGenerationModel,
    str,
]
