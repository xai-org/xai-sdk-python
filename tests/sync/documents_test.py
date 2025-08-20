import pytest

from xai_sdk import Client

from .. import server


@pytest.fixture(scope="session")
def client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_search(client: Client):
    response = client.documents.search(query="test-query-1", collection_ids=["test-collection-1"])
    assert len(response.matches) == 2
    assert response.matches[0].file_id == "test-file-1"
    assert response.matches[1].file_id == "test-file-1"

    response = client.documents.search(query="test-query-2", collection_ids=["test-collection-1"])
    assert len(response.matches) == 1
    assert response.matches[0].file_id == "test-file-2"


def test_search_with_limit(client: Client):
    response = client.documents.search(query="test-query-1", collection_ids=["test-collection-1"], limit=1)
    assert len(response.matches) == 1
    assert response.matches[0].file_id == "test-file-1"
    assert response.matches[0].chunk_id == "test-chunk-1"
    assert response.matches[0].chunk_content == "test-chunk-content-1"
    assert response.matches[0].score == 0.5
