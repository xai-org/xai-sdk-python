<div align="center">
  <img src="https://avatars.githubusercontent.com/u/130314967?s=200&v=4" alt="xAI Logo" width="100" />
  <h1>xAI Python SDK</h1>
  <p>The official Python SDK for xAI's APIs</p>
  <a href="https://pypi.org/project/xai-sdk">
    <img src="https://img.shields.io/pypi/v/xai-sdk" alt="PyPI Version" />
  </a>
  <a href="">
    <img src="https://img.shields.io/pypi/l/xai-sdk" alt="License" />
  </a>
  <a href="">
    <img src="https://img.shields.io/pypi/pyversions/xai-sdk" alt="Python Version" />
  </a>
</div>

<br>

The xAI Python SDK is a gRPC-based Python library for interacting with xAI's APIs. Built for Python 3.10 and above, it offers both **synchronous** and **asynchronous** clients.

Whether you're generating text, images, or structured outputs, the xAI SDK is designed to be intuitive, robust, and developer-friendly.

## Documentation

Comprehensive documentation is available at [docs.x.ai](https://docs.x.ai). Explore detailed guides, API references, and tutorials to get the most out of the xAI SDK.

## Installation

Install from PyPI with pip.

```bash
pip install xai-sdk
```

Alternatively you can also use [uv](https://docs.astral.sh/uv/)

```bash
uv add xai-sdk
```

### Requirements
Python 3.10 or higher is required to use the xAI SDK.

## Usage

The xAI SDK supports both synchronous (`xai_sdk.Client`) and asynchronous (`xai_sdk.AsyncClient`) clients. For a complete set of examples demonstrating the SDK's capabilities, including authentication, chat, image generation, function calling, and more, refer to the [examples folder](/examples).

### Client Instantiation

To use the xAI SDK, you need to instantiate either a synchronous or asynchronous client. By default, the SDK looks for an environment variable named `XAI_API_KEY` for authentication. If this variable is set, you can instantiate the clients without explicitly passing the API key:

```python
from xai_sdk import Client, AsyncClient

# Synchronous client
sync_client = Client()

# Asynchronous client
async_client = AsyncClient()
```

If you prefer to explicitly pass the API key, you can do so using `os.getenv` or by loading it from a `.env` file using the `python-dotenv` package:

```python
import os
from dotenv import load_dotenv
from xai_sdk import Client, AsyncClient

load_dotenv()

api_key = os.getenv("XAI_API_KEY")
sync_client = Client(api_key=api_key)
async_client = AsyncClient(api_key=api_key)
```

Make sure to set the `XAI_API_KEY` environment variable or load it from a `.env` file before using the SDK. This ensures secure handling of your API key without hardcoding it into your codebase.

### Multi-Turn Chat (Synchronous)

The xAI SDK supports multi-turn conversations with a simple `append` method to manage conversation history, making it ideal for interactive applications.

First, create a `chat` instance, start `append`ing messages to it, and finally call `sample` to yield a response from the model. While the underlying APIs are still stateless, this approach makes it easy to manage the message history.

```python
from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client()
chat = client.chat.create(
    model="grok-3",
    messages=[system("You are a pirate assistant.")]
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

### Multi-Turn Chat (Asynchronous)

For async usage, simply import `AsyncClient` instead of `Client`.

```python
import asyncio
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user

async def main():
    client = AsyncClient()
    chat = client.chat.create(
        model="grok-3",
        messages=[system("You are a pirate assistant.")]
    )

    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break
        chat.append(user(prompt))
        response = await chat.sample()
        print(f"Grok: {response.content}")
        chat.append(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming

The xAI SDK supports streaming responses, allowing you to process model outputs in real-time, which is ideal for interactive applications like chatbots. The `stream` method returns a tuple containing `response` and `chunk`. The chunks contain the text deltas from the stream, while the `response` variable automatically accumulates the response as the stream progresses.

```python
from xai_sdk import Client
from xai_sdk.chat import user

client = Client()
chat = client.chat.create(model="grok-3")

while True:
    prompt = input("You: ")
    if prompt.lower() == "exit":
        break
    chat.append(user(prompt))
    print("Grok: ", end="", flush=True)
    for response, chunk in chat.stream():
        print(chunk.content, end="", flush=True)
    print()
    chat.append(response)
```

### Image Understanding

You can easily interleave images and text together, making tasks like image understanding and analysis easy.

```python
from xai_sdk import Client
from xai_sdk.chat import image, user

client = Client()
chat = client.chat.create(model="grok-2-vision")

chat.append(
    user(
        "Which animal looks happier in these images?",
        image("https://images.unsplash.com/photo-1561037404-61cd46aa615b"),   # Puppy
        image("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba") # Kitten
    )
)
response = chat.sample()
print(f"Grok: {response.content}")
```

## Advanced Features

The xAI SDK excels in advanced use cases, such as:

- **Function Calling**: Define tools and let the model intelligently call them (see sync [function_calling.py](/examples/sync/function_calling.py) and async [function_calling.py](/examples/aio/function_calling.py)).
- **Image Generation**: Generate images with image generation models (see sync [image_generation.py](/examples/sync/image_generation.py) and async [image_generation.py](/examples/aio/image_generation.py)).
- **Image Understanding**: Analyze images with vision models (see sync [image_understanding.py](/examples/sync/image_understanding.py) and async [image_understanding.py](/examples/aio/image_understanding.py)).
- **Structured Outputs**: Return model responses as structured objects in the form of Pydantic models (see sync [structured_outputs.py](/examples/sync/structured_outputs.py) and async [structured_outputs.py](/examples/aio/structured_outputs.py)).
- **Reasoning Models**: Leverage reasoning-focused models with configurable effort levels (see sync [reasoning.py](/examples/sync/reasoning.py) and async [reasoning.py](/examples/aio/reasoning.py)).
- **Deferred Chat**: Sample a long-running response from a model via polling (see sync [deferred_chat.py](/examples/sync/deferred_chat.py) and async [deferred_chat.py](/examples/aio/deferred_chat.py)).
- **Tokenization**: Tokenize text with the tokenizer API (see sync [tokenizer.py](/examples/sync/tokenizer.py) and async [tokenizer.py](/examples/aio/tokenizer.py)).
- **Models**: Retrieve information on different models available to you, including, name, aliases, token price, max prompt length etc (see sync [models.py](/examples/sync/models.py) and async [models.py](/examples/aio/models.py))
- **Live Search**: Augment Grok's knowledge with up-to-date information from the web and 𝕏 (see sync [search.py](/examples/sync/search.py) and async [search.py](/examples/aio/search.py))
- **Telemetry & Observability**: Export OpenTelemetry traces with rich metadata attributes to console or OTLP backends (see sync [telemetry.py](/examples/sync/telemetry.py) and async [telemetry.py](/examples/aio/telemetry.py))

## Telemetry & Observability

The xAI SDK includes the option to export OpenTelemetry traces to the console or an OTLP compatible backend. Exporting telemetry is not enabled by default, and you must explicitly configure this in code to start exporting traces.

When enabled, each API call automatically generates detailed traces (spans) that capture the complete execution flow of that call, as well as rich metadata including attributes such as input prompts, model responses, and token usage statistics.
When consumed by an observability platform which can visualize these traces, this makes it easy to monitor, debug, and analyze your applications' performance and behavior.

The attributes on the generated traces *largely* follow the [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/), meaning Otel backends that support these conventions, such as Langfuse can visualize these traces in a structured way.

In some cases, where there is no corresponding standard in the OpenTelemetry GenAI semantic conventions, the xAI SDK adds some additional attributes to particular traces that users may find useful.

### Export Options

#### Console Export (Development)

Console export prints trace data in JSON format directly to your console:

```python
from xai_sdk.telemetry import Telemetry

telemetry = Telemetry()
telemetry.setup_console_exporter()

client = Client()

# The call to sample will now generate a trace that you will be able to see in the console
chat = client.chat.create(model="grok-3")
chat.append(user("Hello, how are you?"))
response = chat.sample()
print(f"Response: {response.content}")
```

#### OTLP Export (Production)

For production environments, send traces to observability platforms like Jaeger, Langfuse, or any OTLP-compliant backend:

```python
from xai_sdk.telemetry import Telemetry

telemetry = Telemetry()
telemetry.setup_otlp_exporter(
    endpoint="https://your-observability-platform.com/traces",
    headers={"Authorization": "Bearer your-token"}
)

client = Client()

# The call to sample will now generate a trace that you will be able to see in your observability platform
chat = client.chat.create(model="grok-3")
chat.append(user("Hello, how are you?"))
response = chat.sample()
print(f"Response: {response.content}")
```

You can also set the environment variables `OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_EXPORTER_OTLP_ENDPOINT`, and `OTEL_EXPORTER_OTLP_HEADERS` to configure the exporter. If you set the environment variables, you don't need pass any parameters to the `setup_otlp_exporter` method directly.

### Installation Requirements

The telemetry feature requires additional dependencies based on your export needs:

```bash
# For HTTP OTLP export
pip install xai-sdk[telemetry-http]
# or
uv add xai-sdk[telemetry-http]

# For gRPC OTLP export
pip install xai-sdk[telemetry-grpc]
# or
uv add xai-sdk[telemetry-grpc]
```

### Environment Variables

The telemetry system respects all standard OpenTelemetry environment variables:

- `OTEL_EXPORTER_OTLP_PROTOCOL`: Export protocol ("grpc" or "http/protobuf")
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP endpoint URL
- `OTEL_EXPORTER_OTLP_HEADERS`: Authentication headers

### Advanced Configuration

#### Custom TracerProvider

You may be using the xAI SDK within an application that is already using OpenTelemetry. In this case, you can provide/re-use your own TracerProvider for the xAI SDK to make use of.

```python
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from xai_sdk.telemetry import Telemetry

# Create custom provider with specific configuration
custom_resource = Resource.create({"service.name": "my-app"})
custom_provider = TracerProvider(resource=custom_resource)

# Use the custom tracer provider
telemetry = Telemetry(provider=custom_provider)
telemetry.setup_otlp_exporter()
```

### Disabling Tracing

If you're using the xAI SDK within an application that is already using OpenTelemetry to export other traces, you may want to selectively disable xAI SDK traces only, this can be done by setting the environment variable `XAI_SDK_DISABLE_TRACING` to `1` or `true`.

## Timeouts

The xAI SDK allows you to set a timeout for API requests during client initialization. This timeout applies to all RPCs and methods used with that client instance. The default timeout is 15 minutes (900 seconds).

It is not currently possible to specify timeouts for an individual RPC/client method.

To set a custom timeout, pass the `timeout` parameter when creating the `Client` or `AsyncClient`. The timeout is specified in seconds.

Example for synchronous client:

```python
from xai_sdk import Client

# Set timeout to 5 minutes (300 seconds)
sync_client = Client(timeout=300)
```

Example for asynchronous client:

```python
from xai_sdk import AsyncClient

# Set timeout to 5 minutes (300 seconds)
async_client = AsyncClient(timeout=300)
```

In the case of a timeout, a `grpc.RpcError` (for synchronous clients) or `grpc.aio.AioRpcError` (for asynchronous clients) will be raised with the gRPC status code `grpc.StatusCode.DEADLINE_EXCEEDED`.

## Retries

The xAI SDK has retries enabled by default for certain types of failed requests. If the service returns an `UNAVAILABLE` error, the SDK will automatically retry the request with exponential backoff. The default retry policy is configured as follows:

- **Maximum Attempts**: 5
- **Initial Backoff**: 0.1 seconds
- **Maximum Backoff**: 1 second
- **Backoff Multiplier**: 2

This means that after an initial failure, the SDK will wait 0.1 seconds before the first retry, then 0.2 seconds, 0.4 seconds, and so on, up to a maximum of 1 second between attempts, for a total of up to 5 attempts.

You can disable retries by setting the `grpc.enable_retries` channel option to `0` when initializing the client:

```python
from xai_sdk import Client

# Disable retries
sync_client = Client(channel_options=[("grpc.enable_retries", 0)])
```

Similarly, for the asynchronous client:

```python
from xai_sdk import AsyncClient

# Disable retries
async_client = AsyncClient(channel_options=[("grpc.enable_retries", 0)])
```

#### Custom Retry Policy

You can configure your own retry policy by setting the `grpc.service_config` channel option with a JSON string that defines the retry behavior. The JSON structure should follow the gRPC service config format. Here's an example of how to set a custom retry policy:

```python
import json
from xai_sdk import Client

# Define a custom retry policy
custom_retry_policy = json.dumps({
    "methodConfig": [{
        "name": [{}], # Applies to all methods
        "retryPolicy": {
            "maxAttempts": 3,         # Reduced number of attempts
            "initialBackoff": "0.5s", # Longer initial wait
            "maxBackoff": "2s",       # Longer maximum wait
            "backoffMultiplier": 1.5, # Slower increase in wait time
            "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"] # Additional status code for retry
        }
    }]
})

# Initialize client with custom retry policy
sync_client = Client(channel_options=[
    ("grpc.service_config", custom_retry_policy)
])
```

Similarly, for the asynchronous client:

```python
import json
from xai_sdk import AsyncClient

# Define a custom retry policy
custom_retry_policy = json.dumps({
    "methodConfig": [{
        "name": [{}], # Applies to all methods
        "retryPolicy": {
            "maxAttempts": 3,         # Reduced number of attempts
            "initialBackoff": "0.5s", # Longer initial wait
            "maxBackoff": "2s",       # Longer maximum wait
            "backoffMultiplier": 1.5, # Slower increase in wait time
            "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"] # Additional status code for retry
        }
    }]
})

# Initialize async client with custom retry policy
async_client = AsyncClient(channel_options=[
    ("grpc.service_config", custom_retry_policy)
])
```

In this example, the custom policy reduces the maximum number of attempts to 3, increases the initial backoff to 0.5 seconds, sets a maximum backoff of 2 seconds, uses a smaller backoff multiplier of 1.5, and allows retries on both `UNAVAILABLE` and `RESOURCE_EXHAUSTED` status codes.

Note that when setting a custom `grpc.service_config`, it will override the default retry policy.

## Accessing Underlying Proto Objects

In rare cases, you might need to access the raw proto object returned from an API call. While the xAI SDK is designed to expose most commonly needed fields directly on the response objects for ease of use, there could be scenarios where accessing the underlying proto object is necessary for advanced or custom processing.

You can access the raw proto object on any response by using the `.proto` attribute. Here's an example of how to do this with a chat response:

```python
from xai_sdk import Client
from xai_sdk.chat import user

client = Client()
chat = client.chat.create(model="grok-3")
chat.append(user("Hello, how are you?"))
response = chat.sample()

# Access the underlying proto object
# In this case, this will be of type xai_sdk.proto.chat_pb2.GetChatCompletionResponse
proto_object = response.proto
print(proto_object)
```

Please note that you should rarely need to interact with the proto object directly, as the SDK is built to provide a more user-friendly interface to the data. Use this approach only when specific fields or data structures not exposed by the SDK are required for your application. If you find yourself needing to regularly access the proto object directly, please consider opening an issue so that we can improve the experience.

## Error Codes

When using the xAI SDK, you may encounter various error codes returned by the API. These errors are based on gRPC status codes and provide insight into what went wrong with a request. For the synchronous client (`Client`), errors will be of type `grpc.RpcError`, while for the asynchronous client (`AsyncClient`), errors will be of type `grpc.aio.AioRpcError`.

Below is a table of common gRPC status codes you might encounter when using the xAI SDK:

| gRPC Status Code          | Meaning                                                                | xAI SDK/API Context                                                                                     |
|---------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `UNKNOWN`                 | An unknown error occurred.                                             | An unexpected issue occurred on the server side, not specifically related to the request.               |
| `INVALID_ARGUMENT`        | The client specified an invalid argument.                              | An invalid argument was provided to the model/endpoint, such as incorrect parameters or malformed input.|
| `DEADLINE_EXCEEDED`       | The deadline for the request expired before the operation completed.   | Raised if the request exceeds the timeout specified by the client (default is 900 seconds, configurable during client instantiation). |
| `NOT_FOUND`               | A specified resource was not found.                                    | A requested model or resource does not exist.                                                           |
| `PERMISSION_DENIED`       | The caller does not have permission to execute the specified operation.| The API key is disabled, blocked, or lacks sufficient permissions to access a specific model or feature. |
| `UNAUTHENTICATED`         | The request does not have valid authentication credentials.            | The API key is missing, invalid, or expired.                                                            |
| `RESOURCE_EXHAUSTED`      | A resource quota has been exceeded (e.g., rate limits).                | The user has exceeded their API usage quota or rate limits for requests.                                |
| `INTERNAL`                | An internal error occurred.                                            | An internal server error occurred on the xAI API side.                                                  |
| `UNAVAILABLE`             | The service is currently unavailable. This is often a transient error. | The model or endpoint invoked is temporarily down or there are connectivity issues. The SDK defaults to automatically retrying errors with this status code. |
| `DATA_LOSS`               | Unrecoverable data loss or corruption occurred.                        | Occurs when a user provides an image via URL in API calls (e.g., in a chat conversation) and the server fails to fetch the image from that URL. |

These error codes can help diagnose issues with API requests. When handling errors, ensure you check the specific status code to understand the nature of the problem and take appropriate action.

## Versioning

The xAI SDK generally follows [Semantic Versioning (SemVer)](https://semver.org/) to ensure a clear and predictable approach to versioning. Semantic Versioning uses a three-part version number in the format `MAJOR.MINOR.PATCH`, where:

- **MAJOR** version increments indicate backwards-incompatible API changes.
- **MINOR** version increments indicate the addition of backward-compatible functionality.
- **PATCH** version increments indicate backward-compatible bug fixes.

This approach helps developers understand the impact of upgrading to a new version of the SDK. We strive to maintain backward compatibility in minor and patch releases, ensuring that your applications continue to work seamlessly. However, please note that while we aim to restrict breaking changes to major version updates, some backwards incompatible changes to library internals may occasionally occur in minor or patch releases. These changes will typically not affect the public API, but if you are interacting with internal components or structures, we recommend reviewing release notes for each update to avoid unexpected issues.

This project maintains a [changelog](/CHANGELOG.md) such that developers can track updates and changes to the SDK as new versions are released.

### Determining the Installed Version

You can easily check the version of the xAI SDK installed in your environment using either of the following methods:

- **Using pip/uv**: Run the following command in your terminal to see the installed version of the SDK:
  ```bash
  pip show xai-sdk
  ```
  or 

  ```bash
  uv pip show xai-sdk
  ```
  
  This will display detailed information about the package, including the version number.

- **Programmatically in Python**: You can access the version information directly in your code by importing the SDK and checking the `__version__` attribute:
  ```python
  import xai_sdk
  print(xai_sdk.__version__)
  ```

These methods allow you to confirm which version of the xAI SDK you are currently using, which can be helpful for debugging or ensuring compatibility with specific features.

## License

The xAI SDK is distributed under the Apache-2.0 License

## Contributing

See the [documentation](/CONTRIBUTING.md) on contributing to this project.