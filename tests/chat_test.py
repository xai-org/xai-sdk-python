import pytest

from xai_sdk.chat import CompactContextResponse, Response, _agent_count_to_proto, developer
from xai_sdk.proto import chat_pb2, sample_pb2, usage_pb2
from xai_sdk.tools import get_tool_call_type


def test_lazy_buffering_accumulates_chunks():
    """Test that chunks accumulate in buffers without immediate concatenation."""
    # Create a response with an empty output
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(role=chat_pb2.ROLE_ASSISTANT),
            )
        ]
    )
    response = Response(response_pb, 0)

    # Create chunks with content
    chunk1 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Hello, ",
                    reasoning_content="Step 1: ",
                    encrypted_content="Enc1: ",
                ),
            )
        ]
    )
    chunk2 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="world!",
                    reasoning_content="Step 2.",
                    encrypted_content="Enc2.",
                ),
            )
        ]
    )

    # Process chunks
    response.process_chunk(chunk1)
    response.process_chunk(chunk2)

    # Verify buffers contain individual chunks (not yet concatenated)
    assert response._content_buffers[0] == ["Hello, ", "world!"]
    assert response._reasoning_content_buffers[0] == ["Step 1: ", "Step 2."]
    assert response._encrypted_content_buffers[0] == ["Enc1: ", "Enc2."]

    # Verify proto is in sync
    assert response._proto_in_sync is False

    # Accessing content should trigger sync
    assert response.content == "Hello, world!"
    assert response.reasoning_content == "Step 1: Step 2."
    assert response.encrypted_content == "Enc1: Enc2."


def test_lazy_buffering_sync_only_on_content_access():
    """Test that sync only happens when content properties are accessed."""
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[chat_pb2.CompletionOutput(index=0, finish_reason=sample_pb2.REASON_STOP)]
    )
    response = Response(response_pb, 0)

    # Process a chunk
    chunk = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Test content",
                ),
                finish_reason=sample_pb2.REASON_STOP,
            )
        ]
    )
    response.process_chunk(chunk)

    # Verify buffer has content but proto doesn't yet
    assert response._content_buffers[0] == ["Test content"]
    assert response._proto.outputs[0].message.content == ""

    # Accessing finish_reason (non-content property) should not trigger sync
    _ = response.finish_reason
    assert response._proto.outputs[0].message.content == ""

    # Accessing content should trigger sync
    content = response.content
    assert content == "Test content"
    assert response._proto.outputs[0].message.content == "Test content"

    # After sync, buffer should contain the consolidated content
    assert response._content_buffers[0] == ["Test content"]


def test_lazy_buffering_multiple_indices():
    """Test that lazy buffering works correctly with multiple output indices."""
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(index=0),
            chat_pb2.CompletionOutput(index=1),
        ]
    )
    response = Response(response_pb, None)  # None means all indices

    # Process chunks for different indices
    chunk1 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Response 0 part 1, ",
                ),
            ),
            chat_pb2.CompletionOutputChunk(
                index=1,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Response 1 part 1, ",
                ),
            ),
        ]
    )
    chunk2 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(content="part 2"),
            ),
            chat_pb2.CompletionOutputChunk(
                index=1,
                delta=chat_pb2.Delta(content="part 2"),
            ),
        ]
    )

    response.process_chunk(chunk1)
    response.process_chunk(chunk2)

    # Verify buffers for each index
    assert response._content_buffers[0] == ["Response 0 part 1, ", "part 2"]
    assert response._content_buffers[1] == ["Response 1 part 1, ", "part 2"]

    # Trigger sync and verify
    assert response._proto.outputs[0].message.content == ""  # Not synced yet
    _ = response.content  # Triggers sync
    assert response._proto.outputs[0].message.content == "Response 0 part 1, part 2"
    assert response._proto.outputs[1].message.content == "Response 1 part 1, part 2"


def test_lazy_buffering_empty_chunks():
    """Test that empty chunks don't cause issues."""
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(role=chat_pb2.ROLE_ASSISTANT),
            )
        ]
    )
    response = Response(response_pb, 0)

    # Process chunk with empty content
    chunk = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="",  # Empty
                ),
            )
        ]
    )
    response.process_chunk(chunk)

    # Empty content shouldn't be added to buffer
    assert 0 not in response._content_buffers or response._content_buffers[0] == []

    # Add non-empty chunk
    chunk2 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(role=chat_pb2.ROLE_ASSISTANT, content="Hello"),
            )
        ]
    )
    response.process_chunk(chunk2)

    assert response._content_buffers[0] == ["Hello"]
    assert response.content == "Hello"


def test_lazy_buffering_proto_property_triggers_sync():
    """Test that accessing the proto property triggers sync."""
    response_pb = chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput(index=0)])
    response = Response(response_pb, 0)

    # Process chunk
    chunk = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Test",
                ),
            )
        ]
    )
    response.process_chunk(chunk)

    # Verify buffer has content but proto doesn't yet
    assert response._content_buffers[0] == ["Test"]
    assert response._proto.outputs[0].message.content == ""

    # Accessing proto property should trigger sync
    proto = response.proto
    assert proto.outputs[0].message.content == "Test"


def test_lazy_buffering_with_streaming():
    """Test lazy buffering with a simulated streaming scenario."""
    response_pb = chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput(index=0)])
    response = Response(response_pb, 0)

    # Simulate multiple streaming chunks
    chunks_data = ["The ", "quick ", "brown ", "fox ", "jumps"]
    for chunk_text in chunks_data:
        chunk = chat_pb2.GetChatCompletionChunk(
            outputs=[
                chat_pb2.CompletionOutputChunk(
                    index=0,
                    delta=chat_pb2.Delta(
                        role=chat_pb2.ROLE_ASSISTANT,
                        content=chunk_text,
                    ),
                )
            ]
        )
        response.process_chunk(chunk)

    # Verify all chunks are in the buffer
    assert response._content_buffers[0] == chunks_data

    # Final content should be correctly concatenated
    assert response.content == "The quick brown fox jumps"

    # After first sync, buffer should contain consolidated string
    assert response._content_buffers[0] == ["The quick brown fox jumps"]


def test_get_tool_call_type():
    """Test the get_tool_call_type function."""
    server_side_tool_call = chat_pb2.ToolCall(type=chat_pb2.ToolCallType.TOOL_CALL_TYPE_WEB_SEARCH_TOOL)
    assert get_tool_call_type(server_side_tool_call) == "web_search_tool"
    client_side_tool_call = chat_pb2.ToolCall(type=chat_pb2.ToolCallType.TOOL_CALL_TYPE_CLIENT_SIDE_TOOL)
    assert get_tool_call_type(client_side_tool_call) == "client_side_tool"


def test_response_debug_output():
    """Test that Response.debug_output returns the debug output from the response proto."""
    # Create a debug output with some test data
    debug_output = chat_pb2.DebugOutput(
        attempts=3,
        request="test request",
        prompt="test prompt",
        responses=["response 1", "response 2"],
        chunks=["chunk 1", "chunk 2"],
        cache_read_count=5,
        lb_address="test.lb.address",
        sampler_tag="test_sampler",
    )

    # Create a response with debug output
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Test response",
                ),
            )
        ],
        debug_output=debug_output,
    )
    response = Response(response_pb, 0)

    # Verify debug_output property returns the correct debug output
    assert response.debug_output == debug_output
    assert response.debug_output.attempts == 3
    assert response.debug_output.request == "test request"
    assert response.debug_output.prompt == "test prompt"
    assert list(response.debug_output.responses) == ["response 1", "response 2"]
    assert list(response.debug_output.chunks) == ["chunk 1", "chunk 2"]
    assert response.debug_output.cache_read_count == 5
    assert response.debug_output.lb_address == "test.lb.address"
    assert response.debug_output.sampler_tag == "test_sampler"


def test_chunk_debug_output():
    """Test that Chunk.debug_output returns the debug output from the chunk proto."""
    from xai_sdk.chat import Chunk

    # Create a debug output with some test data
    debug_output = chat_pb2.DebugOutput(
        attempts=2,
        prompt="chunk prompt",
        chunks=["chunk data"],
        lb_address="chunk.lb.address",
    )

    # Create a chunk with debug output
    chunk_pb = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Test chunk",
                ),
            )
        ],
        debug_output=debug_output,
    )
    chunk = Chunk(chunk_pb, 0)

    # Verify debug_output property returns the correct debug output
    assert chunk.debug_output == debug_output
    assert chunk.debug_output.attempts == 2
    assert chunk.debug_output.prompt == "chunk prompt"
    assert list(chunk.debug_output.chunks) == ["chunk data"]
    assert chunk.debug_output.lb_address == "chunk.lb.address"


def test_response_inline_citations():
    """Test that Response.inline_citations returns the inline citations from all assistant outputs."""
    # Create inline citations
    web_citation = chat_pb2.InlineCitation(
        id="1",
        start_index=10,
        end_index=35,
        web_citation=chat_pb2.WebCitation(url="https://example.com/article"),
    )
    x_citation = chat_pb2.InlineCitation(
        id="2",
        start_index=50,
        end_index=80,
        x_citation=chat_pb2.XCitation(url="https://x.com/user/status/123"),
    )

    # Create a response with inline citations in the message
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Test response with citations [[1]](https://example.com) and [[2]](https://x.com)",
                    citations=[web_citation, x_citation],
                ),
            ),
        ],
    )
    response = Response(response_pb, None)  # None means all outputs

    # Verify inline_citations property returns all citations from assistant outputs
    inline_citations = response.inline_citations
    assert len(inline_citations) == 2

    # Verify first citation (web)
    assert inline_citations[0].id == "1"
    assert inline_citations[0].start_index == 10
    assert inline_citations[0].end_index == 35
    assert inline_citations[0].HasField("web_citation")
    assert inline_citations[0].web_citation.url == "https://example.com/article"

    # Verify second citation (X)
    assert inline_citations[1].id == "2"
    assert inline_citations[1].start_index == 50
    assert inline_citations[1].end_index == 80
    assert inline_citations[1].HasField("x_citation")
    assert inline_citations[1].x_citation.url == "https://x.com/user/status/123"


def test_response_inline_citations_excludes_non_assistant_outputs():
    """Test that inline_citations only returns citations from assistant role outputs."""
    assistant_citation = chat_pb2.InlineCitation(
        id="1",
        start_index=0,
        end_index=20,
        web_citation=chat_pb2.WebCitation(url="https://assistant.example.com"),
    )

    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Assistant response",
                    citations=[assistant_citation],
                ),
            ),
            chat_pb2.CompletionOutput(
                index=1,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_TOOL,
                    content="Tool response",
                ),
            ),
        ],
    )
    response = Response(response_pb, None)

    # Should only return the assistant citation, not the tool citation
    inline_citations = response.inline_citations
    assert len(inline_citations) == 1
    assert inline_citations[0].id == "1"
    assert inline_citations[0].web_citation.url == "https://assistant.example.com"


def test_chunk_inline_citations():
    """Test that Chunk.inline_citations returns the inline citations from the delta."""
    from xai_sdk.chat import Chunk

    # Create inline citations for the chunk
    citation1 = chat_pb2.InlineCitation(
        id="1",
        start_index=5,
        end_index=25,
        web_citation=chat_pb2.WebCitation(url="https://example.com"),
    )
    citation2 = chat_pb2.InlineCitation(
        id="2",
        start_index=30,
        end_index=55,
        x_citation=chat_pb2.XCitation(url="https://x.com/status/456"),
    )

    # Create a chunk with inline citations
    chunk_pb = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Some content [[1]](url) more [[2]](url)",
                    citations=[citation1, citation2],
                ),
            )
        ],
    )
    chunk = Chunk(chunk_pb, 0)

    # Verify inline_citations property
    inline_citations = chunk.inline_citations
    assert len(inline_citations) == 2
    assert inline_citations[0].id == "1"
    assert inline_citations[0].web_citation.url == "https://example.com"
    assert inline_citations[1].id == "2"
    assert inline_citations[1].x_citation.url == "https://x.com/status/456"


def test_chunk_inline_citations_multiple_outputs():
    """Test that Chunk.inline_citations aggregates citations from multiple assistant outputs."""
    from xai_sdk.chat import Chunk

    citation1 = chat_pb2.InlineCitation(
        id="1",
        start_index=0,
        end_index=10,
        web_citation=chat_pb2.WebCitation(url="https://first.example.com"),
    )
    citation2 = chat_pb2.InlineCitation(
        id="2",
        start_index=0,
        end_index=10,
        web_citation=chat_pb2.WebCitation(url="https://second.example.com"),
    )

    chunk_pb = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="First output",
                    citations=[citation1],
                ),
            ),
            chat_pb2.CompletionOutputChunk(
                index=1,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Second output",
                    citations=[citation2],
                ),
            ),
        ],
    )
    chunk = Chunk(chunk_pb, None)  # None means all outputs

    # Should aggregate citations from all assistant outputs
    inline_citations = chunk.inline_citations
    assert len(inline_citations) == 2
    assert inline_citations[0].web_citation.url == "https://first.example.com"
    assert inline_citations[1].web_citation.url == "https://second.example.com"


def test_process_chunk_accumulates_inline_citations():
    """Test that process_chunk correctly accumulates inline citations on the response."""
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(role=chat_pb2.ROLE_ASSISTANT),
            )
        ]
    )
    response = Response(response_pb, 0)

    # First chunk with citation
    citation1 = chat_pb2.InlineCitation(
        id="1",
        start_index=10,
        end_index=30,
        web_citation=chat_pb2.WebCitation(url="https://first.example.com"),
    )
    chunk1 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="First part [[1]](url)",
                    citations=[citation1],
                ),
            )
        ]
    )

    # Second chunk with another citation
    citation2 = chat_pb2.InlineCitation(
        id="2",
        start_index=50,
        end_index=70,
        x_citation=chat_pb2.XCitation(url="https://x.com/status/789"),
    )
    chunk2 = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content=" second part [[2]](url)",
                    citations=[citation2],
                ),
            )
        ]
    )

    # Process both chunks
    response.process_chunk(chunk1)
    response.process_chunk(chunk2)

    # Verify inline citations are accumulated on the response
    inline_citations = response.inline_citations
    assert len(inline_citations) == 2
    assert inline_citations[0].id == "1"
    assert inline_citations[0].web_citation.url == "https://first.example.com"
    assert inline_citations[1].id == "2"
    assert inline_citations[1].x_citation.url == "https://x.com/status/789"


def test_response_inline_citations_empty():
    """Test that inline_citations returns empty list when no citations present."""
    response_pb = chat_pb2.GetChatCompletionResponse(
        outputs=[
            chat_pb2.CompletionOutput(
                index=0,
                message=chat_pb2.CompletionMessage(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Response without citations",
                ),
            )
        ],
    )
    response = Response(response_pb, 0)

    assert response.inline_citations == []


def test_chunk_inline_citations_empty():
    """Test that Chunk.inline_citations returns empty list when no citations present."""
    from xai_sdk.chat import Chunk

    chunk_pb = chat_pb2.GetChatCompletionChunk(
        outputs=[
            chat_pb2.CompletionOutputChunk(
                index=0,
                delta=chat_pb2.Delta(
                    role=chat_pb2.ROLE_ASSISTANT,
                    content="Content without citations",
                ),
            )
        ],
    )
    chunk = Chunk(chunk_pb, 0)

    assert chunk.inline_citations == []


def test_web_search_user_location():
    """Test that web_search util function correctly sets user_location city and timezone fields."""
    from xai_sdk.tools import web_search

    # Create a web_search tool with city and timezone
    tool = web_search(
        user_location_city="San Francisco",
        user_location_timezone="America/Los_Angeles",
    )

    # Verify the tool is a chat_pb2.Tool
    assert isinstance(tool, chat_pb2.Tool)

    # Verify the web_search field is set
    assert tool.HasField("web_search")

    # Verify user_location fields are set correctly
    assert tool.web_search.user_location.city == "San Francisco"
    assert tool.web_search.user_location.timezone == "America/Los_Angeles"


def test_web_search_enable_image_search():
    """Test that web_search util function correctly sets enable_image_search."""
    from xai_sdk.tools import web_search

    tool = web_search(enable_image_search=True)

    assert isinstance(tool, chat_pb2.Tool)
    assert tool.HasField("web_search")
    assert tool.web_search.enable_image_search is True


def test_server_side_tool_image_search_enum():
    assert usage_pb2.SERVER_SIDE_TOOL_IMAGE_SEARCH == 10
    assert usage_pb2.ServerSideTool.Name(usage_pb2.SERVER_SIDE_TOOL_IMAGE_SEARCH) == "SERVER_SIDE_TOOL_IMAGE_SEARCH"


def test_mcp_tool_minimal():
    """Test that mcp() creates a tool with only server_url set."""
    from xai_sdk.tools import mcp

    tool = mcp(server_url="https://mcp.example.com")

    assert isinstance(tool, chat_pb2.Tool)
    assert tool.HasField("mcp")
    assert tool.mcp.server_url == "https://mcp.example.com"
    assert tool.mcp.server_label == ""
    assert tool.mcp.server_description == ""
    assert list(tool.mcp.allowed_tool_names) == []
    assert tool.mcp.authorization == ""
    assert dict(tool.mcp.extra_headers) == {}


def test_mcp_tool_all_fields():
    """Test that mcp() correctly sets every field on the MCP proto."""
    from xai_sdk.tools import mcp

    tool = mcp(
        server_url="https://mcp.example.com",
        server_label="example",
        server_description="An example MCP server",
        allowed_tool_names=["search", "lookup"],
        authorization="Bearer my-token",
        extra_headers={"X-Trace-Id": "abc123"},
    )

    assert tool.HasField("mcp")
    assert tool.mcp.server_url == "https://mcp.example.com"
    assert tool.mcp.server_label == "example"
    assert tool.mcp.server_description == "An example MCP server"
    assert list(tool.mcp.allowed_tool_names) == ["search", "lookup"]
    assert tool.mcp.authorization == "Bearer my-token"
    assert dict(tool.mcp.extra_headers) == {"X-Trace-Id": "abc123"}


def test_developer_message():
    """Test that developer() creates a message with ROLE_DEVELOPER role."""
    # Simple string content
    msg = developer("Test developer message")
    assert msg.role == chat_pb2.MessageRole.ROLE_DEVELOPER
    assert len(msg.content) == 1
    assert msg.content[0].text == "Test developer message"

    # Multiple content args (str and text object)
    msg2 = developer("Part 1", "Part 2")
    assert msg2.role == chat_pb2.MessageRole.ROLE_DEVELOPER
    assert len(msg2.content) == 2
    assert msg2.content[0].text == "Part 1"
    assert msg2.content[1].text == "Part 2"


def test_agent_count_to_proto_4():
    """Test that agent_count=4 maps to the correct proto enum."""
    assert _agent_count_to_proto(4) == chat_pb2.AgentCount.AGENT_COUNT_4


def test_agent_count_to_proto_16():
    """Test that agent_count=16 maps to the correct proto enum."""
    assert _agent_count_to_proto(16) == chat_pb2.AgentCount.AGENT_COUNT_16


def test_agent_count_to_proto_invalid():
    """Test that an invalid agent_count raises ValueError."""
    with pytest.raises(ValueError, match="Invalid agent count"):
        _agent_count_to_proto(8)


def test_agent_count_on_request_proto():
    """Test that agent_count is correctly set on the GetCompletionsRequest proto."""
    request = chat_pb2.GetCompletionsRequest(
        model="grok-3",
        agent_count=chat_pb2.AgentCount.AGENT_COUNT_4,
    )
    assert request.agent_count == chat_pb2.AgentCount.AGENT_COUNT_4

    request = chat_pb2.GetCompletionsRequest(
        model="grok-3",
        agent_count=chat_pb2.AgentCount.AGENT_COUNT_16,
    )
    assert request.agent_count == chat_pb2.AgentCount.AGENT_COUNT_16


def test_compact_context_response_id():
    """Test that CompactContextResponse.id returns the id from the proto."""
    proto = chat_pb2.CompactContextResponse(id="compact-abc123")
    response = CompactContextResponse(proto)
    assert response.id == "compact-abc123"


def test_compact_context_response_encrypted_content():
    """Test that CompactContextResponse.encrypted_content returns the encrypted_content from the proto."""
    proto = chat_pb2.CompactContextResponse(encrypted_content="opaque-encrypted-blob")
    response = CompactContextResponse(proto)
    assert response.encrypted_content == "opaque-encrypted-blob"


def test_compact_context_response_dropped_message_count():
    """Test that CompactContextResponse.dropped_message_count returns the count from the proto."""
    proto = chat_pb2.CompactContextResponse(dropped_message_count=5)
    response = CompactContextResponse(proto)
    assert response.dropped_message_count == 5


def test_compact_context_response_dropped_message_count_zero():
    """Test that dropped_message_count defaults to 0 when not set."""
    proto = chat_pb2.CompactContextResponse()
    response = CompactContextResponse(proto)
    assert response.dropped_message_count == 0


def test_compact_context_response_usage():
    """Test that CompactContextResponse.usage returns the SamplingUsage from the proto."""
    usage = usage_pb2.SamplingUsage(
        prompt_tokens=100,
        completion_tokens=20,
        total_tokens=120,
        reasoning_tokens=10,
    )
    proto = chat_pb2.CompactContextResponse(usage=usage)
    response = CompactContextResponse(proto)
    assert response.usage.prompt_tokens == 100
    assert response.usage.completion_tokens == 20
    assert response.usage.total_tokens == 120
    assert response.usage.reasoning_tokens == 10


def test_compact_context_response_all_fields():
    """Test CompactContextResponse with all fields populated."""
    usage = usage_pb2.SamplingUsage(
        prompt_tokens=50,
        completion_tokens=10,
        total_tokens=60,
    )
    proto = chat_pb2.CompactContextResponse(
        id="compact-xyz",
        encrypted_content="encrypted-payload",
        dropped_message_count=3,
        usage=usage,
    )
    response = CompactContextResponse(proto)
    assert response.id == "compact-xyz"
    assert response.encrypted_content == "encrypted-payload"
    assert response.dropped_message_count == 3
    assert response.usage.prompt_tokens == 50
    assert response.usage.total_tokens == 60


def test_compact_context_response_proto_accessible():
    """Test that the underlying proto is accessible via the .proto property."""
    proto = chat_pb2.CompactContextResponse(
        id="compact-test",
        encrypted_content="content",
        dropped_message_count=1,
    )
    response = CompactContextResponse(proto)
    assert response.proto == proto
    assert response.proto.id == "compact-test"


def test_compact_context_response_empty_encrypted_content():
    """Test CompactContextResponse when encrypted_content is empty."""
    proto = chat_pb2.CompactContextResponse(id="compact-empty", encrypted_content="")
    response = CompactContextResponse(proto)
    assert response.encrypted_content == ""


def test_append_compact_context_response_creates_user_message():
    """Test that append(CompactContextResponse) produces a ROLE_USER message with encrypted_content."""
    from xai_sdk.proto import chat_pb2_grpc
    from xai_sdk.sync.chat import Chat as SyncChat

    proto = chat_pb2.CompactContextResponse(
        id="compact-test",
        encrypted_content="opaque-blob",
    )
    compact_resp = CompactContextResponse(proto)

    # Create a minimal Chat to test append behavior.
    stub = chat_pb2_grpc.ChatStub.__new__(chat_pb2_grpc.ChatStub)
    chat = SyncChat(stub, None, None, model="grok-4.3")
    chat.append(compact_resp)

    assert len(chat.messages) == 1
    assert chat.messages[0].role == chat_pb2.MessageRole.ROLE_USER
    assert chat.messages[0].encrypted_content == "opaque-blob"
    assert len(chat.messages[0].content) == 0


def test_append_compact_context_response_clears_existing_messages():
    """Test that appending a CompactContextResponse clears prior messages."""
    from xai_sdk.chat import user as user_msg
    from xai_sdk.proto import chat_pb2_grpc
    from xai_sdk.sync.chat import Chat as SyncChat

    proto = chat_pb2.CompactContextResponse(encrypted_content="blob")
    compact_resp = CompactContextResponse(proto)

    stub = chat_pb2_grpc.ChatStub.__new__(chat_pb2_grpc.ChatStub)
    chat = SyncChat(stub, None, None, model="grok-4.3")
    chat.append(user_msg("Hello"))
    assert len(chat.messages) == 1

    chat.append(compact_resp)

    assert len(chat.messages) == 1
    assert chat.messages[0].role == chat_pb2.MessageRole.ROLE_USER
    assert chat.messages[0].encrypted_content == "blob"
