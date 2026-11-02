import json
from unittest import mock

import pytest

from xai_sdk.aio.chat import Chat as AsyncChat
from xai_sdk.chat import user
from xai_sdk.proto import chat_pb2, sample_pb2
from xai_sdk.sync.chat import Chat


@pytest.fixture(params=['{"city": "Paris"}', '{"city":', ""])
def completion(request, monkeypatch):
    """Represent both complete and truncated model-generated tool arguments."""
    monkeypatch.delenv("XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES", raising=False)
    return chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                finish_reason=sample_pb2.REASON_MAX_LEN,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT,
                    tool_calls=[
                        chat_pb2.ToolCall(
                            id="call_1",
                            function=chat_pb2.FunctionCall(name="weather", arguments=request.param),
                        )
                    ],
                ),
            )
        ]
    )


def assert_telemetry_arguments(attributes, key, arguments):
    """Keep parsed JSON for valid arguments and raw text for incomplete JSON."""
    expected = {"city": "Paris"} if arguments == '{"city": "Paris"}' else arguments
    assert json.loads(attributes[key])[0]["function"]["arguments"] == expected


@mock.patch("xai_sdk.sync.chat.tracer")
def test_sample_preserves_tool_arguments_and_replays_response(tracer, completion):
    """Telemetry must not prevent receiving or replaying a truncated tool call."""
    stub = mock.Mock()
    stub.GetCompletion.return_value = completion
    chat = Chat(stub, None, None, model="grok-3", messages=[user("Weather?")])
    span = tracer.start_as_current_span.return_value.__enter__.return_value
    arguments = completion.outputs[0].message.tool_calls[0].function.arguments

    response = chat.sample()

    assert response.tool_calls[0].function.arguments == arguments
    assert_telemetry_arguments(span.set_attributes.call_args.args[0], "gen_ai.completion.0.tool_calls", arguments)

    chat.append(response)
    chat.sample()

    assert stub.GetCompletion.call_count == 2
    assert_telemetry_arguments(
        tracer.start_as_current_span.call_args.kwargs["attributes"], "gen_ai.prompt.1.tool_calls", arguments
    )


@mock.patch("xai_sdk.sync.chat.tracer")
def test_stream_finishes_with_incomplete_tool_arguments(tracer, completion):
    """A fully consumed stream must not raise during final telemetry collection."""
    output = completion.outputs[0]
    chunk = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                finish_reason=output.finish_reason,
                delta=chat_pb2.Delta(role=output.message.role, tool_calls=output.message.tool_calls),
            )
        ]
    )
    stub = mock.Mock()
    stub.GetCompletionChunk.return_value = iter([chunk])
    chat = Chat(stub, None, None, model="grok-3", messages=[user("Weather?")])

    responses = list(chat.stream())

    arguments = output.message.tool_calls[0].function.arguments
    assert responses[-1][0].tool_calls[0].function.arguments == arguments
    span = tracer.start_as_current_span.return_value.__enter__.return_value
    assert_telemetry_arguments(span.set_attributes.call_args.args[0], "gen_ai.completion.0.tool_calls", arguments)


@mock.patch("xai_sdk.sync.chat.tracer")
def test_disabled_sensitive_telemetry_omits_tool_arguments(tracer, completion, monkeypatch):
    """Raw and parsed arguments must both respect the sensitive-attribute opt-out."""
    monkeypatch.setenv("XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES", "1")
    stub = mock.Mock()
    stub.GetCompletion.return_value = completion
    chat = Chat(stub, None, None, model="grok-3", messages=[user("Weather?")])
    chat.append(chat.sample())
    chat.sample()

    span = tracer.start_as_current_span.return_value.__enter__.return_value
    assert "gen_ai.completion.0.tool_calls" not in span.set_attributes.call_args.args[0]
    assert "gen_ai.prompt.1.tool_calls" not in tracer.start_as_current_span.call_args.kwargs["attributes"]


@pytest.mark.asyncio
@mock.patch("xai_sdk.aio.chat.tracer")
async def test_async_sample_preserves_tool_arguments_and_replays_response(tracer, completion):
    """The async client must preserve the same response and replay behavior."""
    stub = mock.Mock()
    stub.GetCompletion = mock.AsyncMock(return_value=completion)
    chat = AsyncChat(stub, None, None, model="grok-3", messages=[user("Weather?")])
    span = tracer.start_as_current_span.return_value.__enter__.return_value
    arguments = completion.outputs[0].message.tool_calls[0].function.arguments

    response = await chat.sample()

    assert response.tool_calls[0].function.arguments == arguments
    assert_telemetry_arguments(span.set_attributes.call_args.args[0], "gen_ai.completion.0.tool_calls", arguments)

    chat.append(response)
    await chat.sample()

    assert stub.GetCompletion.await_count == 2
    assert_telemetry_arguments(
        tracer.start_as_current_span.call_args.kwargs["attributes"], "gen_ai.prompt.1.tool_calls", arguments
    )
