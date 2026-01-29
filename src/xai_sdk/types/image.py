from typing import Literal, TypeAlias

__all__ = ["ImageAspectRatio", "ImageFormat", "ImageResolution"]

ImageFormat: TypeAlias = Literal["base64", "url"]
ImageAspectRatio: TypeAlias = Literal[
    "1:1",
    "3:4",
    "4:3",
    "9:16",
    "16:9",
    "2:3",
    "3:2",
    "9:19.5",
    "19.5:9",
    "9:20",
    "20:9",
    "1:2",
    "2:1",
]
ImageResolution: TypeAlias = Literal["1k"]
