import grpc
import pytest

from xai_sdk import Client
from xai_sdk.chat import user

from .. import server


@pytest.fixture
def test_server_port():
    with server.run_test_server() as port:
        yield port


def test_client(test_server_port):
    client = Client(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")

    api_key = client.auth.get_api_key_info()
    assert api_key.redacted_api_key == "1**"


def test_client_wrong_api_key(test_server_port):
    client = Client(api_key=server.API_KEY + "bad", api_host=f"localhost:{test_server_port}")

    with pytest.raises(grpc.RpcError):
        client.auth.get_api_key_info()


def test_retries():
    with server.run_test_server(initial_failures=1) as port:
        client = Client(
            api_key=server.API_KEY,
            api_host=f"localhost:{port}",
            channel_options=[
                ("grpc.enable_retries", 0),
            ],
        )

        with pytest.raises(grpc.RpcError):
            client.auth.get_api_key_info()

    with server.run_test_server(initial_failures=1) as port:
        client = Client(api_key=server.API_KEY, api_host=f"localhost:{port}")

        api_key = client.auth.get_api_key_info()
        assert api_key.redacted_api_key == "1**"


def test_timeout_unary_unary():
    with server.run_test_server(response_delay_seconds=2) as port:
        client = Client(api_key=server.API_KEY, api_host=f"localhost:{port}", timeout=1)

        with pytest.raises(grpc.RpcError) as excinfo:
            chat = client.chat.create(model="grok-3")
            chat.append(user("Hello, world!"))
            chat.sample()

        assert excinfo.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED  # type: ignore


def test_timeout_unary_stream():
    with server.run_test_server(response_delay_seconds=2) as port:
        client = Client(api_key=server.API_KEY, api_host=f"localhost:{port}", timeout=1)

        with pytest.raises(grpc.RpcError) as excinfo:
            chat = client.chat.create(model="grok-3")
            chat.append(user("Hello, world!"))
            for _, _ in chat.stream():
                pass

        assert excinfo.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED  # type: ignore
