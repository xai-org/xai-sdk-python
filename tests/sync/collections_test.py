import uuid
from typing import Union

import grpc
import pytest

from xai_sdk import Client
from xai_sdk.collections import CollectionSortBy, DocumentSortBy, Order
from xai_sdk.proto import collections_pb2, shared_pb2, types_pb2

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


@pytest.fixture(scope="session")
def client(management_server: int):
    with server.run_test_server() as port:
        yield Client(
            api_host=f"localhost:{port}",
            api_key=server.API_KEY,
            management_api_host=f"localhost:{management_server}",
            management_api_key=server.MANAGEMENT_API_KEY,
        )


def test_create_collection(client: Client):
    collection_name = f"test-collection-{uuid.uuid4()}"
    chunk_configuration = types_pb2.ChunkConfiguration(
        chars_configuration=types_pb2.CharsConfiguration(max_chunk_size_chars=100, chunk_overlap_chars=10),
        tokens_configuration=types_pb2.TokensConfiguration(
            max_chunk_size_tokens=100, chunk_overlap_tokens=10, encoding_name="utf-8"
        ),
        strip_whitespace=True,
        inject_name_into_chunks=True,
    )
    collection_metadata = client.collections.create(
        collection_name,
        model_name="grok-embedding",
        chunk_configuration=chunk_configuration,
    )

    assert collection_metadata.collection_id is not None
    assert collection_metadata.collection_name == collection_name
    assert collection_metadata.created_at is not None

    response = client.collections.get(collection_metadata.collection_id)
    assert response.collection_id == collection_metadata.collection_id
    assert response.collection_name == collection_name
    assert response.index_configuration == types_pb2.IndexConfiguration(model_name="grok-embedding")
    assert response.chunk_configuration == chunk_configuration
    assert response.created_at == collection_metadata.created_at
    assert response.documents_count == 0


def test_list_collections(client: Client):
    response = client.collections.list()
    assert len(response.collections) >= 2

    for collection_metadata in response.collections:
        assert collection_metadata.collection_id is not None
        assert collection_metadata.collection_name is not None
        assert collection_metadata.created_at is not None

    collection_names = [c.collection_name for c in response.collections]
    assert "test-collection-1" in collection_names
    assert "test-collection-2" in collection_names


@pytest.mark.parametrize(
    "order", ["asc", "desc", shared_pb2.Ordering.ORDERING_ASCENDING, shared_pb2.Ordering.ORDERING_DESCENDING]
)
@pytest.mark.parametrize(
    "sort_by",
    [
        "name",
        collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_NAME,
    ],
)
def test_list_collections_sort_by_name(
    client: Client,
    order: Union[Order, "shared_pb2.Ordering"],
    sort_by: Union[CollectionSortBy, "collections_pb2.CollectionsSortBy"],
):
    response = client.collections.list(sort_by=sort_by, order=order)
    assert len(response.collections) >= 2

    reverse = order in [shared_pb2.Ordering.ORDERING_DESCENDING, "desc"]
    collection_names = [c.collection_name for c in response.collections]
    assert collection_names == sorted(collection_names, reverse=reverse)


@pytest.mark.parametrize(
    "order", ["asc", "desc", shared_pb2.Ordering.ORDERING_ASCENDING, shared_pb2.Ordering.ORDERING_DESCENDING]
)
@pytest.mark.parametrize(
    "sort_by",
    [
        "age",
        collections_pb2.CollectionsSortBy.COLLECTIONS_SORT_BY_AGE,
    ],
)
def test_list_collections_sort_by_age(
    client: Client,
    order: Union[Order, "shared_pb2.Ordering"],
    sort_by: Union[CollectionSortBy, "collections_pb2.CollectionsSortBy"],
):
    response = client.collections.list(sort_by=sort_by, order=order)
    assert len(response.collections) >= 2

    reverse = order in [shared_pb2.Ordering.ORDERING_DESCENDING, "desc"]
    collection_ages = [c.created_at.seconds for c in response.collections]
    assert collection_ages == sorted(collection_ages, reverse=reverse)


def test_delete_collection(client: Client):
    collection_metadata = client.collections.create("test-collection")
    assert collection_metadata.collection_id is not None

    client.collections.delete(collection_metadata.collection_id)
    with pytest.raises(grpc.RpcError) as e:
        client.collections.get(collection_metadata.collection_id)

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Collection not found"  # type: ignore


def test_get_collection_metadata(client: Client):
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    response = client.collections.get(collection_metadata.collection_id)
    assert response.collection_id == collection_metadata.collection_id
    assert response.collection_name == collection_metadata.collection_name
    assert response.created_at == collection_metadata.created_at
    assert response.index_configuration == collection_metadata.index_configuration
    assert response.chunk_configuration == collection_metadata.chunk_configuration
    assert response.documents_count == collection_metadata.documents_count


def test_get_nonexistent_collection(client: Client):
    with pytest.raises(grpc.RpcError) as e:
        client.collections.get("nonexistent-collection-id")

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Collection not found"  # type: ignore


def test_update_collection(client: Client):
    chunk_configuration = types_pb2.ChunkConfiguration(
        chars_configuration=types_pb2.CharsConfiguration(max_chunk_size_chars=100, chunk_overlap_chars=10),
        tokens_configuration=types_pb2.TokensConfiguration(
            max_chunk_size_tokens=100, chunk_overlap_tokens=10, encoding_name="utf-8"
        ),
        strip_whitespace=True,
        inject_name_into_chunks=True,
    )
    collection_metadata = client.collections.create(
        f"test-collection-{uuid.uuid4()}",
        chunk_configuration=chunk_configuration,
    )
    assert collection_metadata.collection_id is not None

    new_name = f"test-collection-{uuid.uuid4()}"
    new_chunk_configuration = types_pb2.ChunkConfiguration(
        chars_configuration=types_pb2.CharsConfiguration(max_chunk_size_chars=200, chunk_overlap_chars=20),
        tokens_configuration=types_pb2.TokensConfiguration(
            max_chunk_size_tokens=200, chunk_overlap_tokens=20, encoding_name="utf-8"
        ),
        strip_whitespace=False,
        inject_name_into_chunks=False,
    )
    client.collections.update(
        collection_metadata.collection_id,
        name=new_name,
        chunk_configuration=new_chunk_configuration,
    )

    response = client.collections.get(collection_metadata.collection_id)
    assert response.collection_name == new_name
    assert response.chunk_configuration == new_chunk_configuration


def test_update_collection_with_no_changes(client: Client):
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    with pytest.raises(ValueError) as e:
        client.collections.update(collection_metadata.collection_id)

    assert str(e.value) == "At least one of name or chunk_configuration must be provided to update a collection"


def test_search(client: Client):
    response = client.collections.search(query="test-query-1", collection_ids=["test-collection-1"])
    assert len(response.matches) == 2
    assert response.matches[0].file_id == "test-file-1"
    assert response.matches[1].file_id == "test-file-1"

    response = client.collections.search(query="test-query-2", collection_ids=["test-collection-1"])
    assert len(response.matches) == 1
    assert response.matches[0].file_id == "test-file-2"


def test_upload_document(client: Client):
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    name = "test-document.txt"
    data = b"Hello, world!"
    content_type = "text/plain"
    fields = {"key": "value"}

    document_metadata = client.collections.upload_document(
        collection_metadata.collection_id,
        name,
        data,
        content_type,
        fields,
    )
    assert document_metadata.file_metadata.file_id is not None
    assert document_metadata.file_metadata.name == name
    assert document_metadata.file_metadata.size_bytes == len(data)
    assert document_metadata.file_metadata.content_type == content_type
    assert document_metadata.file_metadata.created_at is not None
    assert document_metadata.file_metadata.expires_at is not None
    assert document_metadata.file_metadata.hash is not None
    assert document_metadata.fields == fields

    response = client.collections.get_document(
        document_metadata.file_metadata.file_id,
        collection_metadata.collection_id,
    )

    assert response.file_metadata.file_id is not None
    assert response.file_metadata.name == name
    assert response.file_metadata.size_bytes == len(data)
    assert response.file_metadata.content_type == content_type
    assert response.fields == fields


def test_add_existing_document_to_collection(client: Client):
    # Create a collection to add the document to.
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    name = "test-document.txt"
    data = b"Hello, world!"
    content_type = "text/plain"
    fields = {"key": "value"}

    # Upload a new document to the collection.
    document_metadata = client.collections.upload_document(
        collection_metadata.collection_id,
        name,
        data,
        content_type,
        fields,
    )

    # Add the previously uploaded document to a different collection.
    client.collections.add_existing_document(
        "test-collection-1",
        document_metadata.file_metadata.file_id,
        fields,
    )

    response = client.collections.get_document(
        document_metadata.file_metadata.file_id,
        "test-collection-1",
    )

    assert response.file_metadata.file_id == document_metadata.file_metadata.file_id
    assert response.file_metadata.name == name
    assert response.file_metadata.size_bytes == len(data)
    assert response.file_metadata.content_type == content_type
    assert response.fields == fields


def test_list_documents(client: Client):
    response = client.collections.list_documents("test-collection-1")
    assert len(response.documents) >= 2

    for document_metadata in response.documents:
        assert document_metadata.file_metadata.file_id is not None
        assert document_metadata.file_metadata.name is not None
        assert document_metadata.file_metadata.size_bytes is not None
        assert document_metadata.file_metadata.content_type is not None
        assert document_metadata.file_metadata.created_at is not None
        assert document_metadata.file_metadata.expires_at is not None
        assert document_metadata.file_metadata.hash is not None
        assert document_metadata.fields is not None
        assert document_metadata.status == collections_pb2.DocumentStatus.DOCUMENT_STATUS_PROCESSED
        assert document_metadata.error_message == ""

    document_names = [d.file_metadata.name for d in response.documents]
    assert "test-file-1" in document_names
    assert "test-file-3" in document_names


@pytest.mark.parametrize(
    "order", ["asc", "desc", shared_pb2.Ordering.ORDERING_ASCENDING, shared_pb2.Ordering.ORDERING_DESCENDING]
)
@pytest.mark.parametrize(
    "sort_by",
    [
        "name",
        collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_NAME,
    ],
)
def test_list_documents_sort_by_name(
    client: Client,
    order: Union[Order, "shared_pb2.Ordering"],
    sort_by: Union[DocumentSortBy, "collections_pb2.DocumentsSortBy"],
):
    response = client.collections.list_documents("test-collection-1", sort_by=sort_by, order=order)
    assert len(response.documents) >= 2

    reverse = order in [shared_pb2.Ordering.ORDERING_DESCENDING, "desc"]
    document_names = [d.file_metadata.name for d in response.documents]
    assert document_names == sorted(document_names, reverse=reverse)


@pytest.mark.parametrize(
    "order", ["asc", "desc", shared_pb2.Ordering.ORDERING_ASCENDING, shared_pb2.Ordering.ORDERING_DESCENDING]
)
@pytest.mark.parametrize(
    "sort_by",
    [
        "age",
        collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_AGE,
    ],
)
def test_list_documents_sort_by_age(
    client: Client,
    order: Union[Order, "shared_pb2.Ordering"],
    sort_by: Union[DocumentSortBy, "collections_pb2.DocumentsSortBy"],
):
    response = client.collections.list_documents("test-collection-1", sort_by=sort_by, order=order)
    assert len(response.documents) >= 2

    reverse = order in [shared_pb2.Ordering.ORDERING_DESCENDING, "desc"]
    document_ages = [d.file_metadata.created_at.seconds for d in response.documents]
    assert document_ages == sorted(document_ages, reverse=reverse)


@pytest.mark.parametrize(
    "order", ["asc", "desc", shared_pb2.Ordering.ORDERING_ASCENDING, shared_pb2.Ordering.ORDERING_DESCENDING]
)
@pytest.mark.parametrize(
    "sort_by",
    [
        "size",
        collections_pb2.DocumentsSortBy.DOCUMENTS_SORT_BY_SIZE,
    ],
)
def test_list_documents_sort_by_size(
    client: Client,
    order: Union[Order, "shared_pb2.Ordering"],
    sort_by: Union[DocumentSortBy, "collections_pb2.DocumentsSortBy"],
):
    response = client.collections.list_documents("test-collection-1", sort_by=sort_by, order=order)
    assert len(response.documents) >= 2

    reverse = order in [shared_pb2.Ordering.ORDERING_DESCENDING, "desc"]
    document_sizes = [d.file_metadata.size_bytes for d in response.documents]
    assert document_sizes == sorted(document_sizes, reverse=reverse)


def test_get_document_metadata(client: Client):
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    name = "test-document.txt"
    data = b"Hello, world!"
    content_type = "text/plain"
    fields = {"key": "value"}

    document_metadata = client.collections.upload_document(
        collection_metadata.collection_id,
        name,
        data,
        content_type,
        fields,
    )
    assert document_metadata.file_metadata.file_id is not None

    response = client.collections.get_document(
        document_metadata.file_metadata.file_id,
        collection_metadata.collection_id,
    )

    assert response.file_metadata.file_id == document_metadata.file_metadata.file_id
    assert response.file_metadata.name == name
    assert response.file_metadata.size_bytes == len(data)
    assert response.file_metadata.content_type == content_type
    assert response.fields == fields


def test_get_nonexistent_document_metadata(client: Client):
    with pytest.raises(grpc.RpcError) as e:
        client.collections.get_document(
            "nonexistent-document-id",
            "test-collection-1",
        )

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Document not found"  # type: ignore


def test_batch_get_document_metadata(client: Client):
    response = client.collections.batch_get_documents(
        "test-collection-1",
        ["test-document-1", "test-document-2"],
    )

    assert len(response.documents) == 2

    for document_metadata in response.documents:
        assert document_metadata.file_metadata.file_id is not None
        assert document_metadata.file_metadata.name is not None
        assert document_metadata.file_metadata.size_bytes is not None
        assert document_metadata.file_metadata.content_type is not None
        assert document_metadata.fields is not None


def test_remove_document_from_collection(client: Client):
    # Create a collection to add the document to.
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    # Upload a document to the collection.
    document_metadata = client.collections.upload_document(
        collection_metadata.collection_id,
        "test-document.txt",
        b"Hello, world!",
        "text/plain",
        {"key": "value"},
    )
    assert document_metadata.file_metadata.file_id is not None

    # Verify the document is in the collection.
    response = client.collections.get_document(
        document_metadata.file_metadata.file_id,
        collection_metadata.collection_id,
    )
    assert response.file_metadata.file_id == document_metadata.file_metadata.file_id
    assert response.file_metadata.name == "test-document.txt"
    assert response.file_metadata.size_bytes == len(b"Hello, world!")
    assert response.file_metadata.content_type == "text/plain"
    assert response.fields == {"key": "value"}

    # Remove the document from the collection.
    client.collections.remove_document(
        collection_metadata.collection_id,
        document_metadata.file_metadata.file_id,
    )

    # Verify the document is no longer in the collection.
    with pytest.raises(grpc.RpcError) as e:
        client.collections.get_document(
            document_metadata.file_metadata.file_id,
            collection_metadata.collection_id,
        )

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Document not found"  # type: ignore


def test_update_document(client: Client):
    collection_metadata = client.collections.create(f"test-collection-{uuid.uuid4()}")
    assert collection_metadata.collection_id is not None

    document_metadata = client.collections.upload_document(
        collection_metadata.collection_id,
        "test-document.txt",
        b"Hello, world!",
        "text/plain",
        {"key": "value"},
    )
    assert document_metadata.file_metadata.file_id is not None

    new_name = "test-document-2.txt"
    new_data = b"Hello, again!"
    new_content_type = "text/plain"
    new_fields = {"key-2": "value-2"}

    client.collections.update_document(
        collection_metadata.collection_id,
        document_metadata.file_metadata.file_id,
        name=new_name,
        data=new_data,
        content_type=new_content_type,
        fields=new_fields,
    )

    response = client.collections.get_document(
        document_metadata.file_metadata.file_id,
        collection_metadata.collection_id,
    )

    assert response.file_metadata.file_id == document_metadata.file_metadata.file_id
    assert response.file_metadata.name == new_name
    assert response.file_metadata.size_bytes == len(new_data)
    assert response.file_metadata.content_type == new_content_type
    assert response.fields == new_fields
