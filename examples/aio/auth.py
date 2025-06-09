import asyncio

from xai_sdk import AsyncClient


async def get_api_key_info(client: AsyncClient) -> None:
    """Get the information regarding your API key."""
    api_key_info = await client.auth.get_api_key_info()
    print("API key info")
    print(api_key_info)


async def main() -> None:
    client = AsyncClient()
    await get_api_key_info(client)


if __name__ == "__main__":
    asyncio.run(main())
