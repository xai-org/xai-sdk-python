from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client

from .. import server


@pytest.fixture(scope="session")
def test_client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_tokenize(test_client: Client):
    tokens = test_client.tokenize.tokenize_text(model="grok-3", text="Hello, world!")
    assert len(tokens) == 3, f"Expected 3 tokens, got {len(tokens)}: {tokens}"
    assert tokens[0].token_id == 1
    assert tokens[0].string_token == "Hello"
    assert tokens[0].token_bytes == b"test"
    assert tokens[1].token_id == 2
    assert tokens[1].string_token == " world"
    assert tokens[1].token_bytes == b"test"
    assert tokens[2].token_id == 3
    assert tokens[2].string_token == "!"
    assert tokens[2].token_bytes == b"test"


@mock.patch("xai_sdk.sync.tokenizer.tracer")
def test_tokenize_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.tokenize.tokenize_text(model="grok-3", text="Hello, world!")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="tokenize_text grok-3",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-3"},
    )
