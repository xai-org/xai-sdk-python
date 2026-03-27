from typing import Any, cast

import pytest

from xai_sdk.chat import file


def test_file_content_by_id():
    content = file("file_123")
    assert content.WhichOneof("content") == "file"
    assert content.file.file_id == "file_123"


def test_file_content_inline_bytes():
    content = file(data=b"hello", filename="hello.txt", mime_type="text/plain")
    assert content.WhichOneof("content") == "file"
    assert content.file.data == b"hello"
    assert content.file.filename == "hello.txt"
    assert content.file.mime_type == "text/plain"


def test_file_content_inline_bytes_filename_optional():
    content = file(data=b"hello")
    assert content.WhichOneof("content") == "file"
    assert content.file.data == b"hello"


def test_file_content_url():
    content = file(url="https://example.com/report.pdf")
    assert content.WhichOneof("content") == "file"
    assert content.file.url == "https://example.com/report.pdf"


def test_file_content_url_with_filename_and_mime_type():
    content = file(url="https://example.com/report.pdf", filename="report.pdf", mime_type="application/pdf")
    assert content.WhichOneof("content") == "file"
    assert content.file.url == "https://example.com/report.pdf"
    assert content.file.filename == "report.pdf"
    assert content.file.mime_type == "application/pdf"


def test_file_content_validation():
    file_any = cast(Any, file)
    # No arguments
    with pytest.raises(ValueError):
        file_any()
    # file_id + data
    with pytest.raises(ValueError):
        file_any("file_123", data=b"hello")
    # file_id + filename (not supported for file_id mode)
    with pytest.raises(ValueError):
        file_any("file_123", filename="hello.txt")
    # file_id + url
    with pytest.raises(ValueError):
        file_any("file_123", url="https://example.com/file.pdf")
    # data + url
    with pytest.raises(ValueError):
        file_any(data=b"hello", url="https://example.com/file.pdf")
    # all three
    with pytest.raises(ValueError):
        file_any("file_123", data=b"hello", url="https://example.com/file.pdf")
