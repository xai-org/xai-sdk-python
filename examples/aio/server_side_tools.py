import asyncio
import json

from xai_sdk import AsyncClient
from xai_sdk.chat import tool, tool_result, user
from xai_sdk.tools import code_execution, get_tool_call_type, web_search, x_search


async def agentic_search(client: AsyncClient, model: str, query: str) -> None:
    chat = client.chat.create(
        model=model,
        # All three tools are active, you can add/remove server-side tools as needed
        tools=[
            web_search(),
            x_search(),
            code_execution(),
        ],
        include=[
            "verbose_streaming",
            # The output content of `web_search` and `x_search` will be encrypted by default,
            # thus only enable the output for `code_execution`
            "code_execution_call_output",
        ],
    )
    chat.append(user(query))

    is_thinking = True
    async for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            print(f"\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
        for tool_output in chunk.tool_outputs:
            if tool_output.content:
                tool_call = tool_output.tool_calls[0]
                print(
                    f"\nTool call {tool_call.function.name}({tool_call.function.arguments}) "
                    f"outputs: {tool_output.content}"
                )
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


async def agentic_tools_with_client_side_tools_encrypted_content(client: AsyncClient, model: str) -> None:
    def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"The weather in {city} is sunny."

    weather_tool = tool(
        name="get_weather",
        description="Get the weather for a given city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city",
                }
            },
            "required": ["city"],
        },
    )

    chat = client.chat.create(
        model=model,
        tools=[web_search(), weather_tool],
        use_encrypted_content=True,
    )
    chat.append(user("What is the weather in the city of the team that won the 2025 NBA championship?"))

    while True:
        client_side_tool_calls = []
        async for response, chunk in chat.stream():
            for tool_call in chunk.tool_calls:
                if get_tool_call_type(tool_call) == "client_side_tool":
                    client_side_tool_calls.append(tool_call)
                else:
                    print(
                        f"Server-side tool call: {tool_call.function.name} "
                        f"with arguments: {tool_call.function.arguments}"
                    )

        chat.append(response)

        if not client_side_tool_calls:
            break

        for tool_call in client_side_tool_calls:
            print(f"Client-side tool call: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
            args = json.loads(tool_call.function.arguments)
            result = get_weather(args["city"])
            chat.append(tool_result(result))

    print(f"Final response: {response.content}")


async def agentic_tools_with_client_side_tools_previous_response_id(client: AsyncClient, model: str) -> None:
    def get_weather(city: str) -> str:
        """Get the weather for a given city."""
        return f"The weather in {city} is sunny."

    weather_tool = tool(
        name="get_weather",
        description="Get the weather for a given city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city",
                }
            },
            "required": ["city"],
        },
    )

    chat = client.chat.create(
        model=model,
        tools=[web_search(), weather_tool],
        store_messages=True,
    )
    chat.append(user("What is the weather in the city of the team that won the 2025 NBA championship?"))

    while True:
        client_side_tool_calls = []
        # ruff: noqa: B007
        async for response, chunk in chat.stream():
            for tool_call in chunk.tool_calls:
                if get_tool_call_type(tool_call) == "client_side_tool":
                    client_side_tool_calls.append(tool_call)
                else:
                    print(
                        f"Server-side tool call: {tool_call.function.name} "
                        f"with arguments: {tool_call.function.arguments}"
                    )

        if not client_side_tool_calls:
            break

        chat = client.chat.create(
            model=model,
            tools=[web_search(), weather_tool],
            previous_response_id=response.id,
            store_messages=True,
        )

        for tool_call in client_side_tool_calls:
            print(f"Client-side tool call: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
            args = json.loads(tool_call.function.arguments)
            result = get_weather(args["city"])
            chat.append(tool_result(result))

    print(f"Final response: {response.content}")


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

    # Trigger agentic tools with client-side tools using encrypted content
    # await agentic_tools_with_client_side_tools_encrypted_content(
    #     client,
    #     model="grok-4-fast",
    # )

    # Trigger agentic tools with client-side tools using previous response id
    # await agentic_tools_with_client_side_tools_previous_response_id(
    #     client,
    #     model="grok-4-fast",
    # )


if __name__ == "__main__":
    asyncio.run(main())
