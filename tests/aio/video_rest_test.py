"""Tests for async REST-based video generation."""

import pytest
import pytest_asyncio

from xai_sdk import AsyncClient
from xai_sdk.video import RestVideoResponse

from .. import server


@pytest_asyncio.fixture(scope="session")
async def rest_client():
    """Create an async client configured for REST video transport."""
    with server.run_test_server_with_rest() as (grpc_port, rest_port):
        yield AsyncClient(
            api_key=server.API_KEY,
            api_host=f"localhost:{rest_port}",
            video_transport="rest",
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_rest_generate_returns_video_url(rest_client: AsyncClient):
    """Test that async REST video generation returns a video URL."""
    response = await rest_client.video.generate(prompt="foo", model="grok-imagine-video")

    assert isinstance(response, RestVideoResponse)
    assert response.model == "grok-imagine-video"
    assert response.url
    assert response.duration > 0


@pytest.mark.asyncio(loop_scope="session")
async def test_rest_generate_with_duration(rest_client: AsyncClient):
    """Test that async REST video generation respects duration parameter."""
    response = await rest_client.video.generate(
        prompt="foo",
        model="grok-imagine-video",
        duration=10,
    )

    assert isinstance(response, RestVideoResponse)
    assert response.duration == 10


@pytest.mark.asyncio(loop_scope="session")
async def test_rest_start_returns_request_id(rest_client: AsyncClient):
    """Test that async REST start() returns a request ID."""
    response = await rest_client.video.start(prompt="foo", model="grok-imagine-video")

    assert response.request_id
    assert response.request_id.startswith("rest-video-")


@pytest.mark.asyncio(loop_scope="session")
async def test_rest_get_returns_status(rest_client: AsyncClient):
    """Test that async REST get() returns status information."""
    # Start a generation
    start_response = await rest_client.video.start(prompt="foo", model="grok-imagine-video")

    # Get status (should be pending on first poll)
    get_response = await rest_client.video.get(start_response.request_id)

    assert get_response.status in ["pending", "done"]
