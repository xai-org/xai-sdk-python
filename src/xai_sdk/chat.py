import abc
import datetime
import json
import time
from typing import Any, Generic, Literal, Optional, Sequence, TypeVar, Union

import grpc
from typing_extensions import Self

from .meta import ProtoDecorator
from .proto import chat_pb2, chat_pb2_grpc, image_pb2, sample_pb2, usage_pb2
from .search import SearchParameters

Content = Union[str, chat_pb2.Content]

T = TypeVar("T")


ImageDetail = Literal["auto", "low", "high"]
ReasoningEffort = Literal["low", "high"]
ToolMode = Literal["auto", "none", "required"]
# json_schema purposefully omitted, since the `parse` method should be used when needing json_schema responses.
ResponseFormat = Literal["text", "json_object"]


class BaseClient(abc.ABC, Generic[T]):
    """Base Client for interacting with the `Chat` API."""

    _stub: chat_pb2_grpc.ChatStub

    def __init__(self, channel: Union[grpc.Channel, grpc.aio.Channel]):
        """Creates a new client based on a gRPC channel."""
        self._stub = chat_pb2_grpc.ChatStub(channel)

    def create(
        self,
        model: str,
        *,
        messages: Optional[Sequence[chat_pb2.Message]] = None,
        user: Optional[str] = None,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
        stop: Optional[Sequence[str]] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        tools: Optional[Sequence[chat_pb2.Tool]] = None,
        tool_choice: Optional[Union[ToolMode, chat_pb2.ToolChoice]] = None,
        parallel_tool_calls: Optional[bool] = None,
        response_format: Optional[Union[ResponseFormat, chat_pb2.ResponseFormat]] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        reasoning_effort: Optional[Union[ReasoningEffort, "chat_pb2.ReasoningEffort"]] = None,
        search_parameters: Optional[Union[SearchParameters, chat_pb2.SearchParameters]] = None,
    ) -> T:
        """Creates a new chat conversation.

        This function does not immediately perform an RPC. It only initializes a mutable request
        instance.

        Examples:
            ```
            chat = client.chat.create(
                model="grok-3-latest",
                messages=[
                    system("You are a pirate"),
                    user("How are you?"),
                ]
            )
            response = chat.sample()
            chat.append(response)
            print(response)

            chat.append(user("Tell me a joke"))
            response = chat.sample()
            print(response)
            ```

        Args:
            model: Model to use, e.g. "grok-3-latest".
            messages: A list of messages that make up the the chat conversation. Different models support different
                message types, such as image and text.
            user: A unique identifier representing your end-user, which can help xAI to monitor and detect abuse.
            max_tokens: The maximum number of tokens that can be generated in the chat completion.
            seed: If specified, our system will make a best effort to sample deterministically, such that repeated
                requests with the same seed and parameters should return the same result.
            stop: Up to 4 sequences where the API will stop generating further tokens.
            temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output
                more random, while lower values like 0.2 will make it more focused and deterministic.
            top_p: An alternative to sampling with temperature, called nucleus sampling, where the model considers the
                results of the tokens with `top_p` probability mass.
            logprobs: Whether to return log probabilities of the output tokens or not. If true, returns the log
                probabilities of each output token returned in the content of message.
            top_logprobs: An integer between 0 and 8 specifying the number of most likely tokens to return at each token
                position, each with an associated log probability. logprobs must be set to true if this parameter is
                used.
            tools: A list of tools the model may call in JSON-schema. Currently, only functions are supported as a tool.
                Use this to provide a list of functions the model may generate JSON inputs for. A max of 128 functions
                are supported.
            tool_choice: Controls which (if any) tool is called by the model. `none` means the model will not call any
                tool and instead generates a message. `auto` means the model can pick between generating a message or
                calling one or more tools. `required` means the model must call one or more tools.
                `auto` is the default if tools are present.
                To force the model to always invoke a specific tool, use the `required_tool(name)` function to create a
                `ToolChoice` with mode `required` and specify the tool's name. For example:
                ```
                tool_choice=required_tool("get_weather")
                ```
                This ensures the model must call the specified tool from the list provided in `tools`.
            parallel_tool_calls: If set to false, the model can perform maximum one tool call per response.
                Defaults to true.
            response_format: An object specifying the format that the model must output.
                `json_object` means the model must output a JSON object (although the shape is arbitrary).
                `text` means the model must output a text string.
                To force the model to output a JSON object adhering to a specific JSON Schema use the client's `parse`
                method instead.
            frequency_penalty: Positive values penalize new tokens based on their existing frequency in the text so far,
                decreasing the model's likelihood to repeat the same line verbatim.
            presence_penalty: Positive values penalize new tokens based on whether they appear in the text so far,
                increasing the model's likelihood to talk about new topics.
            reasoning_effort: Constrains how hard a reasoning model thinks before responding. Possible values are `low`
                (uses fewer reasoning tokens) and `high` (uses more reasoning tokens). Defaults to `low`.
            search_parameters: The parameters that control search behavior.
                This includes settings like search mode, date range, sources (e.g., web, news, or X), and whether
                to return citations. See `SearchParameters` for detailed configuration options.

        Returns:
            A new chat request bound to a client.
        """
        tool_choice_pb: Optional[chat_pb2.ToolChoice] = None
        if isinstance(tool_choice, str):
            tool_choice_pb = chat_pb2.ToolChoice(mode=_tool_mode_to_proto(tool_choice))
        else:
            tool_choice_pb = tool_choice

        response_format_pb: Optional[chat_pb2.ResponseFormat] = None
        if isinstance(response_format, str):
            response_format_pb = chat_pb2.ResponseFormat(format_type=_format_type_to_proto(response_format))
        else:
            response_format_pb = response_format

        reasoning_effort_pb: Optional[chat_pb2.ReasoningEffort] = None
        if isinstance(reasoning_effort, str):
            reasoning_effort_pb = _reasoning_effort_to_proto(reasoning_effort)
        else:
            reasoning_effort_pb = reasoning_effort

        search_parameters_pb: Optional[chat_pb2.SearchParameters] = None
        if isinstance(search_parameters, SearchParameters):
            search_parameters_pb = search_parameters._to_proto()
        else:
            search_parameters_pb = search_parameters

        return self._make_chat(
            model=model,
            messages=messages,
            user=user,
            max_tokens=max_tokens,
            seed=seed,
            stop=stop,
            temperature=temperature,
            top_p=top_p,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            tools=tools,
            tool_choice=tool_choice_pb,
            parallel_tool_calls=parallel_tool_calls,
            response_format=response_format_pb,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            reasoning_effort=reasoning_effort_pb,
            search_parameters=search_parameters_pb,
        )

    @abc.abstractmethod
    def _make_chat(self, **settings) -> T:
        """Creates the proto wrapper for chat requests."""


class BaseChat(ProtoDecorator[chat_pb2.GetCompletionsRequest]):
    """Utility class for simplifying the interaction with Chat requests and responses."""

    _stub: chat_pb2_grpc.ChatStub

    def __init__(self, stub: chat_pb2_grpc.ChatStub, **settings) -> None:
        """Prepares a new chat request.

        Args:
            stub: gRPC stub used to connect to the server.
            **settings: See `chat_pb2.GetCompletionsRequest`.
        """
        super().__init__(chat_pb2.GetCompletionsRequest(**settings))
        self._stub = stub

    def append(self, message: Union[chat_pb2.Message, "Response"]) -> Self:
        """Adds a new message to the conversation history, enabling multi-turn interactions.

        This method appends a message to the chat's message sequence, which can be a user input,
        system prompt, assistant response, or tool result. It supports both `chat_pb2.Message`
        objects (created via helper functions like `user`, `system`, `assistant`, or `tool_result`) and
        `Response` objects from previous chat interactions. The method returns the chat object
        itself, allowing for method chaining.

        Examples:
            ```
            # Adding a simple user message
            chat = client.chat.create(model="grok-3")
            chat.append(user("How are you?"))
            ```

            ```
            # Adding a system prompt with an image
            chat = client.chat.create(model="grok-3")
            chat.append(system(
                "Analyze the following image: ",
                image("https://example.com/image.jpg", detail="high"),
                "Provide a detailed description."
            ))
            ```

            ```
            # Appending an assistant's response in a multi-turn conversation
            chat = client.chat.create(model="grok-3")
            chat.append(user("Tell me a pirate joke."))
            response = chat.sample()  # Get assistant's response
            print(f"Grok: {response.content}")
            chat.append(response)  # Add assistant's response to history
            chat.append(user("Another one, please!"))
            ```

            ```
            # Multi-turn chat loop (inspired by sync/chat.py)
            chat = client.chat.create(
                model="grok-3",
                messages=[system("You talk like a pirate.")]
            )
            while True:
                prompt = input("You: ")
                if prompt.lower() == "exit":
                    break
                chat.append(user(prompt))
                response = chat.sample()
                print(f"Grok: {response.content}")
                chat.append(response)
            ```

        Args:
            message: The message to append, either a `chat_pb2.Message` (e.g., created by `user`,
                `system`, `assistant`, or `tool_result`) or a `Response` object from a previous
                chat interaction.

        Returns:
            Self: The chat object, enabling method chaining.
        """
        if isinstance(message, chat_pb2.Message):
            self._proto.messages.append(message)
        elif isinstance(message, Response):
            self._proto.messages.append(
                chat_pb2.Message(
                    role=message._choice.message.role,
                    content=[text(message.content)],
                    tool_calls=message.tool_calls,
                )
            )
        else:
            raise ValueError("Unrecognized message type.")
        return self

    def _make_request(self, n: int) -> chat_pb2.GetCompletionsRequest:
        """Creates a request proto.

        Args:
            n: Number of completions to generate.
        """
        request = chat_pb2.GetCompletionsRequest()
        # prevent requests with no messages.
        if not self._proto.messages:
            raise ValueError(
                "Cannot create a completion request: No messages provided. Please include at least one "
                "message (e.g., using user(), system(), or assistant()) in the request."
            )

        request.CopyFrom(self._proto)
        request.n = n
        return request

    @property
    def messages(self) -> Sequence[chat_pb2.Message]:
        """Returns the messages in the conversation."""
        return self._proto.messages


def user(*args: Content) -> chat_pb2.Message:
    """Creates a new message of role "user"."""
    return chat_pb2.Message(role=chat_pb2.MessageRole.ROLE_USER, content=[_process_content(c) for c in args])


def assistant(*args: Content) -> chat_pb2.Message:
    """Creates a new message of role "assistant"."""
    return chat_pb2.Message(role=chat_pb2.MessageRole.ROLE_ASSISTANT, content=[_process_content(c) for c in args])


def system(*args: Content) -> chat_pb2.Message:
    """Creates a new message of role "system"."""
    return chat_pb2.Message(role=chat_pb2.MessageRole.ROLE_SYSTEM, content=[_process_content(c) for c in args])


def tool_result(result: str) -> chat_pb2.Message:
    """Creates a new message of role "tool".

    Use this to add the result of a tool call to conversation history via `append`.
    """
    return chat_pb2.Message(role=chat_pb2.MessageRole.ROLE_TOOL, content=[text(result)])


def tool(name: str, description: str, parameters: dict[str, Any]) -> chat_pb2.Tool:
    """Creates a new tool for function calling in chat conversations.

    This function defines a tool that the model can call to perform specific tasks, such as executing a function
    with provided arguments. The tool is represented as a `chat_pb2.Tool` object, which includes a function
    specification with a name, description, and JSON schema for the parameters. The model uses this schema to
    generate valid JSON inputs for the function when it decides to call the tool. Tools are typically passed to
    the `create` method of a chat client to enable function calling in a conversation.

    Examples:
        Using a Pydantic model to define the parameter schema:
        ```python
        from pydantic import BaseModel, Field
        from xai_sdk import Client
        from xai_sdk.chat import system, tool

        class GetWeatherRequest(BaseModel):
            city: str = Field(description="The name of the city to get the weather for.")
            units: Literal["C", "F"] = Field(description="The units to use for the temperature.")

        client = Client()

        weather_tool = tool(
            name="get_weather",
            description="Get the weather for a given city.",
            parameters=GetWeatherRequest.model_json_schema(),
        )

        conversation = client.chat.create(
            model="grok-3",
            messages=[system("You are a helpful assistant.")],
            tools=[weather_tool],
        )
        ```

        Using an explicit JSON schema definition:
        ```python
        from xai_sdk import Client
        from xai_sdk.chat import system, tool

        client = Client()

        weather_tool = tool(
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
        )

        conversation = client.chat.create(
            model="grok-3",
            messages=[system("You are a helpful assistant.")],
            tools=[weather_tool],
        )
        ```

    Args:
        name: The name of the function that the model can call. This should be unique and descriptive
            (e.g., "get_weather").
        description: A brief description of what the function does, helping the model understand when to call it
            (e.g., "Get the weather for a given city.").
        parameters: A JSON schema dictionary or a dictionary derived from a Pydantic model's `model_json_schema()`
            that defines the structure and types of the function's input parameters.

    Returns:
        A `chat_pb2.Tool` object representing the function, which can be passed to the `tools` parameter of a
        chat client's `create` method.

    Note:
        - The `parameters` dictionary is serialized to a JSON string internally, so it must be JSON-serializable.
        - A maximum of 128 tools can be provided to a chat conversation.
        - The model decides whether to call the tool based on the conversation context and the tool's description.
    """
    return chat_pb2.Tool(
        function=chat_pb2.Function(
            name=name,
            description=description,
            parameters=json.dumps(parameters),
        )
    )


def required_tool(name: str) -> chat_pb2.ToolChoice:
    """Creates a new tool choice with function name `name`.

    Use this to force the model to always invoke a specific tool.
    `name` must be the name of a tool that has been provided in the `tools` parameter of a chat client's
    `create` method.
    """
    return chat_pb2.ToolChoice(function_name=name)


def text(content: str) -> chat_pb2.Content:
    """Returns a new content object of type text."""
    return chat_pb2.Content(text=content)


def image(image_url: str, *, detail: Optional[ImageDetail] = "auto") -> chat_pb2.Content:
    """Creates a new content object of type image for use in chat messages.

    Args:
        image_url: The URL or base64-encoded string of the image. Supported formats are PNG and JPG.
            If a URL is provided, the image is fetched for each API request without caching.
            Fetching uses the "XaiImageApiFetch/1.0" user agent with a 5-second timeout.
            The maximum image size is 10 MiB; larger images or failed fetches will cause the API request to fail.
        detail: Specifies the image resolution for model processing. One of:
        - `"auto"`: The system selects an appropriate resolution (default).
        - `"low"`: Uses a low-resolution image, reducing token usage and increasing speed.
        - `"high"`: Uses a high-resolution image, increasing token usage and processing time
            but capturing more detail.

    Returns:
        A `chat_pb2.Content` object representing the image content.
    """
    pb_detail = image_pb2.ImageDetail.DETAIL_AUTO
    if detail == "low":
        pb_detail = image_pb2.ImageDetail.DETAIL_LOW
    elif detail == "high":
        pb_detail = image_pb2.ImageDetail.DETAIL_HIGH

    return chat_pb2.Content(image_url=image_pb2.ImageUrlContent(image_url=image_url, detail=pb_detail))


def _process_content(content: Content) -> chat_pb2.Content:
    """Converts a `Content` type to a proto."""
    if isinstance(content, str):
        return text(content)
    else:
        return content


def _reasoning_effort_to_proto(effort: ReasoningEffort) -> chat_pb2.ReasoningEffort:
    """Converts a `ReasoningEffort` literal to a proto."""
    match effort:
        case "low":
            return chat_pb2.ReasoningEffort.EFFORT_LOW
        case "high":
            return chat_pb2.ReasoningEffort.EFFORT_HIGH
        case _:
            raise ValueError(f"Invalid reasoning effort: {effort}. Must be one of: {ReasoningEffort.__args__}")


def _tool_mode_to_proto(mode: ToolMode) -> chat_pb2.ToolMode:
    """Converts a `ToolMode` literal to a proto."""
    match mode:
        case "auto":
            return chat_pb2.ToolMode.TOOL_MODE_AUTO
        case "none":
            return chat_pb2.ToolMode.TOOL_MODE_NONE
        case "required":
            return chat_pb2.ToolMode.TOOL_MODE_REQUIRED
        case _:
            raise ValueError(f"Invalid tool mode: {mode}. Must be one of: {ToolMode.__args__}")


def _format_type_to_proto(format_type: ResponseFormat) -> chat_pb2.FormatType:
    """Converts a `FormatType` literal to a proto."""
    match format_type:
        case "text":
            return chat_pb2.FORMAT_TYPE_TEXT
        case "json_object":
            return chat_pb2.FORMAT_TYPE_JSON_OBJECT
        case "json_schema":
            return chat_pb2.FORMAT_TYPE_JSON_SCHEMA
        case _:
            raise ValueError(f"Invalid response format: {format_type}. Must be one of: {ResponseFormat.__args__}")


class Chunk(ProtoDecorator[chat_pb2.GetChatCompletionChunk]):
    """Adds convenience functions to the chunk proto."""

    _index: int

    def __init__(self, proto: chat_pb2.GetChatCompletionChunk, index: int):
        """Creates a new decorator instance.

        Args:
            proto: Chunk proto to wrap.
            index: Index of the response to track.
        """
        super().__init__(proto)
        self._index = index

    @property
    def choices(self) -> Sequence["ChoiceChunk"]:
        """Returns the choices belonging to this index."""
        return [ChoiceChunk(c) for c in self.proto.choices if c.index == self._index]

    @property
    def output(self) -> str:
        """Concatenates all chunks into a single string."""
        return "".join(c.content + c.reasoning_content for c in self.choices)

    @property
    def content(self) -> str:
        """Concatenates all content chunks into a single string."""
        return "".join(c.content for c in self.choices)

    @property
    def reasoning_content(self) -> str:
        """Concatenates all reasoning chunks into a single string."""
        return "".join(c.reasoning_content for c in self.choices)

    @property
    def citations(self) -> Sequence[str]:
        """Returns the citations of this chunk."""
        return self.proto.citations

    def __str__(self):
        """Concatenates all chunks into a single string."""
        return "".join(c.content + c.reasoning_content for c in self.choices)


class ChoiceChunk(ProtoDecorator[chat_pb2.ChoiceChunk]):
    """Adds convenience functions to the choice chunk proto."""

    @property
    def content(self) -> str:
        """Returns the main content/answer of this choice chunk."""
        return self.proto.delta.content

    @property
    def reasoning_content(self) -> str:
        """Returns the reasoning content of this choice chunk."""
        return self.proto.delta.reasoning_content

    @property
    def role(self) -> chat_pb2.MessageRole:
        """Returns the role of this choice chunk."""
        return self.proto.delta.role

    @property
    def tool_calls(self) -> Sequence[chat_pb2.ToolCall]:
        """Returns the tool calls of this choice chunk."""
        return self.proto.delta.tool_calls

    @property
    def finish_reason(self) -> sample_pb2.FinishReason:
        """Returns the finish reason of this choice chunk."""
        return self.proto.finish_reason


class _ResponseProtoDecorator(ProtoDecorator[chat_pb2.GetChatCompletionResponse]):
    def process_chunk(self, chunk: chat_pb2.GetChatCompletionChunk):
        # Consolidate the response.
        self._proto.usage.CopyFrom(chunk.usage)
        self._proto.created.CopyFrom(chunk.created)
        self._proto.id = chunk.id
        self._proto.model = chunk.model
        self._proto.system_fingerprint = chunk.system_fingerprint
        self._proto.citations.extend(chunk.citations)

        for c in chunk.choices:
            choice = self._proto.choices[c.index]
            choice.index = c.index
            choice.message.content += c.delta.content
            choice.message.reasoning_content += c.delta.reasoning_content
            choice.message.role = c.delta.role
            choice.message.tool_calls.extend(c.delta.tool_calls)
            choice.finish_reason = c.finish_reason


class Response(_ResponseProtoDecorator):
    """Response of a chat request."""

    # A single request can produce multiple responses. This index is used to retrieve the content of
    # a single answer from the response proto.
    _index: int
    # Cache to the answer indexed by this response.
    _choice: chat_pb2.Choice

    def __init__(self, response: chat_pb2.GetChatCompletionResponse, index: int) -> None:
        """Initializes a new instance of the `Response` class.

        Args:
            response: The response proto, which can hold multiple answers.
            index: The index of the answer this class exposes via its convenience methods.
        """
        super().__init__(response)
        self._index = index

        # Find and cache the answer identified by the index.
        choices = [c for c in response.choices if c.index == index]

        if not choices:
            raise ValueError(f"Invalid response proto or index. {response:} {index:}")
        elif len(choices) > 1:
            raise ValueError(f"More than one response for index {index:}. {response:}")
        else:
            self._choice = choices[0]

    @property
    def id(self) -> str:
        """Returns the id of this response."""
        return self.proto.id

    @property
    def content(self) -> str:
        """Returns the answer content of this response."""
        return self._choice.message.content

    @property
    def role(self) -> str:
        """Returns the role of this response."""
        return chat_pb2.MessageRole.Name(self._choice.message.role)

    @property
    def usage(self) -> usage_pb2.SamplingUsage:
        """Returns the usage of this response."""
        return self.proto.usage

    @property
    def reasoning_content(self) -> str:
        """Returns the reasoning trace generated by the model.

        This is only available for models that support reasoning.
        """
        return self._choice.message.reasoning_content

    @property
    def finish_reason(self) -> str:
        """Returns the finish reason of this response."""
        return sample_pb2.FinishReason.Name(self._choice.finish_reason)

    @property
    def logprobs(self) -> chat_pb2.LogProbs:
        """Returns the logprobs of this response."""
        return self._choice.logprobs

    @property
    def system_fingerprint(self) -> str:
        """Returns the system fingerprint of this response."""
        return self.proto.system_fingerprint

    @property
    def tool_calls(self) -> Sequence[chat_pb2.ToolCall]:
        """Returns the tool calls of this response."""
        return self._choice.message.tool_calls

    @property
    def citations(self) -> Sequence[str]:
        """Returns the citations of this response."""
        return self.proto.citations


class PollTimer:
    """Utility for making sure the request timeout is not exceeded when polling.

    When polling, there is no persistent connection to the server that can time out. Instead, we
    have to manually keep track of time.
    """

    def __init__(
        self, timeout: Optional[datetime.timedelta] = None, interval: Optional[datetime.timedelta] = None
    ) -> None:
        """Creates a new instance of the `PollTimer` class.

        Args:
            timeout: Maximum time to wait before aborting the RPC.
            interval: Time to wait between polls.
        """
        self._start = time.time()
        self._timeout = timeout or datetime.timedelta(minutes=10)
        self._interval = interval or datetime.timedelta(milliseconds=100)

    def sleep_interval_or_raise(self) -> float:
        """Returns the time to sleep until the next poll.

        Returns:
            Time to sleep until the next poll.

        Raises:
            TimeoutError when the total polling time is used up.
        """
        runtime = time.time() - self._start
        if runtime > self._timeout.total_seconds():
            raise TimeoutError(f"Polling timed out after {runtime} seconds.")
        else:
            return min(self._timeout.total_seconds() - runtime, self._interval.total_seconds())
