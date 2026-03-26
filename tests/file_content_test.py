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


def test_file_content_validation():
    file_any = cast(Any, file)
    with pytest.raises(ValueError):
        file_any()
    with pytest.raises(ValueError):
        file_any("file_123", data=b"hello")
    with pytest.raises(ValueError):
        file_any("file_123", filename="hello.txt")
