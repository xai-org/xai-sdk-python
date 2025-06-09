from datetime import datetime, timezone
from typing import Sequence, Union

import pytest
from google.protobuf import timestamp_pb2
from pydantic import BaseModel

from xai_sdk import Client
from xai_sdk.chat import (
    Chunk,
    ImageDetail,
    ReasoningEffort,
    Response,
    ResponseFormat,
    ToolMode,
    assistant,
    image,
    required_tool,
    system,
    tool,
    tool_result,
    user,
)
from xai_sdk.proto import chat_pb2, image_pb2, sample_pb2
from xai_sdk.search import SearchParameters, news_source, rss_source, web_source, x_source

from .. import server


@pytest.fixture(scope="session")
def client():
    with server.run_test_server() as port:
        yield Client(api_key=server.API_KEY, api_host=f"localhost:{port}")


def test_unary_no_messages(client: Client):
    chat = client.chat.create("grok-3-latest")
    with pytest.raises(ValueError):
        chat.sample()


def test_unary(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    response = chat.sample()

    assert response.content == "Hello, this is a test response!"


def test_unary_batch(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    responses = chat.sample_batch(10)

    assert len(responses) == 10

    for r in responses:
        assert r.content == "Hello, this is a test response!"


def test_streaming(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    stream = chat.stream()

    chunks = []
    last_response = None
    for r, chunk in stream:
        last_response = r
        chunks.append(chunk)

    assert chunks[0].content == "Hello, "
    assert chunks[1].content == "this is "
    assert chunks[2].content == "a test "
    assert chunks[3].content == "response!"

    assert last_response is not None
    assert last_response.content == "Hello, this is a test response!"


def test_streaming_batch(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    stream = chat.stream_batch(2)

    chunks = []
    last_response = None
    for r, chunk in stream:
        last_response = r
        chunks.append(chunk)

    assert chunks[0][0].content == "Hello, "
    assert chunks[0][1].content == ""

    assert chunks[1][0].content == ""
    assert chunks[1][1].content == "Hello, "

    assert chunks[2][0].content == "this is "
    assert chunks[2][1].content == ""

    assert chunks[3][0].content == ""
    assert chunks[3][1].content == "this is "

    assert chunks[4][0].content == "a test "
    assert chunks[4][1].content == ""

    assert chunks[5][0].content == ""
    assert chunks[5][1].content == "a test "

    assert chunks[6][0].content == "response!"
    assert chunks[6][1].content == ""

    assert chunks[7][0].content == ""
    assert chunks[7][1].content == "response!"

    assert last_response is not None
    assert last_response[0].content == "Hello, this is a test response!"
    assert last_response[1].content == "Hello, this is a test response!"


def test_function_calling(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "units": {"type": "string"}},
                    "required": ["city", "units"],
                },
            )
        ],
    )
    chat.append(user("What is the weather in London?"))
    response = chat.sample()

    assert response.finish_reason == "REASON_TOOL_CALLS"
    assert response.role == "ROLE_ASSISTANT"
    assert response.tool_calls[0].function.name == "get_weather"
    assert response.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'
    assert response.content == "I am retrieving the weather for London in Celsius."


def test_function_calling_batch(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "units": {"type": "string"}},
                    "required": ["city", "units"],
                },
            )
        ],
    )
    chat.append(user("What is the weather in London?"))
    responses = chat.sample_batch(10)

    assert len(responses) == 10
    for r in responses:
        assert r.finish_reason == "REASON_TOOL_CALLS"
        assert r.role == "ROLE_ASSISTANT"
        assert r.tool_calls[0].function.name == "get_weather"
        assert r.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'


def test_function_calling_streaming(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "units": {"type": "string"}},
                    "required": ["city", "units"],
                },
            )
        ],
    )
    chat.append(user("What is the weather in London?"))
    stream = chat.stream()

    expected_chunks = [
        "I",
        " am",
        " retrieving",
        " the",
        " weather",
        " for",
        " London",
        " in",
        " Celsius",
        ".",
        "",  # Final chunk is a tool call which has no content set
    ]

    last_response = None
    for i, (response, chunk) in enumerate(stream):
        last_response = response
        assert chunk.content == expected_chunks[i]

    assert last_response is not None
    assert last_response.content == "I am retrieving the weather for London in Celsius."

    assert len(last_response.tool_calls) == 1
    assert last_response.finish_reason == "REASON_TOOL_CALLS"
    assert last_response.role == "ROLE_ASSISTANT"
    assert last_response.tool_calls[0].function.name == "get_weather"
    assert last_response.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'


def test_function_calling_streaming_batch(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={
                    "type": "object",
                    "properties": {"city": {"type": "string"}, "units": {"type": "string"}},
                    "required": ["city", "units"],
                },
            )
        ],
    )
    chat.append(user("What is the weather in London?"))
    stream = chat.stream_batch(2)

    chunks: Sequence[Sequence[Chunk]] = []
    last_response = None
    for r, chunk in stream:
        last_response = r
        chunks.append(chunk)

    assert chunks[0][0].content == "I"
    assert chunks[0][1].content == ""

    assert chunks[1][0].content == ""
    assert chunks[1][1].content == "I"

    assert chunks[2][0].content == " am"
    assert chunks[2][1].content == ""

    assert chunks[3][0].content == ""
    assert chunks[3][1].content == " am"

    assert chunks[4][0].content == " retrieving"
    assert chunks[4][1].content == ""

    assert chunks[5][0].content == ""
    assert chunks[5][1].content == " retrieving"

    assert chunks[6][0].content == " the"
    assert chunks[6][1].content == ""

    assert chunks[7][0].content == ""
    assert chunks[7][1].content == " the"

    assert chunks[8][0].content == " weather"
    assert chunks[8][1].content == ""

    assert chunks[9][0].content == ""
    assert chunks[9][1].content == " weather"

    assert chunks[10][0].content == " for"
    assert chunks[10][1].content == ""

    assert chunks[11][0].content == ""
    assert chunks[11][1].content == " for"

    assert chunks[12][0].content == " London"
    assert chunks[12][1].content == ""

    assert chunks[13][0].content == ""
    assert chunks[13][1].content == " London"

    assert chunks[14][0].content == " in"
    assert chunks[14][1].content == ""

    assert chunks[15][0].content == ""
    assert chunks[15][1].content == " in"

    assert chunks[16][0].content == " Celsius"
    assert chunks[16][1].content == ""

    assert chunks[17][0].content == ""
    assert chunks[17][1].content == " Celsius"

    assert chunks[18][0].content == "."
    assert chunks[18][1].content == ""

    # Final chunk is a tool call which has no content set
    assert chunks[19][0].content == ""
    assert chunks[19][1].content == ""

    assert last_response is not None

    for response in last_response:
        assert response.content == "I am retrieving the weather for London in Celsius."
        assert response.finish_reason == "REASON_TOOL_CALLS"
        assert response.role == "ROLE_ASSISTANT"
        assert response.tool_calls[0].function.name == "get_weather"
        assert response.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'


def test_structured_output(client: Client):
    class Weather(BaseModel):
        city: str
        units: str
        temperature: int

    chat = client.chat.create("grok-3-latest")
    chat.append(user("What is the weather in London?"))
    response, receipt = chat.parse(Weather)

    assert response.content == '{"city":"London","units":"C", "temperature": 20}'

    assert isinstance(receipt, Weather)
    assert receipt.city == "London"
    assert receipt.units == "C"
    assert receipt.temperature == 20


def test_deferred(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("What is the weather in London?"))
    response = chat.defer()

    assert response.content == "Hello, this is a test response!"


def test_deferred_batch(client: Client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("What is the weather in London?"))
    responses = chat.defer_batch(10)

    assert len(responses) == 10
    for r in responses:
        assert r.content == "Hello, this is a test response!"


def test_search(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )

    chat.append(user("Who is playing in the 2025 Champions League final?"))
    response = chat.sample()

    assert response.content == "Hello, this is a test response!"
    assert len(response.citations) == 3
    assert response.citations[0] == "test-citation-123"
    assert response.citations[1] == "test-citation-456"
    assert response.citations[2] == "test-citation-789"


def test_search_batch(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )

    chat.append(user("Who is playing in the 2025 Champions League final?"))
    responses = chat.sample_batch(10)

    # Citations are set on the response level, not on the choice level
    # Therefore, every sdk response (which is a particular choice) should have the same citations
    for r in responses:
        assert len(r.citations) == 3
        assert r.citations[0] == "test-citation-123"
        assert r.citations[1] == "test-citation-456"
        assert r.citations[2] == "test-citation-789"


def test_search_with_streaming(client: Client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )

    chat.append(user("Who is playing in the 2025 Champions League final?"))
    stream = chat.stream()

    chunks = []
    last_response = None
    for response, chunk in stream:
        last_response = response
        chunks.append(chunk)

    assert chunks[0].content == "Hello, "
    assert chunks[1].content == "this is "
    assert chunks[2].content == "a test "
    assert chunks[3].content == "response!"
    assert chunks[4].citations == ["test-citation-123", "test-citation-456", "test-citation-789"]

    assert last_response is not None
    assert last_response.content == "Hello, this is a test response!"
    assert len(last_response.citations) == 3
    assert last_response.citations[0] == "test-citation-123"
    assert last_response.citations[1] == "test-citation-456"
    assert last_response.citations[2] == "test-citation-789"


@pytest.mark.parametrize(
    "reasoning_effort",
    ["low", "high", chat_pb2.ReasoningEffort.EFFORT_LOW, chat_pb2.ReasoningEffort.EFFORT_HIGH],
)
def test_chat_create_with_reasoning(
    client: Client, reasoning_effort: Union[ReasoningEffort, "chat_pb2.ReasoningEffort"]
):
    chat = client.chat.create(
        "grok-3-mini",
        reasoning_effort=reasoning_effort,
    )

    chat_completion_request = chat.proto
    if reasoning_effort == "low":
        assert chat_completion_request.reasoning_effort == chat_pb2.ReasoningEffort.EFFORT_LOW
    elif reasoning_effort == "high":
        assert chat_completion_request.reasoning_effort == chat_pb2.ReasoningEffort.EFFORT_HIGH
    else:
        assert chat_completion_request.reasoning_effort == reasoning_effort


def test_chat_with_reasoning_invalid_value(client: Client):
    with pytest.raises(ValueError) as e:
        client.chat.create(
            "grok-3-mini",
            reasoning_effort="invalid",  # type: ignore
        )
    assert str(e.value) == "Invalid reasoning effort: invalid. Must be one of: ('low', 'high')"


def test_chat_create_with_tools(client: Client):
    chat = client.chat.create(
        "grok-3",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            ),
            tool(
                name="get_news",
                description="Get the news in a given city",
                parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            ),
        ],
    )

    chat_completion_request = chat.proto
    assert len(chat_completion_request.tools) == 2

    expected_weather_tool = chat_pb2.Tool(
        function=chat_pb2.Function(
            name="get_weather",
            description="Get the weather in a given city",
            parameters='{"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}',
        ),
    )

    expected_news_tool = chat_pb2.Tool(
        function=chat_pb2.Function(
            name="get_news",
            description="Get the news in a given city",
            parameters='{"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}',
        ),
    )

    assert chat_completion_request.tools[0] == expected_weather_tool
    assert chat_completion_request.tools[1] == expected_news_tool


@pytest.mark.parametrize(
    "tool_choice",
    [
        "auto",
        "none",
        "required",
        chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_AUTO),
        chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_NONE),
        chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_REQUIRED),
    ],
)
def test_chat_create_with_tool_mode(client: Client, tool_choice: Union[ToolMode, chat_pb2.ToolChoice]):
    chat = client.chat.create(
        "grok-3",
        tool_choice=tool_choice,
    )

    chat_completion_request = chat.proto
    if tool_choice == "auto":
        assert chat_completion_request.tool_choice == chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_AUTO)
    elif tool_choice == "none":
        assert chat_completion_request.tool_choice == chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_NONE)
    elif tool_choice == "required":
        assert chat_completion_request.tool_choice == chat_pb2.ToolChoice(mode=chat_pb2.TOOL_MODE_REQUIRED)
    else:
        assert chat_completion_request.tool_choice == tool_choice


def test_chat_create_with_required_tool(client: Client):
    chat = client.chat.create(
        "grok-3",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            ),
        ],
        tool_choice=required_tool("get_weather"),
    )

    chat_completion_request = chat.proto
    assert chat_completion_request.tool_choice == chat_pb2.ToolChoice(function_name="get_weather")


@pytest.mark.parametrize(
    "response_format",
    [
        "json_object",
        "text",
        chat_pb2.ResponseFormat(format_type=chat_pb2.FORMAT_TYPE_JSON_OBJECT),
        chat_pb2.ResponseFormat(format_type=chat_pb2.FORMAT_TYPE_TEXT),
        chat_pb2.ResponseFormat(
            format_type=chat_pb2.FORMAT_TYPE_JSON_SCHEMA,
            schema='{"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "number"}}}',
        ),
    ],
)
def test_chat_create_with_response_format(
    client: Client, response_format: Union[ResponseFormat, chat_pb2.ResponseFormat]
):
    chat = client.chat.create(
        "grok-3",
        response_format=response_format,
    )

    chat_completion_request = chat.proto
    if response_format == "json_object":
        assert chat_completion_request.response_format == chat_pb2.ResponseFormat(
            format_type=chat_pb2.FORMAT_TYPE_JSON_OBJECT
        )
    elif response_format == "text":
        assert chat_completion_request.response_format == chat_pb2.ResponseFormat(format_type=chat_pb2.FORMAT_TYPE_TEXT)
    else:
        assert chat_completion_request.response_format == response_format


def test_chat_create_with_response_format_invalid_value(client: Client):
    with pytest.raises(ValueError) as e:
        client.chat.create(
            "grok-3",
            response_format="invalid",  # type: ignore
        )
    assert str(e.value) == "Invalid response format: invalid. Must be one of: ('text', 'json_object')"


def test_chat_create_with_search_parameters(client: Client):
    from_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 1, 31, tzinfo=timezone.utc)

    chat = client.chat.create(
        "grok-3",
        search_parameters=SearchParameters(
            mode="on",
            from_date=from_date,
            to_date=to_date,
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"], safe_search=True),
                news_source(country="UK", safe_search=True),
                x_source(x_handles=["x_handle1", "x_handle2"]),
                rss_source(links=["https://example.com/rss1", "https://example.com/rss2"]),
            ],
            return_citations=True,
            max_search_results=10,
        ),
    )

    chat_completion_request = chat.proto

    assert chat_completion_request.search_parameters == chat_pb2.SearchParameters(
        mode=chat_pb2.SearchMode.ON_SEARCH_MODE,
        from_date=timestamp_pb2.Timestamp().FromDatetime(from_date),
        to_date=timestamp_pb2.Timestamp().FromDatetime(to_date),
        sources=[
            chat_pb2.Source(web=chat_pb2.WebSource(country="UK", excluded_websites=["excluded.com"], safe_search=True)),
            chat_pb2.Source(news=chat_pb2.NewsSource(country="UK", safe_search=True)),
            chat_pb2.Source(x=chat_pb2.XSource(x_handles=["x_handle1", "x_handle2"])),
            chat_pb2.Source(rss=chat_pb2.RssSource(links=["https://example.com/rss1", "https://example.com/rss2"])),
        ],
        return_citations=True,
        max_search_results=10,
    )


def test_chat_append(client: Client):
    chat = client.chat.create("grok-3")
    chat.append(system("You are a helpful assistant."))
    chat.append(user("What is the weather in London?"))
    chat.append(assistant("The weather in London is sunny."))

    expected_messages = [
        chat_pb2.Message(role=chat_pb2.ROLE_SYSTEM, content=[chat_pb2.Content(text="You are a helpful assistant.")]),
        chat_pb2.Message(role=chat_pb2.ROLE_USER, content=[chat_pb2.Content(text="What is the weather in London?")]),
        chat_pb2.Message(
            role=chat_pb2.ROLE_ASSISTANT, content=[chat_pb2.Content(text="The weather in London is sunny.")]
        ),
    ]

    assert len(chat.messages) == 3
    assert chat.messages == expected_messages


@pytest.mark.parametrize("detail", ["auto", "high", "low"])
def test_chat_append_with_images(client: Client, detail: ImageDetail):
    chat = client.chat.create("grok-3")
    chat.append(system("You are a helpful assistant."))
    chat.append(
        user(
            "Describe what you see in these images",
            image(image_url="https://example.com/image.jpg", detail=detail),
            image(image_url="https://example.com/image2.jpg", detail=detail),
        )
    )

    expected_image_detail = image_pb2.DETAIL_AUTO
    if detail == "high":
        expected_image_detail = image_pb2.DETAIL_HIGH
    elif detail == "low":
        expected_image_detail = image_pb2.DETAIL_LOW

    expected_messages = [
        chat_pb2.Message(role=chat_pb2.ROLE_SYSTEM, content=[chat_pb2.Content(text="You are a helpful assistant.")]),
        chat_pb2.Message(
            role=chat_pb2.ROLE_USER,
            content=[
                chat_pb2.Content(text="Describe what you see in these images"),
                chat_pb2.Content(
                    image_url=image_pb2.ImageUrlContent(
                        image_url="https://example.com/image.jpg", detail=expected_image_detail
                    )
                ),
                chat_pb2.Content(
                    image_url=image_pb2.ImageUrlContent(
                        image_url="https://example.com/image2.jpg", detail=expected_image_detail
                    )
                ),
            ],
        ),
    ]

    assert len(chat.messages) == 2
    assert chat.messages == expected_messages


def test_chat_append_response(client: Client):
    chat = client.chat.create("grok-3")
    chat.append(user("test message"))

    chat_completion_response = chat_pb2.GetChatCompletionResponse(
        choices=[
            chat_pb2.Choice(
                finish_reason=sample_pb2.FinishReason.REASON_STOP,
                index=0,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT, content="Hello, this is a test response!"
                ),
            )
        ]
    )

    response = Response(chat_completion_response, 0)

    chat.append(response)

    expected_messages = [
        chat_pb2.Message(role=chat_pb2.ROLE_USER, content=[chat_pb2.Content(text="test message")]),
        chat_pb2.Message(
            role=chat_pb2.ROLE_ASSISTANT, content=[chat_pb2.Content(text="Hello, this is a test response!")]
        ),
    ]

    assert len(chat.messages) == 2
    assert chat.messages == expected_messages


def test_chat_append_tool_result(client: Client):
    chat = client.chat.create("grok-3")
    chat.append(user("test message"))
    chat.append(tool_result("test result"))

    expected_messages = [
        chat_pb2.Message(role=chat_pb2.ROLE_USER, content=[chat_pb2.Content(text="test message")]),
        chat_pb2.Message(role=chat_pb2.ROLE_TOOL, content=[chat_pb2.Content(text="test result")]),
    ]

    assert len(chat.messages) == 2
    assert chat.messages == expected_messages
