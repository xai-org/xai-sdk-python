import grpc
import pytest
from unittest import mock
from opentelemetry.trace import SpanKind
from google.protobuf.empty_pb2 import Empty

from xai_sdk import Client

from .. import server


@pytest.fixture(scope="session")
def test_client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_get_api_key_info_basic(test_client: Client):
    """Basic test for get_api_key_info."""
    api_key_info = test_client.auth.get_api_key_info()
    assert api_key_info.redacted_api_key == "1**"
    assert api_key_info.name == "api key 0"


def test_get_api_key_info_fields(test_client: Client):
    """Test that get_api_key_info returns all expected fields with correct types."""
    api_key_info = test_client.auth.get_api_key_info()
    
    # Test field existence and basic types
    assert isinstance(api_key_info.redacted_api_key, str)
    assert isinstance(api_key_info.name, str)
    assert hasattr(api_key_info, 'user_id')
    assert hasattr(api_key_info, 'create_time')
    assert hasattr(api_key_info, 'modify_time')
    assert hasattr(api_key_info, 'modified_by')
    assert hasattr(api_key_info, 'team_id')
    assert hasattr(api_key_info, 'acls')
    assert hasattr(api_key_info, 'api_key_id')
    assert isinstance(api_key_info.api_key_blocked, bool)
    assert isinstance(api_key_info.team_blocked, bool)
    assert isinstance(api_key_info.disabled, bool)


def test_invalid_api_key():
    """Test that an invalid API key raises an UNAUTHENTICATED error."""
    with server.run_test_server() as port:
        client = Client(api_key="invalid_key", api_host=f"localhost:{port}")
        with pytest.raises(grpc.RpcError) as exc_info:
            client.auth.get_api_key_info()
        assert exc_info.value.code() == grpc.StatusCode.UNAUTHENTICATED


@mock.patch("xai_sdk.sync.auth.tracer")
def test_span_creation(mock_tracer: mock.MagicMock, test_client: Client):
    """Test that get_api_key_info creates a span with the correct attributes."""
    test_client.auth.get_api_key_info()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_api_key_info",
        kind=SpanKind.CLIENT,
    )


def test_server_error():
    """Test that server errors are properly propagated."""
    with server.run_test_server(initial_failures=1) as port:
        # Disable retries for this test
        client = Client(
            api_key=server.API_KEY, 
            api_host=f"localhost:{port}",
            channel_options=[
                ('grpc.enable_retries', 0),
                ('grpc.service_config', '{"methodConfig": [{}]}')  # Override default retry policy
            ]
        )
        with pytest.raises(grpc.RpcError) as exc_info:
            client.auth.get_api_key_info()
        assert exc_info.value.code() == grpc.StatusCode.UNAVAILABLE


@mock.patch('xai_sdk.sync.auth.tracer')
def test_timeout(mock_tracer):
    """Test that the request times out if the server takes too long to respond."""
    # Create a mock for the gRPC stub
    mock_stub = mock.MagicMock()
    
    # Create a mock RpcError with the DEADLINE_EXCEEDED code
    rpc_error = grpc.RpcError()
    rpc_error.code = lambda: grpc.StatusCode.DEADLINE_EXCEEDED
    rpc_error.details = lambda: "Deadline Exceeded"
    
    # Make the mock raise the RpcError
    mock_stub.get_api_key_info.side_effect = rpc_error
    
    # Create a test client with the mock stub
    client = Client(api_key="test_key", api_host="localhost:12345")
    client.auth._stub = mock_stub
    
    # Test that the method properly handles the timeout
    with pytest.raises(grpc.RpcError) as exc_info:
        client.auth.get_api_key_info()
    
    # Verify the error code is as expected
    assert exc_info.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED
    
    # Verify the span was created
    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_api_key_info",
        kind=SpanKind.CLIENT,
    )
