from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client
from xai_sdk.image import ImageFormat

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


@mock.patch("xai_sdk.sync.image.tracer")
@pytest.mark.parametrize("image_format", ["url", "base64"])
def test_sample_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: Client, image_format: ImageFormat
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    user = "test-user-123"
    response = client.image.sample(
        prompt="A beautiful sunset", model="grok-2-image", image_format=image_format, user=user
    )

    expected_request_attributes = {
        "gen_ai.prompt": "A beautiful sunset",
        "gen_ai.operation.name": "generate_image",
        "gen_ai.system": "xai",
        "gen_ai.request.model": "grok-2-image",
        "gen_ai.request.image.format": image_format,
        "gen_ai.request.image.count": 1,
        "user_id": user,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample grok-2-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-2-image",
        "gen_ai.response.image.format": image_format,
        "gen_ai.response.0.image.up_sampled_prompt": response.prompt,
    }

    if image_format == "url":
        expected_response_attributes["gen_ai.response.0.image.url"] = response.url
    else:
        expected_response_attributes["gen_ai.response.0.image.base64"] = response.base64

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.sync.image.tracer")
@pytest.mark.parametrize("image_format", ["url", "base64"])
def test_sample_batch_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: Client, image_format: ImageFormat
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    user = "test-user-123"
    responses = client.image.sample_batch(
        prompt="A beautiful sunset", model="grok-2-image", n=3, image_format=image_format, user=user
    )

    assert len(responses) == 3

    expected_request_attributes = {
        "gen_ai.prompt": "A beautiful sunset",
        "gen_ai.operation.name": "generate_image",
        "gen_ai.system": "xai",
        "gen_ai.request.model": "grok-2-image",
        "gen_ai.request.image.format": image_format,
        "gen_ai.request.image.count": 3,
        "user_id": user,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="image.sample_batch grok-2-image",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.model": "grok-2-image",
        "gen_ai.response.image.format": image_format,
        "gen_ai.response.0.image.up_sampled_prompt": responses[0].prompt,
        "gen_ai.response.1.image.up_sampled_prompt": responses[1].prompt,
        "gen_ai.response.2.image.up_sampled_prompt": responses[2].prompt,
    }

    if image_format == "url":
        expected_response_attributes["gen_ai.response.0.image.url"] = responses[0].url
        expected_response_attributes["gen_ai.response.1.image.url"] = responses[1].url
        expected_response_attributes["gen_ai.response.2.image.url"] = responses[2].url
    else:
        expected_response_attributes["gen_ai.response.0.image.base64"] = responses[0].base64
        expected_response_attributes["gen_ai.response.1.image.base64"] = responses[1].base64
        expected_response_attributes["gen_ai.response.2.image.base64"] = responses[2].base64

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)
