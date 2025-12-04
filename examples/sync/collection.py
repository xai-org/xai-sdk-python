import datetime

import xai_sdk


def create_collection_example(client: xai_sdk.Client):
    print("\n=== Create Collection Example ===")

    collection = client.collections.create(
        name="research-papers",
        model_name="grok-embedding-small",
    )

    print(f"Created collection: {collection.collection_name}")
    print(f"Collection ID: {collection.collection_id}")
    print(f"Model: {collection.index_configuration.model_name}")
    print(f"Created at: {collection.created_at.ToDatetime()}")
    return collection.collection_id


def create_collection_with_token_chunking(client: xai_sdk.Client):
    print("\n=== Create Collection with Token-Based Chunking ===")

    collection = client.collections.create(
        name="code-snippets",
        chunk_configuration={
            "tokens_configuration": {
                "max_chunk_size_tokens": 500,
                "chunk_overlap_tokens": 50,
                "encoding_name": "cl100k_base",
            },
            "strip_whitespace": False,
        },
    )

    print(f"Created collection: {collection.collection_name}")
    print(f"Collection ID: {collection.collection_id}")
    print(f"Collection Chunk Configuration: {collection.chunk_configuration}")
    return collection.collection_id


def list_collections_example(client: xai_sdk.Client):
    print("\n=== List Collections Example ===")

    response = client.collections.list(
        limit=10,
        order="asc",
        sort_by="name",
    )

    print(f"Found {len(response.collections)} collections (sorted by name):")
    for collection in response.collections:
        print(f"  - {collection.collection_name} (ID: {collection.collection_id})")
        print(f"    Documents: {collection.documents_count}")

    if response.pagination_token:
        print("\nPagination token available for next page")


def get_collection_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Get Collection Metadata Example ===")

    collection = client.collections.get(collection_id)
    print(f"Collection: {collection.collection_name}")
    print(f"ID: {collection.collection_id}")
    print(f"Documents: {collection.documents_count}")
    print(f"Model: {collection.index_configuration.model_name}")
    print(f"Created at: {collection.created_at.ToDatetime()}")
    print(f"Chunk Configuration: {collection.chunk_configuration}")

    if collection.field_definitions:
        print("Field definitions:")
        for field in collection.field_definitions:
            print(f"  - {field.key}: required={field.required}, unique={field.unique}")


def update_collection_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Update Collection Example ===")

    updated = client.collections.update(
        collection_id,
        name="research-papers-updated",
        chunk_configuration={
            "chars_configuration": {
                "max_chunk_size_chars": 2000,
                "chunk_overlap_chars": 200,
            },
            "strip_whitespace": True,
        },
    )

    print(f"Updated collection: {updated.collection_name}")
    print(f"New chunk size: {updated.chunk_configuration.chars_configuration.max_chunk_size_chars}")


def upload_document_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Upload Document Example ===")

    document_content = b"""Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that focuses on building
systems that can learn from data and improve their performance over time without
being explicitly programmed."""

    document = client.collections.upload_document(collection_id, name="ml-fundamentals.txt", data=document_content)

    print(f"Uploaded document: {document.file_metadata.name}")
    print(f"File ID: {document.file_metadata.file_id}")
    print(f"Size: {document.file_metadata.size_bytes} bytes")
    print(f"Status: {document.status}")
    return document.file_metadata.file_id


def upload_document_with_wait_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Upload Document with Wait for Indexing Example ===")

    document_content = b"""Deep Learning Neural Networks

Deep learning is a subset of machine learning that uses neural networks with
multiple layers. These networks can learn hierarchical representations of data,
making them particularly effective for tasks like image recognition and natural
language processing."""

    print("Uploading document and waiting for indexing to complete...")

    document = client.collections.upload_document(
        collection_id,
        name="deep-learning.txt",
        data=document_content,
        wait_for_indexing=True,
        poll_interval=datetime.timedelta(seconds=1),
        timeout=datetime.timedelta(seconds=60),
    )

    print(f"Document uploaded and indexed: {document.file_metadata.name}")
    print(f"File ID: {document.file_metadata.file_id}")
    print(f"Status: {document.status}")
    print("✓ Document is ready to be searched immediately!")
    return document.file_metadata.file_id


def add_existing_document_example(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Add Existing Document Example ===")

    client.collections.add_existing_document(
        collection_id,
        file_id,
    )

    print(f"Added existing document (file_id: {file_id}) to collection")


def list_documents_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== List Documents Example ===")

    response = client.collections.list_documents(
        collection_id,
        limit=10,
        order="desc",
        sort_by="age",
    )

    print(f"Found {len(response.documents)} documents:")
    for doc in response.documents:
        print(f"  - {doc.file_metadata.name}")
        print(f"    File ID: {doc.file_metadata.file_id}")
        print(f"    Size: {doc.file_metadata.size_bytes} bytes")
        print(f"    Status: {doc.status}")
        if doc.fields:
            print(f"    Fields: {dict(doc.fields)}")


def get_document_example(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Get Document Metadata Example ===")

    document = client.collections.get_document(file_id, collection_id)
    print(f"Document: {document.file_metadata.name}")
    print(f"File ID: {document.file_metadata.file_id}")
    print(f"Size: {document.file_metadata.size_bytes} bytes")
    print(f"Content type: {document.file_metadata.content_type}")
    print(f"Status: {document.status}")
    print(f"Fields: {dict(document.fields)}")


def batch_get_documents_example(client: xai_sdk.Client, collection_id: str, file_ids: list[str]):
    print("\n=== Batch Get Documents Example ===")

    response = client.collections.batch_get_documents(collection_id, file_ids)

    print(f"Retrieved {len(response.documents)} documents:")
    for doc in response.documents:
        print(f"  - {doc.file_metadata.name} ({doc.file_metadata.file_id})")


def update_document_example(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Update Document Example ===")

    new_content = b"Updated content for the document with additional information."

    updated = client.collections.update_document(
        collection_id,
        file_id,
        name="ml-fundamentals-updated.txt",
        data=new_content,
        content_type="text/plain",
    )

    print(f"Updated document: {updated.file_metadata.name}")
    print(f"New size: {updated.file_metadata.size_bytes} bytes")


def search_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Hybrid Search Example ===")

    results = client.collections.search(
        query="What is machine learning?",
        collection_ids=[collection_id],
        limit=5,
        instructions="Return concise, user-friendly explanations focused on core concepts.",
        retrieval_mode="hybrid",
    )

    print(f"Found {len(results.matches)} matches:")
    for i, match in enumerate(results.matches, 1):
        print(f"\n  Match {i}:")
        print(f"    File ID: {match.file_id}")
        print(f"    Score: {match.score:.4f}")
        print(f"    Chunk: {match.chunk_content[:100]}...")


def reindex_document_example(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Reindex Document Example ===")

    client.collections.reindex_document(collection_id, file_id)
    print(f"Reindexed document (file_id: {file_id})")


def remove_document_example(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Remove Document Example ===")

    client.collections.remove_document(collection_id, file_id)
    print(f"Removed document (file_id: {file_id}) from collection")


def delete_collection_example(client: xai_sdk.Client, collection_id: str):
    print("\n=== Delete Collection Example ===")

    client.collections.delete(collection_id)
    print(f"Deleted collection (ID: {collection_id})")


def main() -> None:
    client = xai_sdk.Client()

    # Create collections
    collection_id = create_collection_example(client)
    collection_id_2 = create_collection_with_token_chunking(client)

    # List collections
    list_collections_example(client)

    # Get collection metadata
    get_collection_example(client, collection_id)

    # Update collection
    update_collection_example(client, collection_id)

    # Upload a document
    file_id = upload_document_example(client, collection_id)

    # Upload a document with wait for indexing
    file_id_wait = upload_document_with_wait_example(client, collection_id)

    # Upload another document for batch operations
    file_id_2 = upload_document_example(client, collection_id)

    # Add an existing document to another collection
    add_existing_document_example(client, collection_id_2, file_id)

    # List documents
    list_documents_example(client, collection_id)

    # Get document metadata
    get_document_example(client, collection_id, file_id)

    # Batch get documents
    batch_get_documents_example(client, collection_id, [file_id, file_id_2])

    # Update document
    update_document_example(client, collection_id, file_id)

    # Search documents
    search_example(client, collection_id)

    # Reindex document (useful after updating collection configuration)
    reindex_document_example(client, collection_id, file_id)

    # Remove documents from collection
    remove_document_example(client, collection_id, file_id)
    remove_document_example(client, collection_id, file_id_2)
    remove_document_example(client, collection_id, file_id_wait)

    # Delete collections (cleanup)
    delete_collection_example(client, collection_id)
    delete_collection_example(client, collection_id_2)

    print("\n=== All examples completed successfully! ===")


if __name__ == "__main__":
    main()
