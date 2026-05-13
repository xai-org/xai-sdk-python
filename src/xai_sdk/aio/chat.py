import asyncio
import datetime
import json
import sys
import warnings
from typing import Any, Optional, Sequence, TypeVar

from opentelemetry.trace import SpanKind, Status, StatusCode
from pydantic import BaseModel

from ..chat import BaseChat, BaseClient, Chunk, Response
from ..poll_timer import PollTimer
from ..proto import chat_pb2, deferred_pb2
from ..telemetry import get_tracer

tracer = get_tracer(__name__)


class Client(BaseClient["Chat"]):
    """Async Client for interacting with the `Chat` API."""

    def _make_chat(self, conversation_id: Optional[str], **settings) -> "Chat":
        return Chat(self._stub, conversation_id, **settings)

    async def get_stored_completion(self, response_id: str) -> Sequence[Response]:
        """Retrieves a stored chat completion response by its ID.

        This method fetches the a model completion by a given response_id.
        The response_id must be from a chat instance that was created
        with `store_messages=True`.

        Returns a sequence since the stored response may contain multiple
        choices if it was generated using one of the batch methods such as `sample_batch()`,
        `stream_batch()`, or `defer_batch()`.

        If the response was generated using a non-batch method such as `sample()`,
        the sequence will contain a single response.

        Args:
            response_id: The ID of the stored response to retrieve.

        Returns:
            Sequence[Response]: A sequence of `Response` objects. Contains a single response for
                responses generated with non-batch methods such as `sample()` or multiple responses for those generated
                with batch methods such as `sample_batch()`.

        Example:
            >>> # Retrieve a previously stored response
            >>> stored_responses = await client.chat.get_stored_completion("response_abc123")
            >>> print(stored_responses[0].content)
            "Previously generated response content"
        """
        response = await self._stub.GetStoredCompletion(chat_pb2.GetStoredCompletionRequest(response_id=response_id))
        return [Response(response, i) for i in range(len(response.outputs))]

    async def delete_stored_completion(self, response_id: str) -> str:
        """Deletes a stored chat completion response from the xAI backend.

        This method permanently removes a previously stored chat completion response by its ID.
        The response_id must be from a chat instance that was created with `store_messages=True`.
        Once deleted, the response can no longer be retrieved via `get_stored_completion()` or referenced by
        `previous_response_id` in new chat instances.

        Args:
            response_id: The ID of the stored response to delete.

        Returns:
            str: The ID of the deleted response, confirming successful deletion.

        Example:
            >>> # Delete a stored response
            >>> deleted_id = await client.chat.delete_stored_completion("response_abc123")
            >>> print(f"Deleted response: {deleted_id}")
            "Deleted response: response_abc123"
        """
        response = await self._stub.DeleteStoredCompletion(
            chat_pb2.DeleteStoredCompletionRequest(response_id=response_id)
        )
        return response.response_id


T = TypeVar("T", bound=BaseModel)


class _AsyncChatStreamBase:
    def __init__(self, chat: "Chat", n: int, span_name: str) -> None:
        self._chat = chat
        self._n = n
        self._span_name = span_name
        self._stream: Optional[Any] = None
        self._stream_iterator: Optional[Any] = None
        self._span: Optional[Any] = None
        self._closed = False
        self._first_chunk_received = False

    @property
    def grpc_call(self) -> Optional[Any]:
        """Returns the underlying gRPC unary-stream call, once iteration has started."""
        return self._stream

    def cancel(self) -> bool:
        """Cancels the underlying gRPC stream if it has started."""
        self._closed = True
        if self._stream is None:
            self._finish_span()
            return False

        cancelled = self._stream.cancel()
        self._finish_span()
        return cancelled

    async def close(self) -> None:
        """Closes the stream by cancelling the underlying gRPC call."""
        self.cancel()

    async def aclose(self) -> None:
        """Closes the stream using the standard async-generator method name."""
        await self.close()

    def _ensure_started(self) -> Any:
        if self._closed:
            raise StopAsyncIteration

        if self._stream is None:
            self._span = tracer.start_span(
                name=f"{self._span_name} {self._chat._proto.model}",
                kind=SpanKind.CLIENT,
                attributes=self._chat._make_span_request_attributes(),
            )
            stream = self._chat._stub.GetCompletionChunk(self._chat._make_request(self._n))
            self._stream = stream
            self._stream_iterator = stream.__aiter__()

        if self._stream_iterator is None:
            raise StopAsyncIteration
        return self._stream_iterator

    async def _read_chunk(self, responses: Sequence[Response]) -> chat_pb2.GetChatCompletionChunk:
        try:
            stream_iterator = self._ensure_started()
            return await stream_iterator.__anext__()
        except StopAsyncIteration:
            self._finish_span(responses)
            raise
        except BaseException:
            self._finish_span(exc_info=sys.exc_info())
            raise

    def _mark_first_chunk_received(self) -> None:
        if not self._first_chunk_received and self._span is not None:
            self._span.set_attribute(
                "gen_ai.completion.start_time",
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
            self._first_chunk_received = True

    def _finish_span(
        self,
        responses: Optional[Sequence[Response]] = None,
        exc_info: Optional[tuple[Any, Any, Any]] = None,
    ) -> None:
        if self._span is None:
            return

        if responses is not None:
            self._span.set_attributes(self._chat._make_span_response_attributes(responses))

        _, exc, _ = exc_info or (None, None, None)
        if exc is not None:
            self._span.record_exception(exc)
            self._span.set_status(Status(StatusCode.ERROR, str(exc)))

        self._span.end()
        self._span = None


class AsyncChatStream(_AsyncChatStreamBase):
    """Cancelable async iterator for a single streamed chat completion."""

    def __init__(self, chat: "Chat") -> None:
        """Creates a cancelable single-response chat stream."""
        super().__init__(chat, n=1, span_name="chat.stream")
        self._index = None if chat._uses_server_side_tools() else 0
        self._response = Response(
            chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput()]), self._index
        )

    def __aiter__(self) -> "AsyncChatStream":
        return self

    async def __anext__(self) -> tuple[Response, Chunk]:
        chunk = await self._read_chunk([self._response])
        self._mark_first_chunk_received()

        # Auto-detect if server added tools implicitly
        self._index = self._chat._auto_detect_multi_output_mode(self._index, chunk.outputs)
        self._response._index = self._index

        self._response.process_chunk(chunk)
        chunk_obj = Chunk(chunk, self._index)
        return self._response, chunk_obj


class AsyncChatBatchStream(_AsyncChatStreamBase):
    """Cancelable async iterator for multiple streamed chat completions."""

    def __init__(self, chat: "Chat", n: int) -> None:
        """Creates a cancelable multi-response chat stream."""
        super().__init__(chat, n=n, span_name="chat.stream_batch")
        proto = chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput(index=i) for i in range(n)])
        self._responses = [Response(proto, i) for i in range(n)]

    def __aiter__(self) -> "AsyncChatBatchStream":
        return self

    async def __anext__(self) -> tuple[Sequence[Response], Sequence[Chunk]]:
        chunk = await self._read_chunk(self._responses)
        self._mark_first_chunk_received()

        self._responses[0].process_chunk(chunk)
        return self._responses, [Chunk(chunk, i) for i in range(self._n)]


class Chat(BaseChat):
    """Utility class for simplifying the interaction with Chat requests and responses."""

    async def sample(self) -> Response:
        """Asynchronously samples a single chat completion response from the model.

        This method sends an async request to the chat API with the current conversation
        history and returns a single response. It is suitable for non-streaming async
        interactions where a single answer is needed.

        Returns:
            Response: A `Response` object containing the model's output, including the
                content and metadata for the first (and only) choice.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Hello, how are you?"))
            >>> response = await chat.sample()
            >>> print(response.content)
            "I'm doing great, thanks for asking!"
        """
        with tracer.start_as_current_span(
            name=f"chat.sample {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            index = None if self._uses_server_side_tools() else 0
            response_pb = await self._stub.GetCompletion(self._make_request(1))
            index = self._auto_detect_multi_output_mode(index, response_pb.outputs)
            response = Response(response_pb, index)
            span.set_attributes(self._make_span_response_attributes([response]))
            return response

    async def sample_batch(self, n: int) -> Sequence[Response]:
        """Asynchronously samples multiple chat completion responses in a single request.

        This method requests `n` responses from the model for the current conversation
        history and returns them as a sequence. It is useful for async scenarios where
        multiple alternative responses are needed, such as exploring different model outputs.

        Args:
            n: The number of responses to generate.

        Returns:
            Sequence[Response]: A sequence of `Response` objects, each representing one of
                the `n` generated responses.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Suggest a gift idea"))
            >>> responses = await chat.sample_batch(3)
            >>> for i, response in enumerate(responses):
            ...     print(f"Option {i+1}: {response.content}")
            Option 1: A book
            Option 2: A scarf
            Option 3: A gift card
        """
        warnings.warn(
            "chat.sample_batch will be deprecated in a future version release. Use chat.sample() instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )

        with tracer.start_as_current_span(
            name=f"chat.sample_batch {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            response_pb = await self._stub.GetCompletion(self._make_request(n))
            responses = [Response(response_pb, i) for i in range(n)]
            span.set_attributes(self._make_span_response_attributes(responses))
            return responses

    def stream(self) -> AsyncChatStream:
        """Asynchronously streams a single chat completion response.

        This method streams the model's response in chunks, yielding each chunk as it is
        received. It is suitable for real-time applications where partial responses
        are displayed as they arrive, such as interactive chat interfaces.

        Returns:
            AsyncChatStream: A cancelable async iterator yielding tuples, each containing:
                - `Response`: The accumulating response object, updated with each chunk.
                - `Chunk`: A `Chunk` object containing the content and metadata of the
                    current chunk.
                Call `stream.cancel()`, `await stream.close()`, or `await stream.aclose()`
                to cancel the underlying gRPC stream from another task.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Tell me a story"))
            >>> async for response, chunk in chat.stream():
            ...     print(chunk.content, end="", flush=True)
            Once upon a time...
            >>> print(response.content)
            "Once upon a time..." (full accumulated response)
        """
        return AsyncChatStream(self)

    def stream_batch(self, n: int) -> AsyncChatBatchStream:
        """Asynchronously streams multiple chat completion responses.

        This method streams `n` responses concurrently in a single request, yielding chunks
        for all responses as they arrive. It is useful for real-time async applications
        needing multiple alternative responses, such as comparing different model outputs
        live.

        Args:
            n: The number of responses to generate.

        Returns:
            AsyncChatBatchStream: A cancelable async iterator yielding tuples, each containing:
                - `Sequence[Response]`: A sequence of `Response` objects, one for each of
                    the `n` responses, updated with each chunk.
                - `Sequence[Chunk]`: A sequence of `Chunk` objects, one for each response,
                    containing the content and metadata of the current chunk.
                Call `stream.cancel()`, `await stream.close()`, or `await stream.aclose()`
                to cancel the underlying gRPC stream from another task.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Suggest a gift"))
            >>> async for responses, chunks in chat.stream_batch(2):
            ...     for i, chunk in enumerate(chunks):
            ...         print(f"Option {i+1}: {chunk.content}")
            Option 1: A book...
            Option 2: A scarf...
            >>> for i, response in enumerate(responses):
            ...     print(f"Final Response {i+1}: {response.content}")
        """
        warnings.warn(
            "chat.stream_batch will be deprecated in a future version release. Use chat.stream() instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )

        return AsyncChatBatchStream(self, n)

    async def parse(self, shape: type[T]) -> tuple[Response, T]:
        """Asynchronously generates and parses a single chat completion response into a Pydantic model.

        This method configures the chat request to return a JSON response conforming to the
        provided Pydantic model's schema, sends an async request, and parses the response
        into an instance of the specified model. It is useful for extracting structured data
        from the model's output in async workflows.

        Args:
            shape: A Pydantic model class (subclass of `BaseModel`) defining the expected
                structure of the response.

        Returns:
            tuple[Response, T]: A tuple containing:
                - `Response`: The raw response object with the model's output and metadata.
                - `T`: An instance of the provided Pydantic model, populated with the parsed
                    response data.

        Example:
            >>> from pydantic import BaseModel
            >>> class Answer(BaseModel):
            ...     text: str
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Say hello"))
            >>> response, parsed = await chat.parse(Answer)
            >>> print(response.content)
            "{'text': 'hello'}"
            >>> print(parsed.text)
            "hello"
        """
        self.proto.response_format.CopyFrom(
            chat_pb2.ResponseFormat(
                format_type=chat_pb2.FormatType.FORMAT_TYPE_JSON_SCHEMA,
                schema=json.dumps(shape.model_json_schema()),
            )
        )

        with tracer.start_as_current_span(
            name=f"chat.parse {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            response = await self._stub.GetCompletion(self._make_request(1))
            index = None if self._uses_server_side_tools() else 0
            index = self._auto_detect_multi_output_mode(index, response.outputs)
            r = Response(response, index)
            parsed = shape.model_validate_json(r.content)
            span.set_attributes(self._make_span_response_attributes([r]))
            return r, parsed

    async def _defer(
        self,
        n: int,
        timeout: Optional[datetime.timedelta],
        interval: Optional[datetime.timedelta],
    ) -> chat_pb2.GetChatCompletionResponse:
        """Internal method to perform an async deferred API request with polling.

        This method initiates an async deferred chat completion request, polls the server
        until the request is complete, and returns the response. It is used by `defer` and
        `defer_batch` to handle unstable connections by breaking long requests into shorter
        polling intervals.

        Args:
            n: The number of responses to generate.
            timeout: Optional maximum duration to wait for the request to complete, defaults to 10 minutes.
            interval: Optional interval between polling attempts, defaults to 100 milliseconds.

        Returns:
            chat_pb2.GetChatCompletionResponse: The raw protocol buffer response from the
                server.

        Raises:
            RuntimeError: If the deferred request expires.
            ValueError: If an unknown deferred status is received.
        """
        timer = PollTimer(timeout, interval, context="waiting for deferred chat completion")
        operation = "chat.defer" if n == 1 else "chat.defer_batch"

        with tracer.start_as_current_span(
            name=f"{operation} {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            response = await self._stub.StartDeferredCompletion(self._make_request(n))

            while True:
                r = await self._stub.GetDeferredCompletion(
                    deferred_pb2.GetDeferredRequest(request_id=response.request_id)
                )
                match r.status:
                    case deferred_pb2.DeferredStatus.DONE:
                        span.set_attributes(
                            self._make_span_response_attributes([Response(r.response, i) for i in range(n)])
                        )
                        return r.response
                    case deferred_pb2.DeferredStatus.EXPIRED:
                        raise RuntimeError("Deferred request expired.")
                    case deferred_pb2.DeferredStatus.PENDING:
                        await asyncio.sleep(timer.sleep_interval_or_raise())
                        continue
                    case unknown_status:
                        raise ValueError(f"Unknown deferred status: {unknown_status}")

    async def defer(
        self, *, timeout: Optional[datetime.timedelta] = None, interval: Optional[datetime.timedelta] = None
    ) -> Response:
        """Asynchronously samples a single chat completion response using polling.

        This method uses an async deferred request with polling to handle unstable
        connections. It is suitable for async environments where long-running requests may
        fail, as it breaks the request into shorter polling intervals.

        Args:
            timeout: Optional maximum duration to wait for the request to complete, defaults to 10 minutes.
            interval: Optional interval between polling attempts, defaults to 100 milliseconds.

        Returns:
            Response: A `Response` object containing the model's output for the first (and
                only) choice.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Hello"))
            >>> response = await chat.defer(timeout=datetime.timedelta(minutes=5))
            >>> print(response.content)
            "Hi there!"
        """
        response = await self._defer(1, timeout, interval)
        return Response(response, 0)

    async def defer_batch(
        self, n: int, *, timeout: Optional[datetime.timedelta] = None, interval: Optional[datetime.timedelta] = None
    ) -> Sequence[Response]:
        """Asynchronously samples multiple chat completion responses using polling.

        This method uses an async deferred request with polling to handle unstable
        connections, generating `n` responses concurrently. It is useful for async batch
        processing in environments with unreliable connections.

        Args:
            n: The number of responses to generate.
            timeout: Optional maximum duration to wait for the request to complete, defaults to 10 minutes.
            interval: Optional interval between polling attempts, defaults to 100 milliseconds.

        Returns:
            Sequence[Response]: A sequence of `Response` objects, each representing one of
                the `n` generated responses.

        Example:
            >>> chat = client.chat.create(model="grok-4.20-non-reasoning")
            >>> chat.append(user("Suggest a gift"))
            >>> responses = await chat.defer_batch(3, timeout=datetime.timedelta(minutes=5))
            >>> for i, response in enumerate(responses):
            ...     print(f"Option {i+1}: {response.content}")
            Option 1: A book
            Option 2: A scarf
            Option 3: A gift card
        """
        warnings.warn(
            "chat.defer_batch will be deprecated in a future version release. Use chat.defer() instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )

        response = await self._defer(n, timeout, interval)
        return [Response(response, i) for i in range(n)]
