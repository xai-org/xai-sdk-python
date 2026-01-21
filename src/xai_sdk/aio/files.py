import asyncio
import os
from asyncio import Semaphore
from typing import BinaryIO, Optional, Sequence, Union

from opentelemetry.trace import SpanKind

from ..files import (
    BaseClient,
    BatchUploadCallback,
    Order,
    ProgressCallback,
    SortBy,
    _async_chunk_file_data,
    _async_chunk_file_from_fileobj,
    _async_chunk_file_from_path,
    _order_to_pb,
    _sort_by_to_pb,
)
from ..proto import files_pb2
from ..telemetry import get_tracer
from ..telemetry.config import should_disable_sensitive_attributes

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Asynchronous client for interacting with the `Files` API."""

    async def upload(
        self,
        file: Union[str, bytes, BinaryIO],
        *,
        filename: Optional[str] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> files_pb2.File:
        """Upload a file to xAI's servers asynchronously.

        This method streams the file in chunks to avoid loading large files entirely into memory.

        Args:
            file: The file to upload. Can be:
                - str: Path to a file on disk
                - bytes/bytearray: Raw file content
                - BinaryIO: File-like object opened in binary mode (e.g., io.BytesIO, open(..., "rb"))
            filename: Name for the uploaded file. Required when `file` is bytes or a file-like
                object without a `.name` attribute. If not provided and `file` is a path,
                the basename of the path is used.
            on_progress: Optional progress callback invoked after each chunk is uploaded.
                The callback is called multiple times during upload (approximately every 3 MiB).
                Supported formats:
                - A callable taking (bytes_uploaded: int, total_bytes: int) for custom tracking.
                  Called with cumulative bytes uploaded and total file size.
                - A callable taking (chunk_size: int) for incremental updates.
                  Called with the size of the chunk just uploaded (e.g., tqdm.update).
                - An object with an `update(n: int)` method (e.g., tqdm progress bar).
                  The update method is called with the chunk size after each upload.

        Returns:
            A File proto containing metadata about the uploaded file.

        Raises:
            FileNotFoundError: If `file` is a path that doesn't exist.
            ValueError: If `filename` is required but not provided.
            IOError: If there's an error reading the file.

        Examples:
            >>> # Upload from file path
            >>> await client.files.upload("document.pdf")
            >>>
            >>> # Upload from bytes
            >>> data = b"file content"
            >>> await client.files.upload(data, filename="file.txt")
            >>>
            >>> # Upload from file object
            >>> with open("data.csv", "rb") as f:
            >>>     await client.files.upload(f)
            >>>
            >>> # Upload with progress tracking using tqdm
            >>> from tqdm import tqdm
            >>> import os
            >>> file_path = "large_file.zip"
            >>> total = os.path.getsize(file_path)
            >>> with tqdm(total=total, unit="B", unit_scale=True, desc="Uploading") as pbar:
            >>>     file_obj = await client.files.upload(file_path, on_progress=pbar.update)
            >>>
            >>> # Upload with custom progress callback
            >>> def progress(uploaded, total):
            >>>     print(f"Uploaded {uploaded}/{total} bytes ({100*uploaded/total:.1f}%)")
            >>> await client.files.upload("file.dat", on_progress=progress)
        """
        # Handle str (file path)
        if isinstance(file, str):
            if not os.path.exists(file):
                raise FileNotFoundError(f"File not found: {file}")
            chunks = _async_chunk_file_from_path(file_path=file, progress=on_progress)

        # Handle bytes
        elif isinstance(file, bytes | bytearray):
            if not filename:
                raise ValueError("filename is required when uploading bytes")
            chunks = _async_chunk_file_data(filename=filename, data=bytes(file), progress=on_progress)

        # Handle file-like object (BinaryIO)
        elif hasattr(file, "read"):
            # Try to get filename from the file object if not provided
            if not filename:
                if hasattr(file, "name") and isinstance(file.name, str):
                    filename = os.path.basename(file.name)
                else:
                    raise ValueError("filename is required when uploading a file-like object without a .name attribute")
            chunks = _async_chunk_file_from_fileobj(file_obj=file, filename=filename, progress=on_progress)
        else:
            raise ValueError(f"Unsupported file type: {type(file)}")
        with tracer.start_as_current_span(
            name="file.upload",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "upload_file",
                "provider.name": "xai",
            },
        ) as span:
            res = await self._stub.UploadFile(chunks)
            if not should_disable_sensitive_attributes():
                span.set_attribute("file.id", res.id)
                span.set_attribute("file.filename", res.filename)
            return res

    async def batch_upload(
        self,
        files: Sequence[Union[str, BinaryIO]],
        *,
        batch_size: int = 50,
        on_file_complete: Optional[BatchUploadCallback] = None,
    ) -> dict[int, Union[files_pb2.File, BaseException]]:
        """Batch upload multiple files asynchronously with controlled concurrency.

        This method always handles partial failures gracefully - if some uploads fail, the successful
        uploads will still be returned in the result dictionary alongside the exceptions.

        Args:
            files: List of files to upload. Each can be:
                   - str: Path to a file on disk
                   - BinaryIO: File-like object with a .name attribute (e.g., open(..., "rb"))
                Note: Raw bytes are not supported in batch mode. Use the upload() method
                directly for bytes, or wrap bytes in io.BytesIO with a name attribute.
            batch_size: Maximum number of concurrent uploads. Defaults to 50.
            on_file_complete: Optional callback invoked after each file upload completes (success or failure).
                The callback receives three arguments: (index: int, file: str | BinaryIO, result: File | BaseException).
                Use this to track progress or log individual file results in real-time.

        Returns:
            Dictionary mapping file indices (0-based position in input list) to results.
            Successful uploads map to File protos, failed uploads map to BaseException objects.

        Examples:
            >>> # Upload multiple files from paths
            >>> files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
            >>> results = await client.files.batch_upload(files)
            >>> for idx, result in results.items():
            >>>     if isinstance(result, BaseException):
            >>>         print(f"Failed to upload {files[idx]}: {result}")
            >>>     else:
            >>>         print(f"Uploaded {files[idx]}: {result.file_id}")
            >>>
            >>> # Upload with progress tracking
            >>> completed = 0
            >>> def on_complete(idx, file, result):
            >>>     nonlocal completed
            >>>     completed += 1
            >>>     status = "success" if not isinstance(result, BaseException) else "failure"
            >>>     print(f"[{completed}/{len(files)}] {status}: {file}")
            >>>
            >>> results = await client.files.batch_upload(files, on_file_complete=on_complete)
            >>>
            >>> # Upload file objects
            >>> with open("file1.txt", "rb") as f1, open("file2.txt", "rb") as f2:
            >>>     results = await client.files.batch_upload([f1, f2])
            >>>
            >>> # Get only successful uploads
            >>> results = await client.files.batch_upload(files)
            >>> successful = {idx: f for idx, f in results.items() if not isinstance(f, BaseException)}
            >>> print(f"Uploaded {len(successful)}/{len(files)} files successfully")
            >>>
            >>> # Control concurrency
            >>> results = await client.files.batch_upload(files, batch_size=10)
        """
        if len(files) == 0:
            raise ValueError("files cannot be empty - please provide at least one file to upload")

        semaphore = Semaphore(batch_size)
        results: dict[int, Union[files_pb2.File, BaseException]] = {}

        async def upload_file(file: Union[str, BinaryIO], index: int) -> None:
            try:
                async with semaphore:
                    result = await self.upload(file)
                    results[index] = result
                    if on_file_complete:
                        on_file_complete(index, file, result)
            except BaseException as e:
                results[index] = e
                if on_file_complete:
                    on_file_complete(index, file, e)

        tasks = [upload_file(file, i) for i, file in enumerate(files)]
        await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def list(
        self,
        *,
        limit: Optional[int] = None,
        order: Optional[Order] = None,
        sort_by: Optional[SortBy] = None,
        pagination_token: Optional[str] = None,
    ) -> files_pb2.ListFilesResponse:
        """List files asynchronously.

        Args:
            limit: Maximum number of files to return. If not specified, uses server default of 100.
            order: Sort order for the files. Either "asc" (ascending) or "desc" (descending).
            sort_by: Field to sort by. Either "created_at", "filename", or "size".
            pagination_token: Token for fetching the next page of results.

        Returns:
            A ListFilesResponse containing the list of files and optional pagination token.
        """
        request = files_pb2.ListFilesRequest()

        if limit is not None:
            request.limit = limit
        if order is not None:
            request.order = _order_to_pb(order)
        if sort_by is not None:
            request.sort_by = _sort_by_to_pb(sort_by)
        if pagination_token is not None:
            request.pagination_token = pagination_token

        return await self._stub.ListFiles(request)

    async def get(self, file_id: str) -> files_pb2.File:
        """Get metadata for a specific file asynchronously.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            A File proto containing metadata about the file.
        """
        request = files_pb2.RetrieveFileRequest(file_id=file_id)
        return await self._stub.RetrieveFile(request)

    async def delete(self, file_id: str) -> files_pb2.DeleteFileResponse:
        """Delete a file asynchronously.

        Args:
            file_id: The ID of the file to delete.

        Returns:
            A DeleteFileResponse indicating whether the deletion was successful.
        """
        request = files_pb2.DeleteFileRequest(file_id=file_id)
        with tracer.start_as_current_span(
            name="file.delete",
            kind=SpanKind.CLIENT,
            attributes={
                "operation.name": "delete",
                "provider.name": "xai",
            },
        ) as span:
            res = await self._stub.DeleteFile(request)
            if not should_disable_sensitive_attributes():
                span.set_attribute("file.id", file_id)
            return res

    async def content(self, file_id: str) -> bytes:
        """Get the complete content of a file asynchronously.

        This method handles the streaming download internally and returns the complete
        file content as bytes.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            The complete file content as bytes.
        """
        request = files_pb2.RetrieveFileContentRequest(file_id=file_id)
        chunks = self._stub.RetrieveFileContent(request)

        # Collect all chunks into a single bytes object
        content_parts = []
        async for chunk in chunks:
            content_parts.append(chunk.data)

        return b"".join(content_parts)
