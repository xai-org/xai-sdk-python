"""Example demonstrating chat with file attachments using sync Client."""

import os
import tempfile

from xai_sdk import Client
from xai_sdk.chat import file, user


def chat_with_file(client: Client, file_path: str, query: str) -> None:
    """Create a chat with a file attachment and stream the response."""
    # Upload the file first
    print(f"Uploading file: {file_path}")
    uploaded_file = client.files.upload(file_path)
    print(f"File uploaded with ID: {uploaded_file.id}\n")

    # Create a chat
    chat = client.chat.create(model="grok-4-fast")

    # Append a message with the file
    chat.append(user(query, file(uploaded_file.id)))

    # Stream the response
    print("Response:")
    print("-" * 80)
    final_response = None
    for response, chunk in chat.stream():
        final_response = response
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n" + "-" * 80)

    # Show usage stats
    if final_response:
        print(f"\nTokens used: {final_response.usage.total_tokens}")

    # Clean up
    client.files.delete(uploaded_file.id)
    print(f"Cleaned up file: {uploaded_file.id}")


def main() -> None:
    """Run the file chat example."""
    client = Client()

    # Create a sample document
    document_content = """
    Quarterly Sales Report - Q4 2024

    Revenue Summary:
    - Total Revenue: $5.2M
    - Year-over-Year Growth: +18%
    - Quarter-over-Quarter Growth: +7%

    Top Performing Products:
    - Product A: $2.1M revenue (+25% YoY)
    - Product B: $1.8M revenue (+12% YoY)
    - Product C: $1.3M revenue (+15% YoY)

    Regional Performance:
    - North America: $2.8M (54% of total)
    - Europe: $1.6M (31% of total)
    - Asia-Pacific: $0.8M (15% of total)

    Key Insights:
    - Strong holiday season performance
    - Product A showing exceptional growth
    - EMEA region expansion successful
    - Customer retention rate: 94%

    Recommendations:
    1. Increase marketing budget for Product A
    2. Expand operations in Asia-Pacific
    3. Launch new product line in Q1 2025
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(document_content)
        temp_file_path = f.name

    try:
        # Chat with the file
        chat_with_file(
            client,
            temp_file_path,
            "Please analyze this sales report and provide the top 3 key takeaways.",
        )
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    main()
