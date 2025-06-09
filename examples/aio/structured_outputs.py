import asyncio
from datetime import datetime

from pydantic import BaseModel

from xai_sdk import AsyncClient
from xai_sdk.chat import image, system, user


async def structured_output(client: AsyncClient) -> None:
    """Extract structured information from an image."""

    # Define the desired shape of the output as a Pydantic model.
    class Item(BaseModel):
        name: str
        quantity: int
        price_in_cents: int

    class Receipt(BaseModel):
        date: datetime
        items: list[Item]
        currency: str
        total_in_cents: int

    chat = client.chat.create(
        model="grok-2-vision",
        messages=[
            system("You are an expert at extracting information from receipts. You pay great attention to detail.")
        ],
    )

    # Append the user turn with the image to the conversation.
    chat.append(
        user(
            "Extract the information contained in this receipt.",
            image(
                "https://images.pexels.com/photos/13431759/pexels-photo-13431759.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
                detail="high",
            ),
        )
    )

    # The parse method will parse the response into the Pydantic model.
    response, receipt = await chat.parse(Receipt)
    assert isinstance(receipt, Receipt)

    print(response.content, end="\n\n")

    for item in receipt.items:
        print(f"{item.quantity}x {item.name} - {item.price_in_cents / 100} {receipt.currency}")

    print(f"Total: {receipt.total_in_cents / 100} {receipt.currency}")


async def main() -> None:
    client = AsyncClient()
    await structured_output(client)


if __name__ == "__main__":
    asyncio.run(main())
