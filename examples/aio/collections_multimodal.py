"""Async example: multimodal Collections workflow (text + local image path → search → vision chat)."""

import asyncio
import os
import tempfile
from pathlib import Path

from xai_sdk import AsyncClient
from xai_sdk.multimodal_collections import (
    document_fields_by_file_id_async,
    multimodal_field_definitions,
    multimodal_user_message,
    resolve_multimodal_search_results,
    upload_multimodal_document_async,
)


async def main() -> None:
    client = AsyncClient()

    with tempfile.TemporaryDirectory() as tmp_dir:
        image_path = Path(tmp_dir) / "widget.jpg"
        image_path.write_bytes(os.urandom(128))

        collection = await client.collections.create(
            name="product-catalog",
            model_name="grok-embedding-small",
            field_definitions=multimodal_field_definitions(),
            description="Text descriptions with local image path references.",
        )

        await upload_multimodal_document_async(
            client.collections,
            collection.collection_id,
            name="widget-a.txt",
            text="Red widget, 12cm, glossy finish with chrome trim.",
            image_path=image_path,
            extra_fields={"sku": "W-001"},
            wait_for_indexing=True,
        )

        results = await client.collections.search(
            query="glossy red widget",
            collection_ids=[collection.collection_id],
            limit=3,
        )
        fields_map = await document_fields_by_file_id_async(
            client.collections,
            collection.collection_id,
            results.matches,
        )
        resolved = resolve_multimodal_search_results(results.matches, fields_map)

        if not resolved:
            print("No search matches returned.")
            return

        hit = resolved[0]
        print(f"Top match (score={hit['score']:.3f}): {hit['chunk_content'][:120]}...")
        print(f"Resolved image paths: {hit['image_paths']}")

        chat = client.chat.create(model="grok-4.20-non-reasoning")
        chat.append(
            multimodal_user_message(
                f"Context from catalog:\n{hit['chunk_content']}\n\nBriefly describe this product.",
                hit["image_paths"],
            )
        )
        response = await chat.sample()
        print(f"\nVision response:\n{response.content}")

        await client.collections.delete(collection.collection_id)


if __name__ == "__main__":
    asyncio.run(main())
