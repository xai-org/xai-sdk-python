import asyncio

from xai_sdk import AsyncClient


async def tokenize_text(client: AsyncClient):
    prompt = input("Enter a prompt: ")
    tokens = await client.tokenize.tokenize_text(prompt, model="grok-3")
    for token in tokens:
        print(f"Token ID: {token.token_id}")
        print(f"Token Text: {token.string_token}")
        print(f"Token Bytes: {token.token_bytes}")


async def main():
    client = AsyncClient()
    await tokenize_text(client)


if __name__ == "__main__":
    asyncio.run(main())
