from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client

from .. import server


@pytest.fixture(scope="session")
def test_client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_get_api_key_info(test_client: Client):
    api_key_info = test_client.auth.get_api_key_info()
    assert api_key_info.redacted_api_key == "1**"
    assert api_key_info.name == "api key 0"


@mock.patch("xai_sdk.sync.auth.tracer")
def test_get_api_key_info_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.auth.get_api_key_info()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_api_key_info",
        kind=SpanKind.CLIENT,
    )
