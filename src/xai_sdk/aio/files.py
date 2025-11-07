import os
from typing import BinaryIO, Optional, Union

from ..files import (
    BaseClient,
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
            return await self._stub.UploadFile(chunks)

        # Handle bytes
        if isinstance(file, bytes | bytearray):
            if not filename:
                raise ValueError("filename is required when uploading bytes")
            chunks = _async_chunk_file_data(filename=filename, data=bytes(file), progress=on_progress)
            return await self._stub.UploadFile(chunks)

        # Handle file-like object (BinaryIO)
        if hasattr(file, "read"):
            # Try to get filename from the file object if not provided
            if not filename:
                if hasattr(file, "name") and isinstance(file.name, str):
                    filename = os.path.basename(file.name)
                else:
                    raise ValueError("filename is required when uploading a file-like object without a .name attribute")
            chunks = _async_chunk_file_from_fileobj(file_obj=file, filename=filename, progress=on_progress)
            return await self._stub.UploadFile(chunks)

        raise ValueError(f"Unsupported file type: {type(file)}")

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
        return await self._stub.DeleteFile(request)

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
