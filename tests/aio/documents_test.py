import pytest
import pytest_asyncio

from xai_sdk import AsyncClient

from .. import server


@pytest_asyncio.fixture(scope="session")
async def client():
    with server.run_test_server() as port:
        yield AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{port}")


@pytest.mark.asyncio(loop_scope="session")
async def test_search(client: AsyncClient):
    response = await client.documents.search(query="test-query-1", collection_ids=["test-collection-1"])
    assert len(response.matches) == 2
    assert response.matches[0].file_id == "test-file-1"
    assert response.matches[1].file_id == "test-file-1"

    response = await client.documents.search(query="test-query-2", collection_ids=["test-collection-1"])
    assert len(response.matches) == 1
    assert response.matches[0].file_id == "test-file-2"


@pytest.mark.asyncio(loop_scope="session")
async def test_search_with_limit(client: AsyncClient):
    response = await client.documents.search(query="test-query-1", collection_ids=["test-collection-1"], limit=1)
    assert len(response.matches) == 1
    assert response.matches[0].file_id == "test-file-1"
    assert response.matches[0].chunk_id == "test-chunk-1"
    assert response.matches[0].chunk_content == "test-chunk-content-1"
    assert response.matches[0].score == 0.5
