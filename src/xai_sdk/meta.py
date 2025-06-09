import pprint
from typing import Generic, TypeVar

T = TypeVar("T")


class ProtoDecorator(Generic[T]):
    """A generic decorator for wrapping protocol buffer objects to simplify interaction.

    This class provides a Pythonic interface for working with raw protocol buffers by
    encapsulating the proto instance and exposing it through a property. It is designed
    to be subclassed to add proto-specific methods and properties, enhancing usability
    with type safety via generics. Commonly used in the xAI SDK to handle API response
    protos, such as those for chat or image generation.

    Args:
        proto: The protocol buffer instance to wrap.

    Attributes:
        proto: The underlying protocol buffer instance.

    Example:
        ```python
        from .proto import image_pb2
        class ImageResponse(ProtoDecorator[image_pb2.ImageResponse]):
            @property
            def base64(self) -> str:
                value = self._proto.base64
                if not value:
                    raise ValueError("Image was not returned via base64.")
                return value

        # Usage
        proto = image_pb2.ImageResponse(base64="some_base64_string")
        response = ImageResponse(proto)
        print(response.base64)  # Access base64 string
        print(response.proto)   # Access raw proto
        print(response)         # Pretty-printed proto
        ```

    Note:
        Subclasses should define additional methods or properties to interact with
        specific fields of the wrapped proto, as shown in the example.
    """

    _proto: T

    def __init__(self, proto: T) -> None:
        """Initializes a new instance of the `ProtoDecorator` class.

        Args:
            proto: The proto instance to wrap.
        """
        self._proto = proto

    @property
    def proto(self) -> T:
        """Returns the underlying protocol buffer."""
        return self._proto

    def __repr__(self):
        return pprint.pformat(self._proto)
