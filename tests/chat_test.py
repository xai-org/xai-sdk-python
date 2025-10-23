from xai_sdk.chat import Response
from xai_sdk.proto import chat_pb2, sample_pb2


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
