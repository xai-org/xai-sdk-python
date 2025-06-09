import pytest

from xai_sdk import AsyncClient

from .. import server


@pytest.fixture
def image_asset():
    return server.read_image()


@pytest.mark.asyncio(loop_scope="session")
async def test_base64(image_asset: bytes):
    with server.run_test_server() as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")
        response = await client.image.sample(prompt="foo", model="grok-2-image", image_format="base64")

        assert response.prompt == "foo"
        assert image_asset == await response.image


@pytest.mark.asyncio(loop_scope="session")
async def test_url(image_asset: bytes):
    with server.run_test_server() as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")
        response = await client.image.sample(prompt="foo", model="grok-2-image", image_format="url")

        assert response.prompt == "foo"
        assert image_asset == await response.image


@pytest.mark.asyncio(loop_scope="session")
async def test_batch(image_asset: bytes):
    with server.run_test_server() as port:
        client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")
        responses = await client.image.sample_batch(prompt="foo", model="grok-2-image", n=2, image_format="base64")

        assert len(responses) == 2

        for r in responses:
            assert r.prompt == "foo"
            assert image_asset == await r.image
