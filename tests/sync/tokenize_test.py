from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client
from xai_sdk.proto import tokenize_pb2

from .. import server


@pytest.fixture(scope="session")
def test_client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_tokenize(test_client: Client):
    tokens = test_client.tokenize.tokenize_text(model="grok-3", text="Hello, world!")
    assert tokens == [
        tokenize_pb2.Token(token_id=1, string_token="Hello", token_bytes=b"test"),
        tokenize_pb2.Token(token_id=2, string_token=" world", token_bytes=b"test"),
        tokenize_pb2.Token(token_id=3, string_token="!", token_bytes=b"test"),
    ]


@mock.patch("xai_sdk.sync.tokenizer.tracer")
def test_tokenize_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.tokenize.tokenize_text(model="grok-3", text="Hello, world!")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="tokenize_text grok-3",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-3"},
    )
