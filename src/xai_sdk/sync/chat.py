import datetime
import json
import time
from typing import Iterator, Optional, Sequence, TypeVar

from pydantic import BaseModel

from ..chat import BaseChat, BaseClient, Chunk, PollTimer, Response
from ..proto import chat_pb2, deferred_pb2


class Client(BaseClient["Chat"]):
    """Sync Client for interacting with the `Chat` API."""

    def _make_chat(self, **settings) -> "Chat":
        return Chat(self._stub, **settings)


T = TypeVar("T", bound=BaseModel)


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
        response = self._stub.GetCompletion(self._make_request(1))
        return Response(response, 0)

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
        response = self._stub.GetCompletion(self._make_request(n))
        return [Response(response, i) for i in range(n)]

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
        response = Response(chat_pb2.GetChatCompletionResponse(choices=[chat_pb2.Choice()]), 0)
        stream = self._stub.GetCompletionChunk(self._make_request(1))

        for chunk in stream:
            response.process_chunk(chunk)
            yield response, Chunk(chunk, 0)

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
        proto = chat_pb2.GetChatCompletionResponse(choices=[chat_pb2.Choice(index=i) for i in range(n)])
        responses = [Response(proto, i) for i in range(n)]
        stream = self._stub.GetCompletionChunk(self._make_request(n))

        for chunk in stream:
            responses[0].process_chunk(chunk)
            yield responses, [Chunk(chunk, i) for i in range(n)]

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
        response = self._stub.GetCompletion(self._make_request(1))

        r = Response(response, 0)
        parsed = shape.model_validate_json(r.content)
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
        response = self._stub.StartDeferredCompletion(self._make_request(n))
        while True:
            r = self._stub.GetDeferredCompletion(deferred_pb2.GetDeferredRequest(request_id=response.request_id))
            match r.status:
                case deferred_pb2.DeferredStatus.DONE:
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
        response = self._defer(n, timeout, interval)
        return [Response(response, i) for i in range(n)]
