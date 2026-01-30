from unittest import mock

import pytest
from opentelemetry.trace import SpanKind

from xai_sdk import Client
from xai_sdk.proto import models_pb2

from .. import server
from ..server import ModelLibrary

MODEL_LIBRARY = ModelLibrary(
    language_models={
        "grok-4-1-fast-reasoning": models_pb2.LanguageModel(
            name="grok-4-1-fast-reasoning",
            aliases=["grok-4-1-fast-reasoning"],
            version="1.0.0",
        ),
        "grok-4-1-fast-non-reasoning": models_pb2.LanguageModel(
            name="grok-4-1-fast-non-reasoning",
            aliases=["grok-4-1-fast-non-reasoning"],
            version="1.0.0",
        ),
    },
    embedding_models={
        "embedding-beta": models_pb2.EmbeddingModel(
            name="embedding-beta",
            aliases=["embedding-beta"],
            version="1.0.0",
        ),
    },
    image_generation_models={
        "grok-imagine-image": models_pb2.ImageGenerationModel(
            name="grok-imagine-image",
            aliases=["grok-imagine-image"],
            version="1.0.0",
        ),
    },
)


@pytest.fixture(scope="session")
def test_client():
    with server.run_test_server(model_library=MODEL_LIBRARY) as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_list_language_models(test_client: Client):
    models = test_client.models.list_language_models()
    assert len(models) == 2
    assert models[0].name == "grok-4-1-fast-reasoning"
    assert models[1].name == "grok-4-1-fast-non-reasoning"


def test_list_embedding_models(test_client: Client):
    models = test_client.models.list_embedding_models()
    assert len(models) == 1
    assert models[0].name == "embedding-beta"


def test_list_image_generation_models(test_client: Client):
    models = test_client.models.list_image_generation_models()
    assert len(models) == 1
    assert models[0].name == "grok-imagine-image"


def test_get_language_model(test_client: Client):
    model = test_client.models.get_language_model("grok-4-1-fast-reasoning")
    assert model.name == "grok-4-1-fast-reasoning"


def test_get_embedding_model(test_client: Client):
    model = test_client.models.get_embedding_model("embedding-beta")
    assert model.name == "embedding-beta"


def test_get_image_generation_model(test_client: Client):
    model = test_client.models.get_image_generation_model("grok-imagine-image")
    assert model.name == "grok-imagine-image"


@mock.patch("xai_sdk.sync.models.tracer")
def test_list_language_models_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.models.list_language_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_language_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.sync.models.tracer")
def test_get_language_model_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.models.get_language_model("grok-4-1-fast-reasoning")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_language_model grok-4-1-fast-reasoning",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-4-1-fast-reasoning"},
    )


@mock.patch("xai_sdk.sync.models.tracer")
def test_list_embedding_models_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.models.list_embedding_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_embedding_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.sync.models.tracer")
def test_get_embedding_model_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, test_client: Client):
    test_client.models.get_embedding_model("embedding-beta")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_embedding_model embedding-beta",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "embedding-beta"},
    )


@mock.patch("xai_sdk.sync.models.tracer")
def test_list_image_generation_models_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: Client
):
    test_client.models.list_image_generation_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_image_generation_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.sync.models.tracer")
def test_get_image_generation_model_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: Client
):
    test_client.models.get_image_generation_model("grok-imagine-image")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_image_generation_model grok-imagine-image",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-imagine-image"},
    )
