"""Unit tests for synchronous Files API client."""

import io
import os
import tempfile
from typing import Callable, Iterable, Optional
from unittest import mock

import pytest
from google.protobuf import timestamp_pb2

from xai_sdk import Client
from xai_sdk.files import _chunk_file_data, _chunk_file_from_path, _order_to_pb, _sort_by_to_pb
from xai_sdk.proto import files_pb2


def _extract_file_index_from_chunks(chunks: Iterable[files_pb2.UploadFileChunk]) -> int:
    """Extract file index from chunk content.

    Helper function to identify which file is being uploaded based on its content.
    This is thread-safe and doesn't rely on execution order.
    """
    chunk_list = list(chunks)
    # Get the content to identify which file this is
    content = b"".join(c.data for c in chunk_list if c.HasField("data"))
    content_str = content.decode("utf-8")
    # Extract index from "content {i}"
    idx = int(content_str.split()[1])
    return idx


def create_mock_upload_handler(
    fail_on_indices: Optional[Iterable[int]] = None,
) -> Callable[[Iterable[files_pb2.UploadFileChunk]], files_pb2.File]:
    """Create a mock upload handler function.

    Args:
        fail_on_indices: Optional set/list of file indices that should fail.
                        If None, all uploads succeed.

    Returns:
        A mock upload function suitable for use as UploadFile.side_effect
    """
    fail_on_indices_set = set(fail_on_indices or [])

    def mock_upload(chunks: Iterable[files_pb2.UploadFileChunk]) -> files_pb2.File:
        idx = _extract_file_index_from_chunks(chunks)

        if idx in fail_on_indices_set:
            raise RuntimeError(f"Upload failed for file {idx}")

        return files_pb2.File(
            id=f"file-{idx}",
            filename=f"batch_{idx}.txt",
            size=100,
            team_id="team-456",
        )

    return mock_upload


@pytest.fixture
def mock_stub():
    """Create a mock FilesStub."""
    return mock.MagicMock()


@pytest.fixture
def client_with_mock_stub(mock_stub):
    """Create a client with a mocked stub."""
    with mock.patch("xai_sdk.files.files_pb2_grpc.FilesStub", return_value=mock_stub):
        client = Client(api_key="test-api-key")
        yield client
        # Explicitly reset mock to ensure no state leakage across test repetitions
        mock_stub.reset_mock()


def test_upload_file(client_with_mock_stub: Client, mock_stub):
    """Test uploading a file from a file path."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content")
        temp_file_path = f.name

    try:
        # Mock the response
        mock_response = files_pb2.File(
            id="file-123",
            filename="test.txt",
            size=12,
            team_id="team-456",
        )
        mock_stub.UploadFile.return_value = mock_response

        # Call upload
        result = client_with_mock_stub.files.upload(temp_file_path)

        # Verify the stub was called
        assert mock_stub.UploadFile.called

        # Verify the response
        assert result.id == "file-123"
        assert result.filename == "test.txt"
        assert result.size == 12
        assert result.team_id == "team-456"
    finally:
        os.unlink(temp_file_path)


def test_upload_file_not_found(client_with_mock_stub: Client):
    """Test uploading a file that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        client_with_mock_stub.files.upload("/nonexistent/file.txt")


def test_upload_bytes(client_with_mock_stub: Client, mock_stub):
    """Test uploading file from bytes."""
    data = b"test content"
    filename = "test.txt"

    # Mock the response
    mock_response = files_pb2.File(
        id="file-123",
        filename=filename,
        size=len(data),
        team_id="team-456",
    )
    mock_stub.UploadFile.return_value = mock_response

    # Call upload with bytes
    result = client_with_mock_stub.files.upload(data, filename=filename)

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-123"
    assert result.filename == "test.txt"
    assert result.size == len(data)


def test_upload_file_object(client_with_mock_stub: Client, mock_stub):
    """Test uploading a file from a file-like object."""
    mock_response = files_pb2.File(
        id="file-789",
        filename="stream.txt",
        size=30,
        team_id="team-abc",
    )
    mock_stub.UploadFile.return_value = mock_response

    # Create a file-like object
    file_obj = io.BytesIO(b"Data from file object")

    # Call upload with file object
    result = client_with_mock_stub.files.upload(file_obj, filename="stream.txt")

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-789"
    assert result.filename == "stream.txt"
    assert result.size == 30


def test_upload_with_progress_callback(client_with_mock_stub: Client, mock_stub):
    """Test uploading a file with progress callback."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
        # Write 10MB of data
        data_size = 10 * 1024 * 1024
        f.write(b"X" * data_size)
        temp_file_path = f.name

    try:
        # Mock the response
        mock_response = files_pb2.File(
            id="file-123",
            filename="test.txt",
            size=data_size,
            team_id="team-456",
        )

        # Track progress calls
        progress_calls = []

        def progress_callback(bytes_uploaded: int, total_bytes: int):
            progress_calls.append((bytes_uploaded, total_bytes))

        # Mock the UploadFile to consume the generator
        def consume_chunks(chunks):
            for _ in chunks:
                pass  # Consume all chunks to trigger progress callbacks
            return mock_response

        mock_stub.UploadFile.side_effect = consume_chunks

        # Call upload with progress callback
        result = client_with_mock_stub.files.upload(temp_file_path, on_progress=progress_callback)

        # Verify the stub was called
        assert mock_stub.UploadFile.called

        # Verify the response
        assert result.id == "file-123"

        # Verify progress callbacks were made
        assert len(progress_calls) > 0
        # Verify the last callback has the total bytes
        last_uploaded, last_total = progress_calls[-1]
        assert last_uploaded == data_size
        assert last_total == data_size
    finally:
        os.unlink(temp_file_path)


def test_upload_with_progress_tqdm_like(client_with_mock_stub: Client, mock_stub):
    """Test uploading a file with tqdm-like progress object."""
    data = b"X" * (5 * 1024 * 1024)  # 5MB

    # Mock the response
    mock_response = files_pb2.File(
        id="file-456",
        filename="test.bin",
        size=len(data),
        team_id="team-789",
    )

    # Create a mock tqdm-like object
    class MockProgressBar:
        def __init__(self):
            self.updates = []

        def update(self, n: int):
            self.updates.append(n)

    progress_bar = MockProgressBar()

    # Mock the UploadFile to consume the generator
    def consume_chunks(chunks):
        for _ in chunks:
            pass  # Consume all chunks to trigger progress callbacks
        return mock_response

    mock_stub.UploadFile.side_effect = consume_chunks

    # Call upload with progress bar
    result = client_with_mock_stub.files.upload(data, filename="test.bin", on_progress=progress_bar)

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-456"

    # Verify progress bar updates were made
    assert len(progress_bar.updates) > 0
    # The sum of all updates should equal the total size
    assert sum(progress_bar.updates) == len(data)


def test_list_files(client_with_mock_stub: Client, mock_stub):
    """Test listing files."""
    # Mock the response
    file1 = files_pb2.File(id="file-1", filename="file1.txt", size=100)
    file2 = files_pb2.File(id="file-2", filename="file2.txt", size=200)
    mock_response = files_pb2.ListFilesResponse(
        data=[file1, file2],
        pagination_token="next-page-token",
    )
    mock_stub.ListFiles.return_value = mock_response

    # Call list
    result = client_with_mock_stub.files.list(limit=10, order="desc")

    # Verify the stub was called with correct arguments
    assert mock_stub.ListFiles.called
    call_args = mock_stub.ListFiles.call_args[0][0]
    assert call_args.limit == 10
    assert call_args.order == files_pb2.Ordering.DESCENDING

    # Verify the response
    assert len(result.data) == 2
    assert result.data[0].id == "file-1"
    assert result.data[1].id == "file-2"
    assert result.pagination_token == "next-page-token"


def test_list_files_with_pagination(client_with_mock_stub: Client, mock_stub):
    """Test listing files with pagination token."""
    mock_response = files_pb2.ListFilesResponse(data=[])
    mock_stub.ListFiles.return_value = mock_response

    # Call list with pagination token
    client_with_mock_stub.files.list(pagination_token="previous-token")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.ListFiles.call_args[0][0]
    assert call_args.pagination_token == "previous-token"


def test_list_files_with_sort_by(client_with_mock_stub: Client, mock_stub):
    """Test listing files with sort_by parameter."""
    mock_response = files_pb2.ListFilesResponse(data=[])
    mock_stub.ListFiles.return_value = mock_response

    # Call list with sort_by
    client_with_mock_stub.files.list(sort_by="filename", order="asc")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.ListFiles.call_args[0][0]
    assert call_args.sort_by == files_pb2.FilesSortBy.FILES_SORT_BY_FILENAME
    assert call_args.order == files_pb2.Ordering.ASCENDING


def test_get_file(client_with_mock_stub: Client, mock_stub):
    """Test getting file metadata."""
    # Mock the response
    created_at = timestamp_pb2.Timestamp()
    created_at.GetCurrentTime()

    mock_response = files_pb2.File(
        id="file-123",
        filename="test.txt",
        size=100,
        team_id="team-456",
        created_at=created_at,
    )
    mock_stub.RetrieveFile.return_value = mock_response

    # Call get
    result = client_with_mock_stub.files.get("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.RetrieveFile.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result.id == "file-123"
    assert result.filename == "test.txt"
    assert result.size == 100


def test_delete_file(client_with_mock_stub: Client, mock_stub):
    """Test deleting a file."""
    # Mock the response
    mock_response = files_pb2.DeleteFileResponse(
        id="file-123",
        deleted=True,
    )
    mock_stub.DeleteFile.return_value = mock_response

    # Call delete
    result = client_with_mock_stub.files.delete("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.DeleteFile.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result.id == "file-123"
    assert result.deleted is True


def test_content(client_with_mock_stub: Client, mock_stub):
    """Test getting file content."""
    # Mock the response (streaming)
    chunk1 = files_pb2.FileContentChunk(data=b"Hello ")
    chunk2 = files_pb2.FileContentChunk(data=b"world!")
    mock_stub.RetrieveFileContent.return_value = [chunk1, chunk2]

    # Call content
    result = client_with_mock_stub.files.content("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.RetrieveFileContent.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result == b"Hello world!"


def test_order_conversion():
    """Test order string to protobuf conversion."""
    assert _order_to_pb("asc") == files_pb2.Ordering.ASCENDING
    assert _order_to_pb("desc") == files_pb2.Ordering.DESCENDING
    assert _order_to_pb(None) == files_pb2.Ordering.ASCENDING


def test_sort_by_conversion():
    """Test sort_by string to protobuf conversion."""
    assert _sort_by_to_pb("created_at") == files_pb2.FilesSortBy.FILES_SORT_BY_CREATED_AT
    assert _sort_by_to_pb("filename") == files_pb2.FilesSortBy.FILES_SORT_BY_FILENAME
    assert _sort_by_to_pb("size") == files_pb2.FilesSortBy.FILES_SORT_BY_SIZE
    assert _sort_by_to_pb(None) == files_pb2.FilesSortBy.FILES_SORT_BY_CREATED_AT


def test_chunk_file_data():
    """Test file data chunking."""
    data = b"A" * (2 * 1024 * 1024)  # 2 MiB of data
    filename = "large_file.bin"

    chunks = list(_chunk_file_data(filename, data))

    # First chunk should be the init chunk
    assert chunks[0].HasField("init")
    assert chunks[0].init.name == filename
    assert chunks[0].init.purpose == ""  # Purpose is unused by backend

    # Subsequent chunks should be data chunks
    assert len(chunks) == 2  # 1 init + 1 data chunk (2 MiB fits in one 5 MiB chunk)
    assert chunks[1].HasField("data")

    # Reconstruct data to verify
    reconstructed = b"".join(chunk.data for chunk in chunks[1:])
    assert reconstructed == data


def test_chunk_file_from_path():
    """Test file chunking from path."""
    # Create a temporary file with 12 MiB of data to test multiple chunks
    data = b"B" * (12 * 1024 * 1024)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        f.write(data)
        temp_file_path = f.name

    try:
        chunks = list(_chunk_file_from_path(temp_file_path))

        # First chunk should be the init chunk
        assert chunks[0].HasField("init")
        assert chunks[0].init.name.startswith("tmp")  # basename starts with tmp
        assert chunks[0].init.purpose == ""  # Purpose is unused by backend

        # Subsequent chunks should be data chunks
        assert len(chunks) == 5  # 1 init + 4 data chunks (3 MiB, 3 MiB, 3 MiB, 3 MiB)
        assert chunks[1].HasField("data")
        assert chunks[2].HasField("data")
        assert chunks[3].HasField("data")
        assert chunks[4].HasField("data")

        # Verify chunk sizes
        assert len(chunks[1].data) == 3 * 1024 * 1024  # 3 MiB
        assert len(chunks[2].data) == 3 * 1024 * 1024  # 3 MiB
        assert len(chunks[3].data) == 3 * 1024 * 1024  # 3 MiB
        assert len(chunks[4].data) == 3 * 1024 * 1024  # 3 MiB

        # Reconstruct data to verify
        reconstructed = b"".join(chunk.data for chunk in chunks[1:])
        assert reconstructed == data
    finally:
        os.unlink(temp_file_path)


def test_upload_large_file_uses_chunking(client_with_mock_stub: Client, mock_stub):
    """Test that uploading a large file from path uses streaming chunks."""
    # Create a temporary file with 12 MiB of data to test multiple chunks
    data = b"C" * (12 * 1024 * 1024)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        f.write(data)
        temp_file_path = f.name

    try:
        # Mock the response
        mock_response = files_pb2.File(
            id="file-large",
            filename="large.bin",
            size=len(data),
            team_id="team-456",
        )
        mock_stub.UploadFile.return_value = mock_response

        # Call upload
        result = client_with_mock_stub.files.upload(temp_file_path)

        # Verify the stub was called
        assert mock_stub.UploadFile.called

        # Get the chunks that were passed to UploadFile
        call_args = mock_stub.UploadFile.call_args[0][0]
        chunks = list(call_args)

        # Verify chunking occurred
        assert len(chunks) == 5  # 1 init + 4 data chunks (3 MiB, 3 MiB, 3 MiB, 3 MiB)
        assert chunks[0].HasField("init")

        # Verify the response
        assert result.id == "file-large"
    finally:
        os.unlink(temp_file_path)


def test_batch_upload_success(client_with_mock_stub: Client, mock_stub):
    """Test batch uploading multiple files successfully."""
    # Create temporary files
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses for each file
        mock_stub.UploadFile.side_effect = create_mock_upload_handler()

        # Call batch_upload
        results = client_with_mock_stub.files.batch_upload(temp_files)

        # Verify all files were uploaded
        assert len(results) == 3
        assert all(idx in results for idx in range(3))

        # Verify all uploads succeeded
        for idx, result in results.items():
            assert not isinstance(result, BaseException)
            assert result.id == f"file-{idx}"
            assert result.team_id == "team-456"

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_batch_upload_with_partial_failures(client_with_mock_stub: Client, mock_stub):
    """Test batch upload with some files failing."""
    # Create temporary files
    temp_files = []
    for i in range(5):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock responses - make files at indices 1 and 3 fail
        mock_stub.UploadFile.side_effect = create_mock_upload_handler(fail_on_indices=[1, 3])

        # Call batch_upload
        results = client_with_mock_stub.files.batch_upload(temp_files)

        # Verify all files are in results
        assert len(results) == 5

        # Verify successful uploads (0, 2, 4)
        for idx in [0, 2, 4]:
            result = results[idx]
            assert not isinstance(result, BaseException)
            assert result.id == f"file-{idx}"

        # Verify failed uploads (1, 3)
        for idx in [1, 3]:
            assert isinstance(results[idx], RuntimeError)
            assert f"Upload failed for file {idx}" in str(results[idx])

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_batch_upload_with_callback(client_with_mock_stub: Client, mock_stub):
    """Test batch upload with progress callback."""
    # Create temporary files
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses
        mock_stub.UploadFile.side_effect = create_mock_upload_handler()

        # Track callback invocations
        callback_calls = []

        def on_complete(idx, file, result):
            callback_calls.append((idx, file, result))

        # Call batch_upload with callback
        results = client_with_mock_stub.files.batch_upload(temp_files, on_file_complete=on_complete)

        # Verify all files were uploaded
        assert len(results) == 3

        # Verify callback was called for each file
        assert len(callback_calls) == 3

        # Verify callback arguments
        for idx, file, result in callback_calls:
            assert 0 <= idx < 3
            assert file == temp_files[idx]
            assert not isinstance(result, BaseException)
            assert result.id.startswith("file-")

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_batch_upload_with_callback_and_failures(client_with_mock_stub: Client, mock_stub):
    """Test batch upload callback receives both successes and failures."""
    # Create temporary files
    temp_files = []
    for i in range(4):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock responses - make file at index 2 fail
        mock_stub.UploadFile.side_effect = create_mock_upload_handler(fail_on_indices=[2])

        # Track callback invocations
        success_calls = []
        failure_calls = []

        def on_complete(idx, file, result):
            if isinstance(result, BaseException):
                failure_calls.append((idx, file, result))
            else:
                success_calls.append((idx, file, result))

        # Call batch_upload with callback
        results = client_with_mock_stub.files.batch_upload(temp_files, on_file_complete=on_complete)

        # Verify results
        assert len(results) == 4
        assert len(success_calls) == 3  # Indices 0, 1, 3
        assert len(failure_calls) == 1  # Index 2

        # Verify failure callback
        idx, _file, error = failure_calls[0]
        assert idx == 2
        assert isinstance(error, RuntimeError)
        assert "Upload failed for file 2" in str(error)

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_batch_upload_custom_batch_size(client_with_mock_stub: Client, mock_stub):
    """Test batch upload with custom batch size."""
    # Create temporary files
    temp_files = []
    for i in range(10):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses
        mock_stub.UploadFile.side_effect = create_mock_upload_handler()

        # Call batch_upload with small batch size
        results = client_with_mock_stub.files.batch_upload(temp_files, batch_size=3)

        # Verify all files were uploaded
        assert len(results) == 10
        assert all(not isinstance(result, BaseException) for result in results.values())

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


def test_batch_upload_empty_list(client_with_mock_stub: Client):
    """Test batch upload with empty file list."""
    with pytest.raises(ValueError):
        client_with_mock_stub.files.batch_upload([])
