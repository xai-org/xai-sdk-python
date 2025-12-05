from concurrent.futures import ThreadPoolExecutor

import requests

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import collections_search

TESLA_10_Q_PDF_URL = "https://ir.tesla.com/_flysystem/s3/sec/000162828025045968/tsla-20250930-gen.pdf"
TESLA_10_K_PDF_URL = "https://ir.tesla.com/_flysystem/s3/sec/000162828025003063/tsla-20241231-gen.pdf"


def agentic_collections_search(client: Client, model: str) -> None:
    response = client.collections.create("tesla-sec-filings")
    print(f"Created collection: {response.collection_id}")

    def upload_document(url: str, name: str, collection_id: str) -> None:
        print(f"Uploading {name} document to collection")
        pdf_content = requests.get(url, timeout=5).content
        client.collections.upload_document(
            collection_id=collection_id,
            name=name,
            data=pdf_content,
            wait_for_indexing=True,
        )
        print(f"Uploaded {name} document to collection")

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(upload_document, TESLA_10_Q_PDF_URL, "tesla-10-Q-2024.pdf", response.collection_id)
        executor.submit(upload_document, TESLA_10_K_PDF_URL, "tesla-10-K-2024.pdf", response.collection_id)

    chat = client.chat.create(
        model=model,
        tools=[
            collections_search(
                collection_ids=[
                    response.collection_id,
                ],
            ),
        ],
    )

    chat.append(
        user(
            "How many consumer vehicles did Tesla produce in total in 2024 and 2025? "
            "Show your working and cite your sources."
        )
    )

    is_thinking = True
    for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            print(f"\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
        if response.usage.reasoning_tokens and is_thinking:
            print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
        if chunk.content and is_thinking:
            print("\n\nFinal Response:")
            is_thinking = False
        if chunk.content and not is_thinking:
            print(chunk.content, end="", flush=True)
        latest_response = response

    print("\n\nCitations:")
    print(latest_response.citations)
    print("\n\nUsage:")
    print(latest_response.usage)
    print(latest_response.server_side_tool_usage)
    print("\n\nTool Calls:")
    print(latest_response.tool_calls)


def main() -> None:
    client = Client()
    agentic_collections_search(client, model="grok-4-fast")


if __name__ == "__main__":
    main()
