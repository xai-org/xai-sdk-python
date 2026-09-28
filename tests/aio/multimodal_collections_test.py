import uuid
from pathlib import Path

import pytest
import pytest_asyncio

from xai_sdk import AsyncClient
from xai_sdk.multimodal_collections import (
    DEFAULT_IMAGE_PATH_FIELD,
    document_fields_by_file_id_async,
    multimodal_field_definitions,
    resolve_multimodal_search_results,
    upload_multimodal_document_async,
)
from xai_sdk.proto import documents_pb2

from .. import server


@pytest.fixture(scope="session")
def in_memory_store():
    store = server.InMemoryStore()
    yield store
    store.clear()


@pytest.fixture(scope="session")
def management_server(in_memory_store: server.InMemoryStore):
    with server.run_test_management_server(in_memory_store=in_memory_store) as management_port:
        yield management_port


@pytest_asyncio.fixture(scope="session")
async def client(management_server: int, in_memory_store: server.InMemoryStore):
    with server.run_test_server(in_memory_store=in_memory_store) as port:
        yield AsyncClient(
            api_host=f"localhost:{port}",
            api_key=server.API_KEY,
            management_api_host=f"localhost:{management_server}",
            management_api_key=server.MANAGEMENT_API_KEY,
        )


@pytest.mark.asyncio
async def test_upload_and_resolve_multimodal_document_async(client: AsyncClient, tmp_path: Path):
    image = tmp_path / "catalog-item.jpg"
    image.write_bytes(b"fake-jpeg")

    collection = await client.collections.create(
        f"multimodal-{uuid.uuid4()}",
        field_definitions=multimodal_field_definitions(),
    )

    document = await upload_multimodal_document_async(
        client.collections,
        collection.collection_id,
        name="catalog-item.txt",
        text="Glossy red widget with chrome trim.",
        image_path=image,
        extra_fields={"sku": "W-001"},
        wait_for_indexing=True,
    )

    assert document.fields[DEFAULT_IMAGE_PATH_FIELD] == str(image.resolve())
    assert document.fields["sku"] == "W-001"

    file_id = document.file_metadata.file_id
    match = documents_pb2.SearchMatch(
        file_id=file_id,
        chunk_id="chunk-1",
        chunk_content=f"{image.resolve()}\nGlossy red widget with chrome trim.",
        score=0.9,
        collection_ids=[collection.collection_id],
    )
    fields_map = await document_fields_by_file_id_async(
        client.collections,
        collection.collection_id,
        [match],
    )
    resolved = resolve_multimodal_search_results([match], fields_map)

    assert resolved[0]["image_paths"] == [str(image.resolve())]
