from unittest import mock

import pytest
import pytest_asyncio
from opentelemetry.trace import SpanKind

from xai_sdk import AsyncClient
from xai_sdk.proto import models_pb2

from .. import server
from ..server import ModelLibrary

MODEL_LIBRARY = ModelLibrary(
    language_models={
        "grok-2": models_pb2.LanguageModel(
            name="grok-2",
            aliases=["grok-2"],
            version="1.0.0",
        ),
        "grok-3": models_pb2.LanguageModel(
            name="grok-3-beta",
            aliases=["grok-3", "grok-3-latest"],
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
        "grok-2-image": models_pb2.ImageGenerationModel(
            name="grok-2-image",
            aliases=["grok-2-image"],
            version="1.0.0",
        ),
    },
)


@pytest.fixture(scope="session")
def test_server_port():
    with server.run_test_server(model_library=MODEL_LIBRARY) as port:
        yield port


@pytest_asyncio.fixture(scope="session")
async def test_client(test_server_port: int):
    client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")
    yield client


@pytest.mark.asyncio(loop_scope="session")
async def test_list_language_models(test_client: AsyncClient):
    models = await test_client.models.list_language_models()
    assert len(models) == 2
    assert models[0].name == "grok-2"
    assert models[1].name == "grok-3-beta"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_embedding_models(test_client: AsyncClient):
    models = await test_client.models.list_embedding_models()
    assert len(models) == 1
    assert models[0].name == "embedding-beta"


@pytest.mark.asyncio(loop_scope="session")
async def test_list_image_generation_models(test_client: AsyncClient):
    models = await test_client.models.list_image_generation_models()
    assert len(models) == 1
    assert models[0].name == "grok-2-image"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_language_model(test_client: AsyncClient):
    model = await test_client.models.get_language_model("grok-2")
    assert model.name == "grok-2"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_embedding_model(test_client: AsyncClient):
    model = await test_client.models.get_embedding_model("embedding-beta")
    assert model.name == "embedding-beta"


@pytest.mark.asyncio(loop_scope="session")
async def test_get_image_generation_model(test_client: AsyncClient):
    model = await test_client.models.get_image_generation_model("grok-2-image")
    assert model.name == "grok-2-image"


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_list_language_models_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.list_language_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_language_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_get_language_model_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.get_language_model("grok-2")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_language_model grok-2",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-2"},
    )


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_list_embedding_models_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.list_embedding_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_embedding_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_get_embedding_model_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.get_embedding_model("embedding-beta")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_embedding_model embedding-beta",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "embedding-beta"},
    )


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_list_image_generation_models_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.list_image_generation_models()

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="list_image_generation_models",
        kind=SpanKind.CLIENT,
    )


@mock.patch("xai_sdk.aio.models.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_get_image_generation_model_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, test_client: AsyncClient
):
    await test_client.models.get_image_generation_model("grok-2-image")

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="get_image_generation_model grok-2-image",
        kind=SpanKind.CLIENT,
        attributes={"gen_ai.request.model": "grok-2-image"},
    )
