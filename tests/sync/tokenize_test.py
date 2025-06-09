import pytest

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
