import asyncio

from xai_sdk import AsyncClient
from xai_sdk.chat import image, user


async def main():
    client = AsyncClient()

    # Create a new batch
    batch = await client.batch.create(batch_name="my_batch")
    print("Created new batch")
    print("---" * 20)
    print(batch)

    # Compose the chat requests
    image_urls = [
        "https://images.unsplash.com/photo-1761301006532-fa8143787a88?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=987",
        "https://images.unsplash.com/photo-1761562964782-4c971df72d29?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=987",
        "https://images.unsplash.com/photo-1521747116042-5a810fda9664?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1170",
    ]

    batch_requests = []

    for index, image_url in enumerate(image_urls):
        chat = client.chat.create(
            model="grok-4-1-fast-reasoning",
            max_tokens=1000,
            temperature=0.7,
            batch_request_id=f"req_{index}",
        )
        chat.append(
            user(
                "Please analyze this image and return JSON with the following fields: "
                "'city', 'country', 'attraction_name'",
                image(image_url, detail="high"),
            )
        )
        batch_requests.append(chat)

    # Add requests to the batch
    await client.batch.add(batch_id=batch.batch_id, batch_requests=batch_requests)

    # Wait for batch to complete by polling for completion
    print("Waiting for batch to complete...")
    while True:
        batch = await client.batch.get(batch_id=batch.batch_id)
        print(f"Progress: {batch.state.num_success + batch.state.num_error}/{batch.state.num_requests}")
        if batch.state.num_pending == 0:
            break
        await asyncio.sleep(3)

    # Display final batch status
    print("Final batch status")
    print("---" * 10)
    print(batch)

    # Display cost (ticks are in units of 1e-10 USD)
    print(f"Total cost: ${batch.cost_breakdown.total_cost_usd_ticks / 1e10:.4f}")

    # List the individual requests of a batch
    metadata = await client.batch.list_batch_requests(batch_id=batch.batch_id)
    print("Listing metadata of individual requests in batch")
    print("---" * 20)
    print(metadata)

    # List the results of a batch
    batch_results = await client.batch.list_batch_results(batch_id=batch.batch_id)
    # Filter the results into succeeded and failed
    succeeded = batch_results.succeeded
    failed = batch_results.failed
    print("Listing batch results")
    print("---" * 20)

    print("Succeeded results:")
    print("---" * 20)
    for result in succeeded:
        print(f"Batch request ID: {result.batch_request_id}")
        print(f"Response Content: {result.response.content}")

    if len(failed) > 0:
        print("Failed results:")
        print("---" * 20)

        for result in failed:
            print(f"Batch request ID: {result.batch_request_id}")
            print(f"Error: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
