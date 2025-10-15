import asyncio

from xai_sdk import AsyncClient
from xai_sdk.chat import user
from xai_sdk.tools import code_execution, web_search, x_search


async def agentic_search(client: AsyncClient, model: str, query: str) -> None:
    chat = client.chat.create(
        model=model,
        # All three tools are active, you can add/remove server-side tools as needed
        tools=[
            web_search(),
            x_search(),
            code_execution(),
        ],
    )
    chat.append(user(query))

    is_thinking = True
    async for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            print(f"\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
        if response.usage.reasoning_tokens and is_thinking:
            print(f"\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
        if chunk.content and is_thinking:
            print("\n\nFinal Response:")
            is_thinking = False
        if chunk.content and not is_thinking:
            print(chunk.content, end="", flush=True)

    print("\n\nCitations:")
    print(response.citations)
    print("\n\nUsage:")
    print(response.usage)
    print(response.server_side_tool_usage)
    print("\n\nTool Calls:")
    print(response.tool_calls)


async def main() -> None:
    client = AsyncClient()

    # Trigger web/x search
    await agentic_search(
        client,
        model="grok-4-fast",
        query=(
            "What was the result of Arsenal's most recent game? Where did they play, who scored and in which minutes?"
        ),
    )

    # Trigger code execution
    # await agentic_search(
    #     client,
    #     model="grok-4-fast",
    #     query=("What is the 102nd number in the Fibonacci sequence?. show me the code"),
    # )

    # Trigger x search/web search
    # await agentic_search(
    #     client,
    #     model="grok-4-fast",
    #     query="What can you tell me about the X user 0xPromar and his recent activity?",
    # )


if __name__ == "__main__":
    asyncio.run(main())
