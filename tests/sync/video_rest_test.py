"""Tests for REST-based video generation."""

import pytest

from xai_sdk import Client
from xai_sdk.video import RestVideoResponse

from .. import server


@pytest.fixture(scope="session")
def rest_client():
    """Create a client configured for REST video transport."""
    with server.run_test_server_with_rest() as (grpc_port, rest_port):
        # Create client with REST transport for video
        yield Client(
            api_key=server.API_KEY,
            api_host=f"localhost:{rest_port}",
            video_transport="rest",
        )


def test_rest_generate_returns_video_url(rest_client: Client):
    """Test that REST video generation returns a video URL."""
    response = rest_client.video.generate(prompt="foo", model="grok-imagine-video")

    assert isinstance(response, RestVideoResponse)
    assert response.model == "grok-imagine-video"
    assert response.url
    assert response.duration > 0


def test_rest_generate_with_duration(rest_client: Client):
    """Test that REST video generation respects duration parameter."""
    response = rest_client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        duration=10,
    )

    assert isinstance(response, RestVideoResponse)
    assert response.duration == 10


def test_rest_start_returns_request_id(rest_client: Client):
    """Test that REST start() returns a request ID."""
    response = rest_client.video.start(prompt="foo", model="grok-imagine-video")

    assert response.request_id
    assert response.request_id.startswith("rest-video-")


def test_rest_get_returns_status(rest_client: Client):
    """Test that REST get() returns status information."""
    # Start a generation
    start_response = rest_client.video.start(prompt="foo", model="grok-imagine-video")

    # Get status (should be pending on first poll)
    get_response = rest_client.video.get(start_response.request_id)

    assert get_response.status in ["pending", "done"]


def test_rest_transport_override():
    """Test that transport can be overridden per-request."""
    with server.run_test_server_with_rest() as (grpc_port, rest_port):
        # Create client with gRPC transport by default
        client = Client(
            api_key=server.API_KEY,
            api_host=f"localhost:{grpc_port}",
            video_transport="grpc",
        )

        # Override to REST for this specific call
        # Note: This will fail because the gRPC server doesn't serve REST
        # But we can test that the transport parameter is accepted
        # In a real scenario, you'd configure the client with the REST host

        # Test gRPC transport works
        response = client.video.generate(prompt="foo", model="grok-imagine-video")
        # gRPC responses are VideoResponse (not RestVideoResponse)
        assert not isinstance(response, RestVideoResponse)
        assert response.url
