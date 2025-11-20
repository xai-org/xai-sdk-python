"""Example demonstrating synchronous Files API usage."""

import io
import os
import tempfile

from tqdm import tqdm

import xai_sdk


def upload_example(client: xai_sdk.Client):
    """Demonstrate file upload."""
    print("\n=== Upload Example ===")

    # Create a temporary file to upload
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test file for the Files API.\n")
        f.write("It demonstrates uploading files to the xAI platform.\n")
        temp_file_path = f.name

    try:
        # Upload the file
        file = client.files.upload(temp_file_path)
        print(f"Uploaded file: {file.filename}")
        print(f"File ID: {file.id}")
        print(f"File size: {file.size} bytes")
        print(f"Team ID: {file.team_id}")
        print(f"Created at: {file.created_at.ToDatetime()}")
        return file.id
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


def upload_bytes_example(client: xai_sdk.Client):
    """Demonstrate file upload from bytes."""
    print("\n=== Upload Bytes Example ===")

    data = b"This is file content uploaded directly from bytes."

    file = client.files.upload(data, filename="bytes_upload_example.txt")
    print(f"Uploaded file: {file.filename}")
    print(f"File ID: {file.id}")
    print(f"File size: {file.size} bytes")
    return file.id


def upload_file_object_example(client: xai_sdk.Client):
    """Demonstrate file upload from a file-like object (BinaryIO)."""
    print("\n=== Upload File Object Example ===")

    # Example 1: Upload from BytesIO
    data = b"Content from BytesIO object.\nThis demonstrates uploading from memory."
    file_obj = io.BytesIO(data)

    file = client.files.upload(file_obj, filename="bytesio_example.txt")
    print(f"Uploaded from BytesIO: {file.filename}")
    print(f"File ID: {file.id}")
    print(f"File size: {file.size} bytes")

    # Example 2: Upload from opened file (filename auto-detected from file.name)
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".dat", delete=False) as f:
        f.write(b"Data written to temp file for upload via file object.")
        temp_path = f.name

    try:
        with open(temp_path, "rb") as f:
            # filename is automatically detected from f.name
            file2 = client.files.upload(f)
            print(f"Uploaded from file object: {file2.filename}")
            print(f"File ID: {file2.id}")
            print(f"File size: {file2.size} bytes")
    finally:
        os.unlink(temp_path)

    return file.id


def upload_large_file_example(client: xai_sdk.Client):
    """Demonstrate uploading a large file (48MB) using streaming chunks."""
    print("\n=== Upload Large File Example (48MB) ===")

    # Create a temporary 48MB file
    file_size = 48 * 1024 * 1024  # 48 MB
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        write_chunk_size = 1024 * 1024  # 1 MB write chunks
        for _ in range(file_size // write_chunk_size):
            f.write(b"X" * write_chunk_size)
        temp_file_path = f.name

    try:
        print(f"Created temporary 48MB file: {temp_file_path}")
        print("Uploading file...")

        # Upload the file - the SDK will automatically stream it in chunks
        file = client.files.upload(temp_file_path)

        print(f"Successfully uploaded file: {file.filename}")
        print(f"File ID: {file.id}")
        print(f"File size: {file.size} bytes ({file.size / (1024 * 1024):.2f} MB)")
        print(f"Team ID: {file.team_id}")
        print(f"Created at: {file.created_at.ToDatetime()}")
        return file.id
    finally:
        # Clean up temporary file
        print("Cleaning up temporary file...")
        os.unlink(temp_file_path)


def upload_with_progress_tqdm_example(client: xai_sdk.Client):
    """Demonstrate uploading a file with tqdm progress bar."""
    print("\n=== Upload with tqdm Progress Bar Example ===")

    # Create a temporary 10MB file
    file_size = 10 * 1024 * 1024  # 10 MB
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        write_chunk_size = 1024 * 1024  # 1 MB write chunks
        for _ in range(file_size // write_chunk_size):
            f.write(b"X" * write_chunk_size)
        temp_file_path = f.name

    try:
        total_bytes = os.path.getsize(temp_file_path)
        print(f"Uploading {total_bytes / (1024 * 1024):.2f} MB file with progress bar...")

        # Upload with tqdm progress bar
        with tqdm(total=total_bytes, unit="B", unit_scale=True, desc="Uploading") as pbar:
            file = client.files.upload(
                temp_file_path,
                on_progress=pbar.update,  # type: ignore[arg-type]
            )

        print(f"\nSuccessfully uploaded file: {file.filename}")
        print(f"File ID: {file.id}")
        return file.id
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


def upload_with_progress_callback_example(client: xai_sdk.Client):
    """Demonstrate uploading a file with custom progress callback."""
    print("\n=== Upload with Custom Progress Callback Example ===")

    # Create a temporary 5MB file
    file_size = 5 * 1024 * 1024  # 5 MB
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        write_chunk_size = 1024 * 1024  # 1 MB write chunks
        for _ in range(file_size // write_chunk_size):
            f.write(b"X" * write_chunk_size)
        temp_file_path = f.name

    try:
        # Define a custom progress callback
        def progress_callback(bytes_uploaded: int, total_bytes: int):
            percentage = (bytes_uploaded / total_bytes) * 100 if total_bytes else 0
            mb_uploaded = bytes_uploaded / (1024 * 1024)
            mb_total = total_bytes / (1024 * 1024)
            print(f"Progress: {mb_uploaded:.2f}/{mb_total:.2f} MB ({percentage:.1f}%)")

        print(f"Uploading {file_size / (1024 * 1024):.2f} MB file with custom callback...")

        # Upload with custom progress callback
        file = client.files.upload(
            temp_file_path,
            on_progress=progress_callback,
        )

        print(f"Successfully uploaded file: {file.filename}")
        print(f"File ID: {file.id}")
        return file.id
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


def batch_upload_example(client: xai_sdk.Client):
    """Demonstrate batch uploading multiple files using threads."""
    print("\n=== Batch Upload Example ===")

    # Create multiple temporary files to upload
    temp_files = []
    num_files = 20

    try:
        for i in range(num_files):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_batch_{i}.txt", delete=False) as f:
                f.write(f"This is test file #{i + 1} for batch upload.\n")
                f.write("Demonstrating concurrent file uploads.\n")
                temp_files.append(f.name)

        print(f"Created {num_files} temporary files")
        print("Uploading files in batch with progress tracking...\n")

        # Track progress with callback
        completed_count = 0
        success_count = 0
        failed_count = 0

        def on_file_complete(_idx, file, result):
            nonlocal completed_count, success_count, failed_count
            completed_count += 1
            if isinstance(result, BaseException):
                failed_count += 1
                print(f"[{completed_count}/{num_files}] Failed: {os.path.basename(file)} - {result}")
            else:
                success_count += 1
                print(f"[{completed_count}/{num_files}] Success: {result.filename} ({result.size} bytes)")

        # Batch upload all files with controlled concurrency and progress callback
        results = client.files.batch_upload(temp_files, batch_size=3, on_file_complete=on_file_complete)

        print("\nBatch upload complete!")
        print(f"  Total: {len(results)} files")
        print(f"  Success: {success_count}")
        print(f"  Failed: {failed_count}")

        return [result.id for result in results.values() if not isinstance(result, BaseException)]

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            os.unlink(temp_file)


def list_example(client: xai_sdk.Client):
    """Demonstrate listing files."""
    print("\n=== List Example ===")

    # List first 10 files sorted by creation date in descending order
    response = client.files.list(limit=10, order="desc", sort_by="created_at")

    print(f"Found {len(response.data)} files (sorted by creation date, newest first):")
    for file in response.data:
        print(f"  - {file.filename} (ID: {file.id}, Size: {file.size} bytes)")

    if response.pagination_token:
        print(f"Pagination token available: {response.pagination_token}")

    # Example: List files sorted by filename in ascending order
    print("\nListing files sorted by filename:")
    response = client.files.list(limit=5, order="asc", sort_by="filename")
    for file in response.data:
        print(f"  - {file.filename}")


def get_example(client: xai_sdk.Client, file_id: str):
    """Demonstrate getting file metadata."""
    print("\n=== Get File Metadata Example ===")

    file = client.files.get(file_id)
    print(f"Retrieved file: {file.filename}")
    print(f"File ID: {file.id}")
    print(f"File size: {file.size} bytes")
    print(f"Created at: {file.created_at.ToDatetime()}")
    if file.HasField("expires_at"):
        print(f"Expires at: {file.expires_at.ToDatetime()}")


def get_content_example(client: xai_sdk.Client, file_id: str):
    """Demonstrate getting file content and writing it to a file."""
    print("\n=== Get File Content Example ===")

    # Download the file content
    content = client.files.content(file_id)
    print(f"Retrieved {len(content)} bytes of content")

    # Write the content to a temporary file
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
        f.write(content)
        downloaded_path = f.name

    try:
        print(f"Content written to: {downloaded_path}")

        # If it's text content, print a preview
        preview_length = 200
        try:
            text_content = content.decode("utf-8")
            preview = text_content[:preview_length]
            if len(text_content) > preview_length:
                preview += "..."
            print(f"Content preview: {preview}")
        except UnicodeDecodeError:
            print("(Binary content, cannot display as text)")
    finally:
        # Clean up the downloaded file
        os.unlink(downloaded_path)


def delete_example(client: xai_sdk.Client, file_id: str):
    """Demonstrate deleting a file."""
    print("\n=== Delete Example ===")

    response = client.files.delete(file_id)
    print(f"Deleted file ID: {response.id}")
    print(f"Deletion successful: {response.deleted}")


def main() -> None:
    """Run all files API examples."""
    client = xai_sdk.Client()

    # Upload a file and get its ID
    file_id = upload_example(client)

    # Upload from bytes
    file_id_2 = upload_bytes_example(client)

    # Upload from file-like object
    file_id_3 = upload_file_object_example(client)

    # Upload with tqdm progress bar
    file_id_4 = upload_with_progress_tqdm_example(client)

    # Upload with custom progress callback
    file_id_5 = upload_with_progress_callback_example(client)

    # Batch upload example
    batch_file_ids = batch_upload_example(client)

    # Upload a large file (48MB) - uncomment to test
    # Note: This will upload a 48MB file, which may take time depending on your connection
    # file_id_large = upload_large_file_example(client)

    # List files
    list_example(client)

    # Get file metadata
    get_example(client, file_id)

    # Get file content
    get_content_example(client, file_id)

    # Delete files (cleanup)
    delete_example(client, file_id)
    delete_example(client, file_id_2)
    delete_example(client, file_id_3)
    delete_example(client, file_id_4)
    delete_example(client, file_id_5)

    # Delete batch uploaded files
    for file_id in batch_file_ids:
        delete_example(client, file_id)

    # Uncomment if you ran the large file upload
    # delete_example(client, file_id_large)

    print("\n=== All examples completed successfully! ===")


if __name__ == "__main__":
    main()
