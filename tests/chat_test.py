from xai_sdk.chat import Response
from xai_sdk.proto import chat_pb2, sample_pb2
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
