import xai_sdk


def create_collection(client: xai_sdk.Client):
    print("\n=== Create Collection ===")

    collection = client.collections.create(
        name="research-papers",
        model_name="grok-embedding-small",
        description="A collection of research papers",
    )

    print(f"Created collection: {collection.collection_name}")
    print(f"Collection ID: {collection.collection_id}")
    print(f"Model: {collection.index_configuration.model_name}")
    print(f"Created at: {collection.created_at.ToDatetime()}")
    print(f"Description: {collection.collection_description}")
    print(f"Documents Count: {collection.documents_count}")
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
        description="A collection of code snippets for search.",
    )

    print(f"Created collection: {collection.collection_name}")
    print(f"Collection ID: {collection.collection_id}")
    print(f"Description: {collection.collection_description}")
    print(f"Collection Chunk Configuration: {collection.chunk_configuration}")
    return collection.collection_id


def create_collection_with_bytes_chunking(client: xai_sdk.Client):
    print("\n=== Create Collection with Byte-Based Chunking ===")

    collection = client.collections.create(
        name="binary-data",
        chunk_configuration={
            "bytes_configuration": {
                "max_chunk_size_bytes": 4096,
                "chunk_overlap_bytes": 512,
            },
        },
        field_definitions=[
            {
                "key": "category",
                "required": True,
                "inject_into_chunk": True,
                "unique": False,
                "description": "The category of the binary data",
            },
        ],
    )

    print(f"Created collection: {collection.collection_name}")
    print(f"Collection ID: {collection.collection_id}")
    print(f"Chunk Configuration: {collection.chunk_configuration}")
    print(f"Field definitions: {[fd.key for fd in collection.field_definitions]}")
    return collection.collection_id


def list_collections(client: xai_sdk.Client):
    print("\n=== List Collections ===")

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


def list_collections_with_filter(client: xai_sdk.Client):
    print("\n=== List Collections with Filter ===")

    response = client.collections.list(filter='collection_name:"research"')

    print(f"Found {len(response.collections)} matching collections:")
    for collection in response.collections:
        print(f"  - {collection.collection_name}")


def get_collection(client: xai_sdk.Client, collection_id: str):
    print("\n=== Get Collection Metadata ===")

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


def update_collection(client: xai_sdk.Client, collection_id: str):
    print("\n=== Update Collection ===")

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
        description="Updated research papers collection.",
    )

    print(f"Updated collection: {updated.collection_name}")
    print(f"New chunk size: {updated.chunk_configuration.chars_configuration.max_chunk_size_chars}")

    # Add a field definition using dict syntax.
    updated = client.collections.update(
        collection_id,
        field_definitions=[
            {
                "field_definition": {
                    "key": "author",
                    "required": False,
                    "inject_into_chunk": True,
                    "unique": False,
                },
                "operation": "add",
            },
        ],
    )

    print(f"Added field definition: {[fd.key for fd in updated.field_definitions]}")

    # Delete a field definition using dict syntax.
    updated = client.collections.update(
        collection_id,
        field_definitions=[{"key": "author", "operation": "delete"}],
    )

    print(f"Deleted field definition, remaining: {[fd.key for fd in updated.field_definitions]}")


def upload_document(client: xai_sdk.Client, collection_id: str, name: str, data: bytes, **kwargs):
    print(f"\n=== Upload Document: {name} ===")

    document = client.collections.upload_document(
        collection_id,
        name=name,
        data=data,
        wait_for_indexing=True,
        **kwargs,
    )

    print(f"Uploaded document: {document.file_metadata.name}")
    print(f"File ID: {document.file_metadata.file_id}")
    print(f"Size: {document.file_metadata.size_bytes} bytes")
    print(f"Status: {document.status}")
    return document.file_metadata.file_id


def add_existing_document(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Add Existing Document ===")

    client.collections.add_existing_document(
        collection_id,
        file_id,
    )

    print(f"Added existing document (file_id: {file_id}) to collection")


def list_documents(client: xai_sdk.Client, collection_id: str):
    print("\n=== List Documents ===")

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


def list_documents_with_filter(client: xai_sdk.Client, collection_id: str):
    print("\n=== List Documents with Filter ===")

    response = client.collections.list_documents(
        collection_id,
        filter="status:DOCUMENT_STATUS_PROCESSED",
    )

    print(f"Found {len(response.documents)} processed documents:")
    for doc in response.documents:
        print(f"  - {doc.file_metadata.name} (status: {doc.status})")


def get_document(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Get Document Metadata ===")

    document = client.collections.get_document(file_id, collection_id)
    print(f"Document: {document.file_metadata.name}")
    print(f"File ID: {document.file_metadata.file_id}")
    print(f"Size: {document.file_metadata.size_bytes} bytes")
    print(f"Content type: {document.file_metadata.content_type}")
    print(f"Status: {document.status}")
    print(f"Fields: {dict(document.fields)}")


def batch_get_documents(client: xai_sdk.Client, collection_id: str, file_ids: list[str]):
    print("\n=== Batch Get Documents ===")

    response = client.collections.batch_get_documents(collection_id, file_ids)

    print(f"Retrieved {len(response.documents)} documents:")
    for doc in response.documents:
        print(f"  - {doc.file_metadata.name} ({doc.file_metadata.file_id})")


def update_document(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Update Document ===")

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


def search(client: xai_sdk.Client, collection_id: str):
    print("\n=== Hybrid Search ===")

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


def reindex_document(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Reindex Document ===")

    client.collections.reindex_document(collection_id, file_id)
    print(f"Reindexed document (file_id: {file_id})")


def remove_document(client: xai_sdk.Client, collection_id: str, file_id: str):
    print("\n=== Remove Document ===")

    client.collections.remove_document(collection_id, file_id)
    print(f"Removed document (file_id: {file_id}) from collection")


def generate_description(client: xai_sdk.Client, collection_id: str):
    print("\n=== Generate Collection Description ===")

    description = client.collections.generate_description(collection_id)
    print(f"Generated description: {description}")


def delete_collection(client: xai_sdk.Client, collection_id: str):
    print("\n=== Delete Collection ===")

    client.collections.delete(collection_id)
    print(f"Deleted collection (ID: {collection_id})")


def main() -> None:
    client = xai_sdk.Client()

    # Create collections with different chunking strategies
    collection_id = create_collection(client)
    collection_id_2 = create_collection_with_token_chunking(client)
    collection_id_3 = create_collection_with_bytes_chunking(client)

    # List collections (with and without filter)
    list_collections(client)
    list_collections_with_filter(client)

    # Get collection metadata
    get_collection(client, collection_id)

    # Update collection (name, chunk config, description, and field definitions)
    update_collection(client, collection_id)

    # Upload documents
    file_id = upload_document(
        client,
        collection_id,
        "ml-fundamentals.txt",
        b"Machine learning is a subset of artificial intelligence that focuses on building "
        b"systems that can learn from data and improve their performance over time without "
        b"being explicitly programmed.",
        fields={"topic": "machine-learning", "level": "beginner"},
    )

    file_id_2 = upload_document(
        client,
        collection_id,
        "deep-learning.txt",
        b"Deep learning is a subset of machine learning that uses neural networks with "
        b"multiple layers. These networks can learn hierarchical representations of data, "
        b"making them particularly effective for tasks like image recognition and natural "
        b"language processing.",
    )

    # Add an existing document to another collection
    add_existing_document(client, collection_id_2, file_id)

    # List documents (with and without filter)
    list_documents(client, collection_id)
    list_documents_with_filter(client, collection_id)

    # Get document metadata
    get_document(client, collection_id, file_id)

    # Batch get documents
    batch_get_documents(client, collection_id, [file_id, file_id_2])

    # Update a document
    update_document(client, collection_id, file_id)

    # Search documents
    search(client, collection_id)

    # Generate a description from collection contents
    generate_description(client, collection_id)

    # Reindex document (useful after updating collection configuration)
    reindex_document(client, collection_id, file_id)

    # Remove documents from collection
    remove_document(client, collection_id, file_id)
    remove_document(client, collection_id, file_id_2)

    # Delete collections (cleanup)
    delete_collection(client, collection_id)
    delete_collection(client, collection_id_2)
    delete_collection(client, collection_id_3)

    print("\n=== All examples completed successfully! ===")


if __name__ == "__main__":
    main()
