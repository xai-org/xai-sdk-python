from unittest import mock

import pytest
import pytest_asyncio
from opentelemetry.trace import SpanKind

from xai_sdk import AsyncClient

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
async def test_get_api_key_info(test_client: AsyncClient):
    api_key_info = await test_client.auth.get_api_key_info()
    assert api_key_info.redacted_api_key == "1**"
    assert api_key_info.name == "api key 0"


@mock.patch("xai_sdk.aio.auth.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_get_api_key_info_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.auth.get_api_key_info()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_api_key_info",
        kind=SpanKind.CLIENT,
    )
