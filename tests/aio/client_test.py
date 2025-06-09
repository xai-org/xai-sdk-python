import grpc
import pytest

from xai_sdk import AsyncClient
from xai_sdk.chat import user

from .. import server


@pytest.fixture(scope="session")
def test_server_port():
    with server.run_test_server() as port:
        yield port


@pytest.mark.asyncio(loop_scope="session")
async def test_client(test_server_port):
    client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")

    api_key = await client.auth.get_api_key_info()
    assert api_key.redacted_api_key == "1**"


@pytest.mark.asyncio(loop_scope="session")
async def test_client_wrong_api_key(test_server_port):
    client = AsyncClient(api_key=server.API_KEY + "bad", api_host=f"localhost:{test_server_port}")

    with pytest.raises(grpc.RpcError):
        await client.auth.get_api_key_info()


@pytest.mark.asyncio(loop_scope="session")
async def test_retries():
    with server.run_test_server(initial_failures=1) as port:
        client = AsyncClient(
            api_key=server.API_KEY,
            api_host=f"localhost:{port}",
            channel_options=[
                ("grpc.enable_retries", 0),
            ],
        )

        with pytest.raises(grpc.RpcError):
            await client.auth.get_api_key_info()

    with server.run_test_server(initial_failures=1) as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")

        api_key = await client.auth.get_api_key_info()
        assert api_key.redacted_api_key == "1**"


@pytest.mark.asyncio(loop_scope="session")
async def test_timeout_unary_unary():
    with server.run_test_server(response_delay_seconds=2) as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}", timeout=1)

        with pytest.raises(grpc.aio.AioRpcError) as exc:
            chat = client.chat.create(model="grok-3")
            chat.append(user("Hello, world!"))
            await chat.sample()

        assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED


@pytest.mark.asyncio(loop_scope="session")
async def test_timeout_unary_stream():
    with server.run_test_server(response_delay_seconds=2) as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}", timeout=1)

        with pytest.raises(grpc.aio.AioRpcError) as exc:
            chat = client.chat.create(model="grok-3")
            chat.append(user("Hello, world!"))
            async for _, _ in chat.stream():
                pass

        assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
