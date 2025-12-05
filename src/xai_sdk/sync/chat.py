import datetime
import json
import time
import warnings
from typing import Iterator, Optional, Sequence, TypeVar

from opentelemetry.trace import SpanKind
from pydantic import BaseModel

from ..chat import BaseChat, BaseClient, Chunk, Response
from ..poll_timer import PollTimer
from ..proto import chat_pb2, deferred_pb2
from ..telemetry import get_tracer


class Client(BaseClient["Chat"]):
    """Sync Client for interacting with the `Chat` API."""

    def _make_chat(self, conversation_id: Optional[str], **settings) -> "Chat":
        return Chat(self._stub, conversation_id, **settings)

    def get_stored_completion(self, response_id: str) -> Sequence[Response]:
        """Retrieves a stored chat completion response by its ID.

        This method fetches the a model completion by a given response_id.
        The response_id must be from a chat instance that was created
        with `store_messages=True`.

        Returns a sequence since the stored response may contain multiple
        choices if it was generated using one of the batch methods such as `sample_batch()`, `stream_batch()`,
        or `defer_batch()`.

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
            >>> stored_responses = client.chat.get_stored_completion("response_abc123")
            >>> print(stored_responses[0].content)
            "Previously generated response content"
        """
        response = self._stub.GetStoredCompletion(chat_pb2.GetStoredCompletionRequest(response_id=response_id))
        return [Response(response, i) for i in range(len(response.outputs))]

    def delete_stored_completion(self, response_id: str) -> str:
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
            >>> deleted_id = client.chat.delete_stored_completion("response_abc123")
            >>> print(f"Deleted response: {deleted_id}")
            "Deleted response: response_abc123"
        """
        response = self._stub.DeleteStoredCompletion(chat_pb2.DeleteStoredCompletionRequest(response_id=response_id))
        return response.response_id


T = TypeVar("T", bound=BaseModel)

tracer = get_tracer(__name__)


class Chat(BaseChat):
    """Utility class for simplifying the interaction with Chat requests and responses."""

    def sample(self) -> Response:
        """Samples a single chat completion response from the model.

        This method sends a request to the chat API with the current conversation history
        and returns a single response. It is suitable for simple, non-streaming interactions
        where a single answer is needed.

        Returns:
            Response: A `Response` object containing the model's output, including the content
                and metadata for the first (and only) choice.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Hello, how are you?"))
            >>> response = chat.sample()
            >>> print(response.content)
            "I'm doing great, thanks for asking!"
        """
        with tracer.start_as_current_span(
            name=f"chat.sample {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            index = None if self._uses_server_side_tools() else 0
            response_pb = self._stub.GetCompletion(self._make_request(1))
            index = self._auto_detect_multi_output_mode(index, response_pb.outputs)
            response = Response(response_pb, index)
            span.set_attributes(self._make_span_response_attributes([response]))
            return response

    def sample_batch(self, n: int) -> Sequence[Response]:
        """Samples multiple chat completion responses concurrently in a single request.

        This method requests `n` responses from the model for the current conversation
        history and returns them as a sequence. It is useful for scenarios where multiple
        alternative responses are needed, such as exploring different model outputs.

        Args:
            n: The number of responses to generate.

        Returns:
            Sequence[Response]: A sequence of `Response` objects, each representing one of the `n` generated responses.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Suggest a gift idea"))
            >>> responses = chat.sample_batch(3)
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
            response_pb = self._stub.GetCompletion(self._make_request(n))
            responses = [Response(response_pb, i) for i in range(n)]
            span.set_attributes(self._make_span_response_attributes(responses))
            return responses

    def stream(self) -> Iterator[tuple[Response, Chunk]]:
        """Streams a single chat completion response.

        This method streams the model's response in chunks, yielding each chunk as it is
        received. It is suitable for real-time applications where partial responses are
        displayed as they arrive, such as interactive chat interfaces.

        Returns:
            Iterator[tuple[Response, Chunk]]: An iterator yielding tuples, each containing:
                - `Response`: The accumulating response object, updated with each chunk.
                - `Chunk`: A `Chunk` object containing the content and metadata of the
                    current chunk.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Tell me a story"))
            >>> for response, chunk in chat.stream():
            ...     print(chunk.content, end="", flush=True)
            Once upon a time...
            >>> print(response.content)
            "Once upon a time..." (full accumulated response)
        """
        first_chunk_received = False
        with tracer.start_as_current_span(
            name=f"chat.stream {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            index = None if self._uses_server_side_tools() else 0
            response = Response(chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput()]), index)
            stream = self._stub.GetCompletionChunk(self._make_request(1))

            for chunk in stream:
                if not first_chunk_received:
                    span.set_attribute(
                        "gen_ai.completion.start_time", datetime.datetime.now(datetime.timezone.utc).isoformat()
                    )
                    first_chunk_received = True

                # Auto-detect if server added tools implicitly
                index = self._auto_detect_multi_output_mode(index, chunk.outputs)
                response._index = index

                response.process_chunk(chunk)
                chunk_obj = Chunk(chunk, index)
                yield response, chunk_obj

            span.set_attributes(self._make_span_response_attributes([response]))

    def stream_batch(self, n: int) -> Iterator[tuple[Sequence[Response], Sequence[Chunk]]]:
        """Streams multiple chat completion responses.

        This method streams `n` responses concurrently in a single request, yielding chunks
        for all responses as they arrive. It is useful for real-time applications needing
        multiple alternative responses, such as comparing different outputs live.

        Args:
            n: The number of responses to generate.

        Returns:
            Iterator[tuple[Sequence[Response], Sequence[Chunk]]]: An iterator yielding tuples,
                each containing:
                - `Sequence[Response]`: A sequence of `Response` objects, one for each of the
                    `n` responses, updated with each chunk.
                - `Sequence[Chunk]`: A sequence of `Chunk` objects, one for each response,
                    containing the content and metadata of the current chunk.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Suggest a gift"))
            >>> for responses, chunks in chat.stream_batch(2):
            ...     for i, chunk in enumerate(chunks):
            ...         print(f"Option {i+1}: {chunk.content}")
            Option 1: A book...
            Option 2: A scarf...
        """
        warnings.warn(
            "chat.stream_batch will be deprecated in a future version release. Use chat.stream() instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )

        proto = chat_pb2.GetChatCompletionResponse(outputs=[chat_pb2.CompletionOutput(index=i) for i in range(n)])
        responses = [Response(proto, i) for i in range(n)]
        first_chunk_received = False

        with tracer.start_as_current_span(
            name=f"chat.stream_batch {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            stream = self._stub.GetCompletionChunk(self._make_request(n))
            for chunk in stream:
                if not first_chunk_received:
                    span.set_attribute(
                        "gen_ai.completion.start_time", datetime.datetime.now(datetime.timezone.utc).isoformat()
                    )
                    first_chunk_received = True

                responses[0].process_chunk(chunk)
                yield responses, [Chunk(chunk, i) for i in range(n)]

            span.set_attributes(self._make_span_response_attributes(responses))

    def parse(self, shape: type[T]) -> tuple[Response, T]:
        """Generates and parses a single chat completion response into a Pydantic model.

        This method configures the chat request to return a JSON response conforming to the
        provided Pydantic model's schema, sends the request, and parses the response into
        an instance of the specified model. It is useful for extracting structured data from
        the model's output.

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
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Say hello"))
            >>> response, parsed = chat.parse(Answer)
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
            response = self._stub.GetCompletion(self._make_request(1))
            index = None if self._uses_server_side_tools() else 0
            index = self._auto_detect_multi_output_mode(index, response.outputs)
            r = Response(response, index)
            parsed = shape.model_validate_json(r.content)
            span.set_attributes(self._make_span_response_attributes([r]))
            return r, parsed

    def _defer(
        self, n: int, timeout: Optional[datetime.timedelta], interval: Optional[datetime.timedelta]
    ) -> chat_pb2.GetChatCompletionResponse:
        """Internal method to perform a deferred API request with polling.

        This method initiates a deferred chat completion request, polls the server until
        the request is complete, and returns the response. It is used by `defer` and
        `defer_batch` to handle unstable connections by breaking long requests into
        shorter polling intervals.

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
        timer = PollTimer(timeout, interval)
        operation = "chat.defer" if n == 1 else "chat.defer_batch"

        with tracer.start_as_current_span(
            name=f"{operation} {self._proto.model}",
            kind=SpanKind.CLIENT,
            attributes=self._make_span_request_attributes(),
        ) as span:
            response = self._stub.StartDeferredCompletion(self._make_request(n))

            while True:
                r = self._stub.GetDeferredCompletion(deferred_pb2.GetDeferredRequest(request_id=response.request_id))
                match r.status:
                    case deferred_pb2.DeferredStatus.DONE:
                        span.set_attributes(
                            self._make_span_response_attributes([Response(r.response, i) for i in range(n)])
                        )
                        return r.response
                    case deferred_pb2.DeferredStatus.EXPIRED:
                        raise RuntimeError("Deferred request expired.")
                    case deferred_pb2.DeferredStatus.PENDING:
                        time.sleep(timer.sleep_interval_or_raise())
                        continue
                    case unknown_status:
                        raise ValueError(f"Unknown deferred status: {unknown_status}")

    def defer(
        self, *, timeout: Optional[datetime.timedelta] = None, interval: Optional[datetime.timedelta] = None
    ) -> Response:
        """Samples a single chat completion response using polling.

        This method uses a deferred request with polling to handle unstable connections.
        It is suitable for environments where long-running requests may fail, as it breaks
        the request into shorter polling intervals.

        Args:
            timeout: Optional maximum duration to wait for the request to complete, defaults to 10 minutes.
            interval: Optional interval between polling attempts, defaults to 100 milliseconds.

        Returns:
            Response: A `Response` object containing the model's output for the first (and
                only) choice.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Hello"))
            >>> response = chat.defer(timeout=datetime.timedelta(minutes=5))
            >>> print(response.content)
            "Hi there!"
        """
        response = self._defer(1, timeout, interval)
        return Response(response, 0)

    def defer_batch(
        self, n: int, *, timeout: Optional[datetime.timedelta] = None, interval: Optional[datetime.timedelta] = None
    ) -> Sequence[Response]:
        """Samples multiple chat completion responses using polling.

        This method uses a deferred request with polling to handle unstable connections,
        generating `n` responses concurrently. It is useful for batch processing in
        environments with unreliable connections.

        Args:
            n: The number of responses to generate.
            timeout: Optional maximum duration to wait for the request to complete, defaults to 10 minutes.
            interval: Optional interval between polling attempts, defaults to 100 milliseconds.

        Returns:
            Sequence[Response]: A sequence of `Response` objects, each representing one of
                the `n` generated responses.

        Example:
            >>> chat = client.chat.create(model="grok-3")
            >>> chat.append(user("Suggest a gift"))
            >>> responses = chat.defer_batch(3, timeout=datetime.timedelta(minutes=5))
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

        response = self._defer(n, timeout, interval)
        return [Response(response, i) for i in range(n)]
