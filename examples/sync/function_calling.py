import json
from typing import Literal, Sequence

from absl import app, flags
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import system, tool, tool_result, user

STREAM = flags.DEFINE_bool("stream", False, "Whether streaming is enabled.")


def function_calling(client: Client) -> None:
    """Multi-turn chat with function calling."""

    def get_weather(city: str, units: Literal["C", "F"]) -> str:
        temperature = 20 if units == "C" else 68
        return f"The weather in {city} is sunny at a temperature of {temperature} {units}."

    chat = client.chat.create(
        model="grok-3",
        messages=[system("You are a helpful assistant that can answer questions and help with tasks.")],
        tools=[
            tool(
                name="get_weather",
                description="Get the weather for a given city.",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "The name of the city to get the weather for."},
                        "units": {
                            "type": "string",
                            "description": "The units to use for the temperature.",
                            "enum": ["C", "F"],
                        },
                    },
                    "required": ["city", "units"],
                },
            ),
        ],
    )

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        chat.append(user(user_input))
        response = chat.sample()
        chat.append(response)

        if response.content:
            print("Grok: ", end="", flush=True)
            print(response.content, end="", flush=True)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_args = json.loads(tool_call.function.arguments)
                result = get_weather(tool_args["city"], tool_args["units"])
                chat.append(tool_result(result))

            response = chat.sample()
            print()
            print("Grok: ", end="", flush=True)
            print(response.content, end="", flush=True)
            chat.append(response)

        print()


def function_calling_streaming(client: Client) -> None:
    """Multi-turn chat with function calling and streaming."""

    # Define the shape of the tool call arguments as a Pydantic model.
    class GetWeatherRequest(BaseModel):
        city: str = Field(description="The name of the city to get the weather for.")
        units: Literal["C", "F"] = Field(description="The units to use for the temperature.")

    def get_weather(request: GetWeatherRequest) -> str:
        temperature = 20 if request.units == "C" else 68
        return f"The weather in {request.city} is sunny at a temperature of {temperature} {request.units}."

    conversation = client.chat.create(
        model="grok-3",
        messages=[system("You are a helpful assistant that can answer questions and help with tasks.")],
        tools=[
            tool(
                name="get_weather",
                description="Get the weather for a given city.",
                parameters=GetWeatherRequest.model_json_schema(),
            )
        ],
    )

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        conversation.append(user(user_input))
        stream = conversation.stream()
        print("Grok: ", end="", flush=True)

        last_response = None
        for response, chunk in stream:
            print(chunk.content, end="", flush=True)
            last_response = response

        assert last_response is not None
        conversation.append(last_response)

        if last_response.tool_calls:
            for tool_call in last_response.tool_calls:
                # Validate the tool call arguments as a Pydantic model and get proper type checking.
                request = GetWeatherRequest.model_validate_json(tool_call.function.arguments)
                result = get_weather(request)
                conversation.append(tool_result(result))

            stream = conversation.stream()
            last_response = None
            for response, chunk in stream:
                print(chunk.content, end="", flush=True)
                last_response = response

            assert last_response is not None
            conversation.append(last_response)

        print()


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = Client()

    if STREAM.value:
        function_calling_streaming(client)
    else:
        function_calling(client)


if __name__ == "__main__":
    app.run(main)
