import pytest
import pytest_asyncio

from xai_sdk import AsyncClient
from xai_sdk.proto import tokenize_pb2

from .. import server


@pytest.fixture(scope="session")
def test_server_port():
    with server.run_test_server() as port:
        yield port


@pytest_asyncio.fixture(scope="session")
async def test_client(test_server_port: int):
    client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")
    yield client


@pytest.mark.asyncio(loop_scope="session")
async def test_tokenize(test_client: AsyncClient):
    tokens = await test_client.tokenize.tokenize_text(model="grok-3", text="Hello, world!")
    assert tokens == [
        tokenize_pb2.Token(token_id=1, string_token="Hello", token_bytes=b"test"),
        tokenize_pb2.Token(token_id=2, string_token=" world", token_bytes=b"test"),
        tokenize_pb2.Token(token_id=3, string_token="!", token_bytes=b"test"),
    ]
