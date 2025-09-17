import json
from datetime import datetime, timezone
from typing import Union
from unittest import mock

import grpc
import pytest
import pytest_asyncio
from google.protobuf import timestamp_pb2
from opentelemetry.trace import SpanKind
from pydantic import BaseModel

from xai_sdk import AsyncClient
from xai_sdk.chat import (
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
def test_server_port():
    with server.run_test_server() as port:
        yield port


@pytest_asyncio.fixture(scope="session")
async def client(test_server_port: int):
    client = AsyncClient(api_key=server.API_KEY, api_host=f"localhost:{test_server_port}")
    yield client


@pytest.mark.asyncio(loop_scope="session")
async def test_unary_no_messages(client: AsyncClient):
    chat = client.chat.create("grok-3-latest")
    with pytest.raises(ValueError):
        await chat.sample()


@pytest.mark.asyncio(loop_scope="session")
async def test_unary(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    response = await chat.sample()

    assert response.content == "Hello, this is a test response!"


@pytest.mark.asyncio(loop_scope="session")
async def test_unary_batch(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    responses = await chat.sample_batch(10)

    assert len(responses) == 10

    for r in responses:
        assert r.content == "Hello, this is a test response!"


@pytest.mark.asyncio(loop_scope="session")
async def test_streaming(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    response = chat.stream()

    chunks = []
    last_response = None
    async for r, chunk in response:
        last_response = r
        chunks.append(chunk)

    assert chunks[0].content == "Hello, "
    assert chunks[1].content == "this is "
    assert chunks[2].content == "a test "
    assert chunks[3].content == "response!"

    assert last_response is not None
    assert last_response.content == "Hello, this is a test response!"


@pytest.mark.asyncio(loop_scope="session")
async def test_streaming_batch(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    response = chat.stream_batch(2)

    chunks = []
    last_response = None
    async for r, chunk in response:
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


@pytest.mark.asyncio(loop_scope="session")
async def test_deferred(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    response = await chat.defer()
    assert response.content == "Hello, this is a test response!"


@pytest.mark.asyncio(loop_scope="session")
async def test_deferred_batch(client):
    chat = client.chat.create("grok-3-latest")
    chat.append(user("test message"))
    responses = await chat.defer_batch(10)
    assert len(responses) == 10

    for r in responses:
        assert r.content == "Hello, this is a test response!"


@pytest.mark.asyncio(loop_scope="session")
async def test_function_calling(client):
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
    response = await chat.sample()

    assert response.finish_reason == "REASON_TOOL_CALLS"
    assert response.role == "ROLE_ASSISTANT"
    assert response.tool_calls[0].function.name == "get_weather"
    assert response.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'
    assert response.content == "I am retrieving the weather for London in Celsius."


@pytest.mark.asyncio(loop_scope="session")
async def test_function_calling_batch(client):
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
    responses = await chat.sample_batch(10)

    assert len(responses) == 10
    for r in responses:
        assert r.finish_reason == "REASON_TOOL_CALLS"
        assert r.role == "ROLE_ASSISTANT"
        assert r.tool_calls[0].function.name == "get_weather"
        assert r.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'
        assert r.content == "I am retrieving the weather for London in Celsius."


@pytest.mark.asyncio(loop_scope="session")
async def test_function_calling_streaming(client):
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
    i = 0
    async for response, chunk in stream:
        last_response = response
        assert chunk.content == expected_chunks[i]
        i += 1

    assert last_response is not None
    assert last_response.content == "I am retrieving the weather for London in Celsius."
    assert len(last_response.tool_calls) == 1
    assert last_response.finish_reason == "REASON_TOOL_CALLS"
    assert last_response.role == "ROLE_ASSISTANT"
    assert last_response.tool_calls[0].function.name == "get_weather"
    assert last_response.tool_calls[0].function.arguments == '{"city":"London","units":"C"}'


@pytest.mark.asyncio(loop_scope="session")
async def test_function_calling_streaming_batch(client):
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

    chunks = []
    last_response = None
    async for r, chunk in stream:
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


@pytest.mark.asyncio(loop_scope="session")
async def test_structured_output(client):
    class Weather(BaseModel):
        city: str
        units: str
        temperature: int

    chat = client.chat.create("grok-3-latest")
    chat.append(user("What is the weather in London?"))
    response, receipt = await chat.parse(Weather)

    assert response.content == '{"city":"London","units":"C", "temperature": 20}'
    assert isinstance(receipt, Weather)
    assert receipt.city == "London"
    assert receipt.units == "C"
    assert receipt.temperature == 20


@pytest.mark.asyncio(loop_scope="session")
async def test_search(client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(included_x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )
    chat.append(user("Who is playing in the 2025 Champions League final?"))
    response = await chat.sample()

    assert response.content == "Hello, this is a test response!"
    assert len(response.citations) == 3
    assert response.citations[0] == "test-citation-123"
    assert response.citations[1] == "test-citation-456"
    assert response.citations[2] == "test-citation-789"


@pytest.mark.asyncio(loop_scope="session")
async def test_search_batch(client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(included_x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )
    chat.append(user("Who is playing in the 2025 Champions League final?"))
    responses = await chat.sample_batch(10)

    for r in responses:
        assert len(r.citations) == 3
        assert r.citations[0] == "test-citation-123"
        assert r.citations[1] == "test-citation-456"
        assert r.citations[2] == "test-citation-789"


@pytest.mark.asyncio(loop_scope="session")
async def test_search_with_streaming(client):
    chat = client.chat.create(
        "grok-3-latest",
        search_parameters=SearchParameters(
            mode="on",
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"]),
                news_source(country="UK"),
                x_source(included_x_handles=["x_handle1", "x_handle2"]),
            ],
            return_citations=True,
        ),
    )
    chat.append(user("Who is playing in the 2025 Champions League final?"))
    stream = chat.stream()

    chunks = []
    last_response = None
    async for response, chunk in stream:
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


@pytest.mark.asyncio(loop_scope="session")
async def test_get_stored_completion_returns_single_completion(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()

    assert response.content == "Hello, this is a test response!"

    retrieved_response = await client.chat.get_stored_completion(response.id)
    assert len(retrieved_response) == 1
    retrieved_response = retrieved_response[0]
    assert retrieved_response.content == "Hello, this is a test response!"
    assert retrieved_response.request_settings == chat_pb2.RequestSettings(temperature=0.5, top_p=0.9)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_stored_completion_returns_multiple_completions(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(user("Hello, how are you?"))
    responses = await chat.sample_batch(3)
    assert len(responses) == 3
    for r in responses:
        assert r.content == "Hello, this is a test response!"

    # All response objects have the same response id so just use the first one
    retrieved_response = await client.chat.get_stored_completion(responses[0].id)
    assert len(retrieved_response) == 3
    for r in retrieved_response:
        assert r.content == "Hello, this is a test response!"
        assert r.request_settings == chat_pb2.RequestSettings(temperature=0.5, top_p=0.9)


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_stored_completion_deletes_single_completion(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=True)
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()

    assert response.content == "Hello, this is a test response!"

    deleted_id = await client.chat.delete_stored_completion(response.id)
    assert deleted_id == response.id

    with pytest.raises(grpc.RpcError) as e:
        await client.chat.get_stored_completion(response.id)

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Response not found"  # type: ignore


@pytest.mark.asyncio(loop_scope="session")
async def test_get_stored_completion_raises_not_found_error_if_response_not_found(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=False)
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()

    with pytest.raises(grpc.RpcError) as e:
        await client.chat.get_stored_completion(response.id)

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Response not found"  # type: ignore


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_stored_completion_raises_not_found_error_if_response_not_found(client: AsyncClient):
    chat = client.chat.create(model="grok-3", store_messages=False)
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()

    with pytest.raises(grpc.RpcError) as e:
        await client.chat.delete_stored_completion(response.id)

    assert e.value.code() == grpc.StatusCode.NOT_FOUND  # type: ignore
    assert e.value.details() == "Response not found"  # type: ignore


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_sample_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    response = await chat.sample()

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.sample grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.id": response.id,
        "gen_ai.response.model": response._proto.model,
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": response.system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": response.content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_sample_creates_span_with_correct_optional_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"

    # Set all possible request attributes
    chat = client.chat.create(
        model="grok-3",
        conversation_id=conversation_id,
        messages=[
            system("You are a helpful assistant."),
            user("Hello, how are you?"),
            assistant("I'm doing well, thank you!"),
        ],
        temperature=0.5,
        max_tokens=100,
        top_p=0.9,
        frequency_penalty=0.2,
        presence_penalty=0.1,
        seed=123,
        stop=["stop"],
        logprobs=True,
        top_logprobs=10,
        reasoning_effort="low",
        user="test-user",
        response_format="json_object",
        parallel_tool_calls=False,
        store_messages=True,
        previous_response_id="test-previous-response-id",
    )

    await chat.sample()

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "json_object",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": True,
        "gen_ai.request.frequency_penalty": 0.2,
        "gen_ai.request.presence_penalty": 0.1,
        "gen_ai.request.temperature": 0.5,
        "gen_ai.request.parallel_tool_calls": False,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.request.max_tokens": 100,
        "gen_ai.request.seed": 123,
        "gen_ai.request.stop_sequences": ["stop"],
        "gen_ai.request.top_p": 0.9,
        "gen_ai.request.top_logprobs": 10,
        "gen_ai.request.reasoning_effort": "low",
        "user_id": "test-user",
        # All prompt messages
        "gen_ai.prompt.0.role": "system",
        "gen_ai.prompt.0.content": "You are a helpful assistant.",
        "gen_ai.prompt.1.role": "user",
        "gen_ai.prompt.1.content": "Hello, how are you?",
        "gen_ai.prompt.2.role": "assistant",
        "gen_ai.prompt.2.content": "I'm doing well, thank you!",
        "gen_ai.request.store_messages": True,
        "gen_ai.request.previous_response_id": "test-previous-response-id",
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.sample grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_sample_batch_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    responses = await chat.sample_batch(3)

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.sample_batch grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    assert len(responses) == 3
    expected_response_attributes = {
        "gen_ai.response.id": responses[0].id,
        "gen_ai.response.model": responses[0]._proto.model,
        "gen_ai.usage.input_tokens": responses[0].usage.prompt_tokens,
        "gen_ai.usage.output_tokens": responses[0].usage.completion_tokens,
        "gen_ai.usage.total_tokens": responses[0].usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": responses[0].usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": responses[0].usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": responses[0].usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": responses[0].usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": responses[0].system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason for response in responses],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": responses[0].content,
        "gen_ai.completion.1.role": "assistant",
        "gen_ai.completion.1.content": responses[1].content,
        "gen_ai.completion.2.role": "assistant",
        "gen_ai.completion.2.content": responses[2].content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_stream_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    chunks_received = []
    final_response = None
    async for response, chunk in chat.stream():
        chunks_received.append(chunk)
        final_response = response

    assert len(chunks_received) > 0
    assert final_response is not None
    assert final_response.content == "Hello, this is a test response!"

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.stream grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    mock_span.set_attribute.assert_called_once_with("gen_ai.completion.start_time", mock.ANY)

    expected_response_attributes = {
        "gen_ai.response.id": final_response.id,
        "gen_ai.response.model": final_response._proto.model,
        "gen_ai.usage.input_tokens": final_response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": final_response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": final_response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": final_response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": final_response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": final_response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": final_response.usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": final_response.system_fingerprint,
        "gen_ai.response.finish_reasons": [final_response.finish_reason],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": final_response.content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_stream_batch_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    chunks_received = []
    final_responses = None
    async for responses, chunks in chat.stream_batch(2):
        chunks_received.extend(chunks)
        final_responses = responses

    assert len(chunks_received) > 0
    assert final_responses is not None
    assert len(final_responses) == 2
    assert final_responses[0].content == "Hello, this is a test response!"

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.stream_batch grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    mock_span.set_attribute.assert_called_once_with("gen_ai.completion.start_time", mock.ANY)

    expected_response_attributes = {
        "gen_ai.response.id": final_responses[0].id,
        "gen_ai.response.model": final_responses[0]._proto.model,
        "gen_ai.usage.input_tokens": final_responses[0].usage.prompt_tokens,
        "gen_ai.usage.output_tokens": final_responses[0].usage.completion_tokens,
        "gen_ai.usage.total_tokens": final_responses[0].usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": final_responses[0].usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": final_responses[0].usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": final_responses[0].usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": final_responses[0].usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": final_responses[0].system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason for response in final_responses],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": final_responses[0].content,
        "gen_ai.completion.1.role": "assistant",
        "gen_ai.completion.1.content": final_responses[1].content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_parse_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    from pydantic import BaseModel

    class TestResponse(BaseModel):
        city: str
        units: str
        temperature: int

    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("What's the weather in London?"))

    response, parsed = await chat.parse(TestResponse)

    assert response is not None
    assert parsed is not None
    assert isinstance(parsed, TestResponse)
    assert parsed.city == "London"
    assert parsed.units == "C"
    assert parsed.temperature == 20

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "json_schema",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "What's the weather in London?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.parse grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.id": response.id,
        "gen_ai.response.model": response._proto.model,
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": response.system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": response.content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_defer_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    response = await chat.defer()

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.defer grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.id": response.id,
        "gen_ai.response.model": response._proto.model,
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": response.system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": response.content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_defer_batch_creates_span_with_correct_attributes(mock_tracer: mock.MagicMock, client: AsyncClient):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    responses = await chat.defer_batch(3)

    assert len(responses) == 3
    for response in responses:
        assert response.content == "Hello, this is a test response!"

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "Hello, how are you?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.defer_batch grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.id": responses[0].id,
        "gen_ai.response.model": responses[0]._proto.model,
        "gen_ai.usage.input_tokens": responses[0].usage.prompt_tokens,
        "gen_ai.usage.output_tokens": responses[0].usage.completion_tokens,
        "gen_ai.usage.total_tokens": responses[0].usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": responses[0].usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": responses[0].usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": responses[0].usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": responses[0].usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": responses[0].system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason for response in responses],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": responses[0].content,
        "gen_ai.completion.1.role": "assistant",
        "gen_ai.completion.1.content": responses[1].content,
        "gen_ai.completion.2.role": "assistant",
        "gen_ai.completion.2.content": responses[2].content,
    }
    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@pytest.mark.asyncio(loop_scope="session")
@mock.patch("xai_sdk.aio.chat.tracer")
async def test_chat_with_function_calling_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: AsyncClient
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(
        model="grok-3",
        conversation_id=conversation_id,
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            ),
        ],
    )
    chat.append(user("What's the weather in London?"))
    response = await chat.sample()

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "What's the weather in London?",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.sample grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )

    expected_response_attributes = {
        "gen_ai.response.id": response.id,
        "gen_ai.response.model": response._proto.model,
        "gen_ai.usage.input_tokens": response.usage.prompt_tokens,
        "gen_ai.usage.output_tokens": response.usage.completion_tokens,
        "gen_ai.usage.total_tokens": response.usage.total_tokens,
        "gen_ai.usage.reasoning_tokens": response.usage.reasoning_tokens,
        "gen_ai.usage.cached_prompt_text_tokens": response.usage.cached_prompt_text_tokens,
        "gen_ai.usage.prompt_text_tokens": response.usage.prompt_text_tokens,
        "gen_ai.usage.prompt_image_tokens": response.usage.prompt_image_tokens,
        "gen_ai.response.system_fingerprint": response.system_fingerprint,
        "gen_ai.response.finish_reasons": [response.finish_reason],
        "gen_ai.completion.0.role": "assistant",
        "gen_ai.completion.0.content": response.content,
        "gen_ai.completion.0.tool_calls": json.dumps(
            [
                {
                    "id": "test-tool-call",
                    "type": "function",
                    "function": {"name": "get_weather", "arguments": {"city": "London", "units": "C"}},
                }
            ]
        ),
    }

    mock_span.set_attributes.assert_called_once_with(expected_response_attributes)


@pytest.mark.asyncio(loop_scope="session")
@mock.patch("xai_sdk.aio.chat.tracer")
async def test_chat_with_function_call_result_creates_span_with_correct_attributes(
    mock_tracer: mock.MagicMock, client: AsyncClient
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(
        model="grok-3",
        conversation_id=conversation_id,
    )
    chat.append(user("What's the weather in London?"))
    chat.append(
        chat_pb2.Message(
            role=chat_pb2.ROLE_ASSISTANT,
            content=[chat_pb2.Content(text="I am retrieving the weather for London in Celsius.")],
            tool_calls=[
                chat_pb2.ToolCall(
                    id="test-tool-call",
                    function=chat_pb2.FunctionCall(name="get_weather", arguments='{"city":"London","units":"C"}'),
                )
            ],
        )
    )
    chat.append(tool_result("The weather in London is 20 degrees Fahrenheit."))
    await chat.sample()

    expected_request_attributes = {
        "gen_ai.operation.name": "chat",
        "gen_ai.system": "xai",
        "gen_ai.output.type": "text",
        "gen_ai.request.model": "grok-3",
        "gen_ai.request.logprobs": False,
        "gen_ai.request.frequency_penalty": 0.0,
        "gen_ai.request.presence_penalty": 0.0,
        "gen_ai.request.temperature": 1.0,
        "gen_ai.request.parallel_tool_calls": True,
        "server.port": 443,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.prompt.0.role": "user",
        "gen_ai.prompt.0.content": "What's the weather in London?",
        "gen_ai.prompt.1.role": "assistant",
        "gen_ai.prompt.1.content": "I am retrieving the weather for London in Celsius.",
        "gen_ai.prompt.1.tool_calls": json.dumps(
            [
                {
                    "id": "test-tool-call",
                    "type": "function",
                    "function": {"name": "get_weather", "arguments": {"city": "London", "units": "C"}},
                }
            ]
        ),
        "gen_ai.prompt.2.role": "tool",
        "gen_ai.prompt.2.content": "The weather in London is 20 degrees Fahrenheit.",
        "gen_ai.request.store_messages": False,
    }

    mock_tracer.start_as_current_span.assert_called_once_with(
        name="chat.sample grok-3",
        kind=SpanKind.CLIENT,
        attributes=expected_request_attributes,
    )


@mock.patch("xai_sdk.aio.chat.tracer")
@pytest.mark.asyncio(loop_scope="session")
async def test_multi_turn_conversation_creates_multiple_spans_with_same_conversation_id(
    mock_tracer: mock.MagicMock, client: AsyncClient
):
    mock_span = mock.MagicMock()
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

    conversation_id = "test-conversation-id"
    chat = client.chat.create(model="grok-3", conversation_id=conversation_id)
    chat.append(user("Hello, how are you?"))

    # Sample twice to create two spans which should have the same conversation_id
    await chat.sample()
    chat.append(user("Hi again"))
    await chat.sample()

    assert mock_tracer.start_as_current_span.call_count == 2
    call_args_list = mock_tracer.start_as_current_span.call_args_list
    first_call_attributes = call_args_list[0].kwargs["attributes"]
    assert first_call_attributes["gen_ai.conversation.id"] == conversation_id
    second_call_attributes = call_args_list[1].kwargs["attributes"]
    assert second_call_attributes["gen_ai.conversation.id"] == conversation_id


@pytest.mark.parametrize(
    "reasoning_effort",
    ["low", "high", chat_pb2.ReasoningEffort.EFFORT_LOW, chat_pb2.ReasoningEffort.EFFORT_HIGH],
)
def test_chat_create_with_reasoning(
    client: AsyncClient, reasoning_effort: Union[ReasoningEffort, "chat_pb2.ReasoningEffort"]
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


def test_chat_with_reasoning_invalid_value(client: AsyncClient):
    with pytest.raises(ValueError) as e:
        client.chat.create(
            "grok-3-mini",
            reasoning_effort="invalid",  # type: ignore
        )
    assert str(e.value) == "Invalid reasoning effort: invalid. Must be one of: ('low', 'high')"


def test_chat_create_with_tools(client: AsyncClient):
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
def test_chat_create_with_tool_mode(client: AsyncClient, tool_choice: Union[ToolMode, chat_pb2.ToolChoice]):
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


def test_chat_create_with_required_tool(client: AsyncClient):
    chat = client.chat.create(
        "grok-3",
        tools=[
            tool(
                name="get_weather",
                description="Get the weather in a given city",
                parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
            ),
        ],
        tool_choice=required_tool(name="get_weather"),
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
    client: AsyncClient, response_format: Union[ResponseFormat, chat_pb2.ResponseFormat]
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


def test_chat_create_with_response_format_invalid_value(client: AsyncClient):
    with pytest.raises(ValueError) as e:
        client.chat.create(
            "grok-3",
            response_format="invalid",  # type: ignore
        )
    assert str(e.value) == "Invalid response format: invalid. Must be one of: ('text', 'json_object')"


def test_chat_create_with_search_parameters(client: AsyncClient):
    from_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 1, 31, tzinfo=timezone.utc)

    expected_from_date_pb = timestamp_pb2.Timestamp()
    expected_from_date_pb.FromDatetime(from_date)

    expected_to_date_pb = timestamp_pb2.Timestamp()
    expected_to_date_pb.FromDatetime(to_date)

    chat = client.chat.create(
        "grok-3",
        search_parameters=SearchParameters(
            mode="on",
            from_date=from_date,
            to_date=to_date,
            sources=[
                web_source(country="UK", excluded_websites=["excluded.com"], safe_search=True),
                news_source(country="UK", safe_search=True),
                x_source(
                    included_x_handles=["x_handle1", "x_handle2"],
                    post_favorite_count=1000,
                    post_view_count=1000,
                ),
                rss_source(links=["https://example.com/rss1", "https://example.com/rss2"]),
            ],
            return_citations=True,
            max_search_results=10,
        ),
    )

    chat_completion_request = chat.proto

    assert chat_completion_request.search_parameters == chat_pb2.SearchParameters(
        mode=chat_pb2.SearchMode.ON_SEARCH_MODE,
        from_date=expected_from_date_pb,
        to_date=expected_to_date_pb,
        sources=[
            chat_pb2.Source(web=chat_pb2.WebSource(country="UK", excluded_websites=["excluded.com"], safe_search=True)),
            chat_pb2.Source(news=chat_pb2.NewsSource(country="UK", safe_search=True)),
            chat_pb2.Source(
                x=chat_pb2.XSource(
                    included_x_handles=["x_handle1", "x_handle2"],
                    post_favorite_count=1000,
                    post_view_count=1000,
                )
            ),
            chat_pb2.Source(rss=chat_pb2.RssSource(links=["https://example.com/rss1", "https://example.com/rss2"])),
        ],
        return_citations=True,
        max_search_results=10,
    )


def test_chat_create_with_search_parameters_proto(client: AsyncClient):
    from_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 1, 31, tzinfo=timezone.utc)

    expected_from_date_pb = timestamp_pb2.Timestamp()
    expected_from_date_pb.FromDatetime(from_date)

    expected_to_date_pb = timestamp_pb2.Timestamp()
    expected_to_date_pb.FromDatetime(to_date)

    search_parameters_pb = chat_pb2.SearchParameters(
        mode=chat_pb2.SearchMode.ON_SEARCH_MODE,
        from_date=expected_from_date_pb,
        to_date=expected_to_date_pb,
        sources=[
            chat_pb2.Source(web=chat_pb2.WebSource(country="UK", excluded_websites=["excluded.com"], safe_search=True)),
            chat_pb2.Source(news=chat_pb2.NewsSource(country="UK", safe_search=True)),
            chat_pb2.Source(
                x=chat_pb2.XSource(
                    included_x_handles=["x_handle1", "x_handle2"],
                    post_favorite_count=1000,
                    post_view_count=1000,
                )
            ),
            chat_pb2.Source(rss=chat_pb2.RssSource(links=["https://example.com/rss1", "https://example.com/rss2"])),
        ],
        return_citations=True,
        max_search_results=10,
    )

    chat = client.chat.create(
        "grok-3",
        search_parameters=search_parameters_pb,
    )

    assert chat.proto.search_parameters == search_parameters_pb


def test_chat_append(client: AsyncClient):
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
def test_chat_append_with_images(client: AsyncClient, detail: ImageDetail):
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


def test_chat_append_response(client: AsyncClient):
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


def test_chat_append_tool_result(client: AsyncClient):
    chat = client.chat.create("grok-3")
    chat.append(user("test message"))
    chat.append(tool_result("test result"))

    expected_messages = [
        chat_pb2.Message(role=chat_pb2.ROLE_USER, content=[chat_pb2.Content(text="test message")]),
        chat_pb2.Message(role=chat_pb2.ROLE_TOOL, content=[chat_pb2.Content(text="test result")]),
    ]

    assert len(chat.messages) == 2
    assert chat.messages == expected_messages
