import pytest

from xai_sdk import Client

from .. import server


@pytest.fixture(scope="session")
def client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


@pytest.fixture
def image_asset():
    return server.read_image()


def test_base64(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-2-image", image_format="base64")

    assert response.prompt == "foo"
    assert image_asset == response.image


def test_url(client: Client, image_asset: bytes):
    response = client.image.sample(prompt="foo", model="grok-2-image", image_format="url")

    assert response.prompt == "foo"
    assert image_asset == response.image


def test_batch(client: Client, image_asset: bytes):
    responses = client.image.sample_batch(prompt="foo", model="grok-2-image", n=2, image_format="base64")

    assert len(responses) == 2

    for r in responses:
        assert r.prompt == "foo"
        assert image_asset == r.image
