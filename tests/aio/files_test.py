"""Unit tests for asynchronous Files API client."""

import io
import os
import tempfile
from unittest import mock

import pytest
import pytest_asyncio
from google.protobuf import timestamp_pb2

from xai_sdk import AsyncClient
from xai_sdk.files import _chunk_file_from_path
from xai_sdk.proto import files_pb2


@pytest.fixture
def mock_stub():
    """Create a mock FilesStub."""
    return mock.MagicMock()


@pytest_asyncio.fixture
async def client_with_mock_stub(mock_stub):
    """Create an async client with a mocked stub."""
    with mock.patch("xai_sdk.files.files_pb2_grpc.FilesStub", return_value=mock_stub):
        client = AsyncClient(api_key="test-api-key")
        yield client
        await client.close()


@pytest.mark.asyncio
async def test_upload_file(client_with_mock_stub: AsyncClient, mock_stub):
    """Test uploading a file from a file path asynchronously."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test content")
        temp_file_path = f.name

    try:
        # Mock the response as a coroutine
        mock_response = files_pb2.File(
            id="file-123",
            filename="test.txt",
            size=12,
            team_id="team-456",
        )

        # Create async mock
        async def async_return():
            return mock_response

        mock_stub.UploadFile.return_value = async_return()

        # Call upload
        result = await client_with_mock_stub.files.upload(temp_file_path)

        # Verify the stub was called
        assert mock_stub.UploadFile.called

        # Verify the response
        assert result.id == "file-123"
        assert result.filename == "test.txt"
        assert result.size == 12
        assert result.team_id == "team-456"
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_upload_file_not_found(client_with_mock_stub: AsyncClient):
    """Test uploading a file that doesn't exist asynchronously."""
    with pytest.raises(FileNotFoundError):
        await client_with_mock_stub.files.upload("/nonexistent/file.txt")


@pytest.mark.asyncio
async def test_upload_bytes(client_with_mock_stub: AsyncClient, mock_stub):
    """Test uploading file from bytes asynchronously."""
    data = b"test content"
    filename = "test.txt"

    # Mock the response
    mock_response = files_pb2.File(
        id="file-123",
        filename=filename,
        size=len(data),
        team_id="team-456",
    )

    async def async_return():
        return mock_response

    mock_stub.UploadFile.return_value = async_return()

    # Call upload with bytes
    result = await client_with_mock_stub.files.upload(data, filename=filename)

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-123"
    assert result.filename == "test.txt"
    assert result.size == len(data)


@pytest.mark.asyncio
async def test_upload_file_object(client_with_mock_stub: AsyncClient, mock_stub):
    """Test uploading a file from a file-like object asynchronously."""
    mock_response = files_pb2.File(
        id="file-789",
        filename="stream.txt",
        size=30,
        team_id="team-abc",
    )

    async def async_return():
        return mock_response

    mock_stub.UploadFile.return_value = async_return()

    # Create a file-like object
    file_obj = io.BytesIO(b"Data from file object")

    # Call upload with file object
    result = await client_with_mock_stub.files.upload(file_obj, filename="stream.txt")

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-789"
    assert result.filename == "stream.txt"
    assert result.size == 30


@pytest.mark.asyncio
async def test_upload_with_progress_callback(client_with_mock_stub: AsyncClient, mock_stub):
    """Test uploading a file with progress callback asynchronously."""
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

        # Mock the UploadFile to consume the async generator
        async def consume_chunks(chunks):
            async for _ in chunks:
                pass  # Consume all chunks to trigger progress callbacks
            return mock_response

        mock_stub.UploadFile.side_effect = consume_chunks

        # Call upload with progress callback
        result = await client_with_mock_stub.files.upload(temp_file_path, on_progress=progress_callback)

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


@pytest.mark.asyncio
async def test_upload_with_progress_tqdm_like(client_with_mock_stub: AsyncClient, mock_stub):
    """Test uploading a file with tqdm-like progress object asynchronously."""
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

    # Mock the UploadFile to consume the async generator
    async def consume_chunks(chunks):
        async for _ in chunks:
            pass  # Consume all chunks to trigger progress callbacks
        return mock_response

    mock_stub.UploadFile.side_effect = consume_chunks

    # Call upload with progress bar
    result = await client_with_mock_stub.files.upload(data, filename="test.bin", on_progress=progress_bar)

    # Verify the stub was called
    assert mock_stub.UploadFile.called

    # Verify the response
    assert result.id == "file-456"

    # Verify progress bar updates were made
    assert len(progress_bar.updates) > 0
    # The sum of all updates should equal the total size
    assert sum(progress_bar.updates) == len(data)


@pytest.mark.asyncio
async def test_list_files(client_with_mock_stub: AsyncClient, mock_stub):
    """Test listing files asynchronously."""
    # Mock the response
    file1 = files_pb2.File(id="file-1", filename="file1.txt", size=100)
    file2 = files_pb2.File(id="file-2", filename="file2.txt", size=200)
    mock_response = files_pb2.ListFilesResponse(
        data=[file1, file2],
        pagination_token="next-page-token",
    )

    async def async_return():
        return mock_response

    mock_stub.ListFiles.return_value = async_return()

    # Call list
    result = await client_with_mock_stub.files.list(limit=10, order="desc")

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


@pytest.mark.asyncio
async def test_list_files_with_pagination(client_with_mock_stub: AsyncClient, mock_stub):
    """Test listing files with pagination token asynchronously."""
    mock_response = files_pb2.ListFilesResponse(data=[])

    async def async_return():
        return mock_response

    mock_stub.ListFiles.return_value = async_return()

    # Call list with pagination token
    await client_with_mock_stub.files.list(pagination_token="previous-token")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.ListFiles.call_args[0][0]
    assert call_args.pagination_token == "previous-token"


@pytest.mark.asyncio
async def test_list_files_with_sort_by(client_with_mock_stub: AsyncClient, mock_stub):
    """Test listing files with sort_by parameter asynchronously."""
    mock_response = files_pb2.ListFilesResponse(data=[])

    async def async_return():
        return mock_response

    mock_stub.ListFiles.return_value = async_return()

    # Call list with sort_by
    await client_with_mock_stub.files.list(sort_by="size", order="desc")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.ListFiles.call_args[0][0]
    assert call_args.sort_by == files_pb2.FilesSortBy.FILES_SORT_BY_SIZE
    assert call_args.order == files_pb2.Ordering.DESCENDING


@pytest.mark.asyncio
async def test_get_file(client_with_mock_stub: AsyncClient, mock_stub):
    """Test getting file metadata asynchronously."""
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

    async def async_return():
        return mock_response

    mock_stub.RetrieveFile.return_value = async_return()

    # Call get
    result = await client_with_mock_stub.files.get("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.RetrieveFile.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result.id == "file-123"
    assert result.filename == "test.txt"
    assert result.size == 100


@pytest.mark.asyncio
async def test_delete_file(client_with_mock_stub: AsyncClient, mock_stub):
    """Test deleting a file asynchronously."""
    # Mock the response
    mock_response = files_pb2.DeleteFileResponse(
        id="file-123",
        deleted=True,
    )

    async def async_return():
        return mock_response

    mock_stub.DeleteFile.return_value = async_return()

    # Call delete
    result = await client_with_mock_stub.files.delete("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.DeleteFile.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result.id == "file-123"
    assert result.deleted is True


@pytest.mark.asyncio
async def test_content(client_with_mock_stub: AsyncClient, mock_stub):
    """Test getting file content asynchronously."""

    # Create an async generator for the mock
    async def async_gen():
        yield files_pb2.FileContentChunk(data=b"Hello ")
        yield files_pb2.FileContentChunk(data=b"world!")

    mock_stub.RetrieveFileContent.return_value = async_gen()

    # Call content
    result = await client_with_mock_stub.files.content("file-123")

    # Verify the stub was called with correct arguments
    call_args = mock_stub.RetrieveFileContent.call_args[0][0]
    assert call_args.file_id == "file-123"

    # Verify the response
    assert result == b"Hello world!"


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


@pytest.mark.asyncio
async def test_upload_large_file_uses_chunking(client_with_mock_stub: AsyncClient, mock_stub):
    """Test that uploading a large file from path uses streaming chunks asynchronously."""
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

        # Track chunks and return response
        captured_chunks = []

        async def consume_and_capture_chunks(chunks):
            async for chunk in chunks:
                captured_chunks.append(chunk)
            return mock_response

        mock_stub.UploadFile.side_effect = consume_and_capture_chunks

        # Call upload
        result = await client_with_mock_stub.files.upload(temp_file_path)

        # Verify the stub was called
        assert mock_stub.UploadFile.called

        # Verify chunking occurred
        assert len(captured_chunks) == 5  # 1 init + 4 data chunks (3 MiB, 3 MiB, 3 MiB, 3 MiB)
        assert captured_chunks[0].HasField("init")

        # Verify the response
        assert result.id == "file-large"
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_batch_upload_success(client_with_mock_stub: AsyncClient, mock_stub):
    """Test batch uploading multiple files successfully."""
    # Create temporary files
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses for each file
        call_count = 0

        async def mock_upload(chunks):
            nonlocal call_count
            file_id = f"file-{call_count}"
            call_count += 1
            async for _ in chunks:
                pass  # Consume chunks
            return files_pb2.File(
                id=file_id,
                filename=f"batch_{call_count - 1}.txt",
                size=100,
                team_id="team-456",
            )

        mock_stub.UploadFile.side_effect = mock_upload

        # Call batch_upload
        results = await client_with_mock_stub.files.batch_upload(temp_files)

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


@pytest.mark.asyncio
async def test_batch_upload_with_partial_failures(client_with_mock_stub: AsyncClient, mock_stub):
    """Test batch upload with some files failing."""
    # Create temporary files
    temp_files = []
    for i in range(5):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock responses - make files at indices 1 and 3 fail
        call_count = 0

        async def mock_upload(chunks):
            nonlocal call_count
            idx = call_count
            call_count += 1
            async for _ in chunks:
                pass  # Consume chunks

            if idx in [1, 3]:
                raise RuntimeError(f"Upload failed for file {idx}")

            return files_pb2.File(
                id=f"file-{idx}",
                filename=f"batch_{idx}.txt",
                size=100,
                team_id="team-456",
            )

        mock_stub.UploadFile.side_effect = mock_upload

        # Call batch_upload
        results = await client_with_mock_stub.files.batch_upload(temp_files)

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


@pytest.mark.asyncio
async def test_batch_upload_with_callback(client_with_mock_stub: AsyncClient, mock_stub):
    """Test batch upload with progress callback."""
    # Create temporary files
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses
        call_count = 0

        async def mock_upload(chunks):
            nonlocal call_count
            file_id = f"file-{call_count}"
            call_count += 1
            async for _ in chunks:
                pass
            return files_pb2.File(
                id=file_id,
                filename=f"batch_{call_count - 1}.txt",
                size=100,
                team_id="team-456",
            )

        mock_stub.UploadFile.side_effect = mock_upload

        # Track callback invocations
        callback_calls = []

        def on_complete(idx, file, result):
            callback_calls.append((idx, file, result))

        # Call batch_upload with callback
        results = await client_with_mock_stub.files.batch_upload(temp_files, on_file_complete=on_complete)

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


@pytest.mark.asyncio
async def test_batch_upload_with_callback_and_failures(client_with_mock_stub: AsyncClient, mock_stub):
    """Test batch upload callback receives both successes and failures."""
    # Create temporary files
    temp_files = []
    for i in range(4):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock responses - make file at index 2 fail
        call_count = 0

        async def mock_upload(chunks):
            nonlocal call_count
            idx = call_count
            call_count += 1
            async for _ in chunks:
                pass

            if idx == 2:
                raise ValueError(f"Failed file {idx}")

            return files_pb2.File(
                id=f"file-{idx}",
                filename=f"batch_{idx}.txt",
                size=100,
                team_id="team-456",
            )

        mock_stub.UploadFile.side_effect = mock_upload

        # Track callback invocations
        success_calls = []
        failure_calls = []

        def on_complete(idx, file, result):
            if isinstance(result, BaseException):
                failure_calls.append((idx, file, result))
            else:
                success_calls.append((idx, file, result))

        # Call batch_upload with callback
        results = await client_with_mock_stub.files.batch_upload(temp_files, on_file_complete=on_complete)

        # Verify results
        assert len(results) == 4
        assert len(success_calls) == 3  # Indices 0, 1, 3
        assert len(failure_calls) == 1  # Index 2

        # Verify failure callback
        idx, _file, error = failure_calls[0]
        assert idx == 2
        assert isinstance(error, ValueError)
        assert "Failed file 2" in str(error)

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_batch_upload_custom_batch_size(client_with_mock_stub: AsyncClient, mock_stub):
    """Test batch upload with custom batch size."""
    # Create temporary files
    temp_files = []
    for i in range(10):
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
            f.write(f"content {i}")
            temp_files.append(f.name)

    try:
        # Mock successful responses
        call_count = 0

        async def mock_upload(chunks):
            nonlocal call_count
            file_id = f"file-{call_count}"
            call_count += 1
            async for _ in chunks:
                pass
            return files_pb2.File(
                id=file_id,
                filename=f"batch_{call_count - 1}.txt",
                size=100,
                team_id="team-456",
            )

        mock_stub.UploadFile.side_effect = mock_upload

        # Call batch_upload with small batch size
        results = await client_with_mock_stub.files.batch_upload(temp_files, batch_size=3)

        # Verify all files were uploaded
        assert len(results) == 10
        assert all(not isinstance(result, BaseException) for result in results.values())

    finally:
        for temp_file in temp_files:
            os.unlink(temp_file)


@pytest.mark.asyncio
async def test_batch_upload_empty_list(client_with_mock_stub: AsyncClient):
    """Test batch upload with empty file list."""
    with pytest.raises(ValueError):
        await client_with_mock_stub.files.batch_upload([])
