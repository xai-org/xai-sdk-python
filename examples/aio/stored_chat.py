import asyncio

import grpc

from xai_sdk import AsyncClient
from xai_sdk.chat import system, user


async def stored_response(client: AsyncClient):
    # Create a new chat instance with message storage enabled
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(system("You give brief answers"))
    chat.append(user("Tell me about xAI"))
    original_response = await chat.sample()

    print("----------------- Original response -----------------")
    print(original_response.content)

    # Start a new chat with the previous response as the previous_response_id
    chat = client.chat.create(
        model="grok-3",
        previous_response_id=original_response.id,
        store_messages=True,
    )
    # Purposefully ask a question that requires the previous context in order to answer.
    chat.append(user("Who was the founder?"))
    follow_up_response = await chat.sample()

    print("\n----------------- Thread one -----------------")
    print(follow_up_response.content)

    # Optionally, easily create a new thread of conversation using the original chat as a starting point.
    chat = client.chat.create(
        model="grok-3",
        previous_response_id=original_response.id,
        store_messages=True,
    )
    chat.append(user("What is the company's mission?"))

    final_response = await chat.sample()
    print("\n----------------- Thread two -----------------")
    print(final_response.content)


async def get_stored_response(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(system("You give brief answers"))
    chat.append(user("Tell me about xAI"))

    original_response = await chat.sample()
    print(f"Original response: {original_response.content}")

    retrieved_responses = await client.chat.get_stored_completion(original_response.id)
    print(f"\nRetrieved response: {retrieved_responses[0].content}")
    assert retrieved_responses[0].content == original_response.content


async def get_stored_response_batch(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(system("You give brief answers"))
    chat.append(user("Tell me about xAI"))

    original_responses = await chat.sample_batch(3)
    for index, response in enumerate(original_responses):
        print(f"\nOriginal response {index}: {response.content}")

    retrieved_responses = await client.chat.get_stored_completion(response.id)
    for index, response in enumerate(retrieved_responses):
        print(f"\nRetrieved response {index}: {response.content}")


async def delete_stored_response(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(system("You give brief answers"))
    chat.append(user("Tell me about xAI"))

    original_response = await chat.sample()
    print(f"Original response: {original_response.content}")

    deleted_id = await client.chat.delete_stored_completion(original_response.id)
    print(f"Deleted response: {deleted_id}")

    try:
        await client.chat.get_stored_completion(deleted_id)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:  # type: ignore
            print("Response not found")
            return
        else:
            raise e


async def main():
    client = AsyncClient()

    # Uncomment the respective line to run the example.
    await stored_response(client)
    # await get_stored_response(client)
    # await get_stored_response_batch(client)
    # await delete_stored_response(client)


if __name__ == "__main__":
    asyncio.run(main())
