import asyncio
import os
from typing import Any, AsyncIterator, BinaryIO, Callable, Iterator, Literal, Protocol, Union

import grpc

from .proto import files_pb2, files_pb2_grpc

# Chunk size for file uploads (3 MiB)
_CHUNK_SIZE = 3 << 20

Order = Literal["asc", "desc"]
SortBy = Literal["created_at", "filename", "size"]


class ProgressBarLike(Protocol):
    """Protocol for tqdm-like progress bars."""

    def update(self, n: int) -> Any:
        """Update progress by n units."""
        ...


# Type for progress tracking - either a callable or an object with update() method
ProgressCallback = Union[Callable[[int, int], None], Callable[[int], None], ProgressBarLike, None]

# Type for batch upload completion callbacks
BatchUploadCallback = Callable[[int, Union[str, BinaryIO], Union["files_pb2.File", BaseException]], None]


class BaseClient:
    """Base Client for interacting with the `Files` API."""

    _stub: files_pb2_grpc.FilesStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = files_pb2_grpc.FilesStub(channel)


def _invoke_progress(
    progress: ProgressCallback, chunk_size: int, cumulative_bytes: int, total_bytes: int | None = None
) -> None:
    """Invoke progress callback, supporting both callable and tqdm-like objects.

    Args:
        progress: Either a callable or an object with an update() method (like tqdm).
        chunk_size: Size of the chunk just sent (for incremental updates).
        cumulative_bytes: Total number of bytes uploaded so far.
        total_bytes: Total number of bytes to upload (optional).
    """
    if progress is None:
        return

    # Check if it has an update method (tqdm-like object)
    if hasattr(progress, "update") and callable(getattr(progress, "update", None)):
        # tqdm expects incremental updates
        progress.update(chunk_size)  # type: ignore
    # Check if it's a callable (function)
    elif callable(progress):
        # Try calling with both arguments first (custom callback with total)
        try:
            progress(cumulative_bytes, total_bytes)  # type: ignore
        except TypeError:
            # If that fails, try calling with just incremental bytes (tqdm.update style)
            progress(chunk_size)  # type: ignore


def _order_to_pb(order: Order | None) -> files_pb2.Ordering:
    """Converts order string to protobuf enum."""
    match order:
        case "asc":
            return files_pb2.Ordering.ASCENDING
        case "desc":
            return files_pb2.Ordering.DESCENDING
        case _:
            return files_pb2.Ordering.ASCENDING


def _sort_by_to_pb(sort_by: SortBy | None) -> files_pb2.FilesSortBy:
    """Converts sort_by string to protobuf enum."""
    match sort_by:
        case "created_at":
            return files_pb2.FilesSortBy.FILES_SORT_BY_CREATED_AT
        case "filename":
            return files_pb2.FilesSortBy.FILES_SORT_BY_FILENAME
        case "size":
            return files_pb2.FilesSortBy.FILES_SORT_BY_SIZE
        case _:
            return files_pb2.FilesSortBy.FILES_SORT_BY_CREATED_AT


def _chunk_file_data(
    filename: str, data: bytes, progress: ProgressCallback = None
) -> Iterator[files_pb2.UploadFileChunk]:
    """Generator that yields file upload chunks.

    First yields the initialization chunk with metadata, then yields data chunks.

    Args:
        filename: Name of the file being uploaded.
        data: The file data as bytes.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    total_bytes = len(data)
    bytes_uploaded = 0

    # Subsequent chunks: file data
    for i in range(0, len(data), _CHUNK_SIZE):
        chunk_data = data[i : i + _CHUNK_SIZE]
        chunk_size = len(chunk_data)
        bytes_uploaded += chunk_size

        yield files_pb2.UploadFileChunk(data=chunk_data)

        _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)


def _chunk_file_from_path(file_path: str, progress: ProgressCallback = None) -> Iterator[files_pb2.UploadFileChunk]:
    """Generator that yields file upload chunks by streaming from disk.

    This method reads the file in chunks rather than loading it entirely into memory,
    making it suitable for large files.

    Args:
        file_path: Path to the file to upload.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    filename = os.path.basename(file_path)
    total_bytes = os.path.getsize(file_path)
    bytes_uploaded = 0

    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    # Subsequent chunks: stream file data from disk
    with open(file_path, "rb") as f:
        while chunk_data := f.read(_CHUNK_SIZE):
            chunk_size = len(chunk_data)
            bytes_uploaded += chunk_size

            yield files_pb2.UploadFileChunk(data=chunk_data)

            _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)


def _chunk_file_from_fileobj(
    file_obj: BinaryIO, filename: str, progress: ProgressCallback = None
) -> Iterator[files_pb2.UploadFileChunk]:
    """Generator that yields file upload chunks from a file-like object.

    Args:
        file_obj: Binary file-like object to read from.
        filename: Name to use for the uploaded file.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    # Try to determine total size if possible
    total_bytes = None
    bytes_uploaded = 0
    try:
        current_pos = file_obj.tell()
        file_obj.seek(0, 2)  # Seek to end
        total_bytes = file_obj.tell()
        file_obj.seek(current_pos)  # Return to original position
    except (OSError, AttributeError):
        # Not all file objects support seek/tell (e.g., streams)
        pass

    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    # Stream file data from file object
    while chunk_data := file_obj.read(_CHUNK_SIZE):
        chunk_size = len(chunk_data)
        bytes_uploaded += chunk_size

        yield files_pb2.UploadFileChunk(data=chunk_data)

        _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)


# Async versions for AsyncClient


async def _async_chunk_file_data(
    filename: str, data: bytes, progress: ProgressCallback = None
) -> AsyncIterator[files_pb2.UploadFileChunk]:
    """Async generator that yields file upload chunks.

    First yields the initialization chunk with metadata, then yields data chunks.

    Args:
        filename: Name of the file being uploaded.
        data: The file data as bytes.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    total_bytes = len(data)
    bytes_uploaded = 0

    # Subsequent chunks: file data
    for i in range(0, len(data), _CHUNK_SIZE):
        chunk_data = data[i : i + _CHUNK_SIZE]
        chunk_size = len(chunk_data)
        bytes_uploaded += chunk_size

        yield files_pb2.UploadFileChunk(data=chunk_data)

        _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)


async def _async_chunk_file_from_path(
    file_path: str, progress: ProgressCallback = None
) -> AsyncIterator[files_pb2.UploadFileChunk]:
    """Async generator that yields file upload chunks by streaming from disk.

    This method reads the file in chunks using asyncio to avoid blocking the event loop,
    making it suitable for large files in async contexts.

    Args:
        file_path: Path to the file to upload.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    filename = os.path.basename(file_path)
    total_bytes = os.path.getsize(file_path)
    bytes_uploaded = 0

    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    # Use asyncio to read file without blocking
    loop = asyncio.get_event_loop()

    def read_chunk(f):
        return f.read(_CHUNK_SIZE)

    with open(file_path, "rb") as f:
        while True:
            # Read chunk in executor to avoid blocking event loop
            chunk_data = await loop.run_in_executor(None, read_chunk, f)
            if not chunk_data:
                break

            chunk_size = len(chunk_data)
            bytes_uploaded += chunk_size

            yield files_pb2.UploadFileChunk(data=chunk_data)

            _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)


async def _async_chunk_file_from_fileobj(
    file_obj: BinaryIO, filename: str, progress: ProgressCallback = None
) -> AsyncIterator[files_pb2.UploadFileChunk]:
    """Async generator that yields file upload chunks from a file-like object.

    Args:
        file_obj: Binary file-like object to read from.
        filename: Name to use for the uploaded file.
        progress: Optional progress callback or tqdm-like object.

    Yields:
        UploadFileChunk messages containing either init metadata or data.
    """
    # Try to determine total size if possible
    total_bytes = None
    bytes_uploaded = 0
    try:
        current_pos = file_obj.tell()
        file_obj.seek(0, 2)  # Seek to end
        total_bytes = file_obj.tell()
        file_obj.seek(current_pos)  # Return to original position
    except (OSError, AttributeError):
        # Not all file objects support seek/tell (e.g., streams)
        pass

    # First chunk: initialization with metadata
    yield files_pb2.UploadFileChunk(
        init=files_pb2.UploadFileInit(
            name=filename,
            purpose="",  # Purpose is unused by backend
        )
    )

    # Use asyncio to read file without blocking
    loop = asyncio.get_event_loop()

    def read_chunk():
        return file_obj.read(_CHUNK_SIZE)

    # Stream file data from file object
    while True:
        chunk_data = await loop.run_in_executor(None, read_chunk)
        if not chunk_data:
            break

        chunk_size = len(chunk_data)
        bytes_uploaded += chunk_size

        yield files_pb2.UploadFileChunk(data=chunk_data)

        _invoke_progress(progress, chunk_size, bytes_uploaded, total_bytes)
