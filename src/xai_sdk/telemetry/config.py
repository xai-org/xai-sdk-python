import os
from typing import Optional

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor

from xai_sdk.__about__ import __version__ as xai_sdk_version


class Telemetry:
    """Telemetry configuration and tracing setup for the xAI SDK.

    This class provides OpenTelemetry-based distributed tracing capabilities for monitoring
    and debugging xAI SDK operations. It allows you to configure span processors to export
    telemetry data to observability platforms.

    The Telemetry class handles TracerProvider setup and configuration. You can either provide
    your own TracerProvider instance for custom configuration, or let the class create one
    automatically with sensible defaults. When a TracerProvider is auto-created, it becomes
    the global OpenTelemetry tracer provider for the entire process. The class then handles
    the configuration of different span processors (OTLP, Console) to send telemetry data
    to your preferred destinations.

    All standard OpenTelemetry environment variables are respected, including:
    - OTEL_EXPORTER_OTLP_PROTOCOL: Export protocol ("grpc" or "http/protobuf")
    - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint URL
    - OTEL_EXPORTER_OTLP_HEADERS: Authentication headers (e.g., "Authorization=Bearer token")
    - And many others as defined in the OpenTelemetry specification

    Additionally, the following xAI SDK specific environment variables are supported:
    - XAI_SDK_DISABLE_TRACING: Disables all tracing if set to "1" or "true"
    - XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES: Disables collection of sensitive attributes
      (user inputs, AI responses, prompts) in traces if set to "1" or "true"

    Examples:
        Basic setup with console output for development:
        ```python
        from xai_sdk import Client
        from xai_sdk.chat import user
        from xai_sdk.telemetry import Telemetry

        # Initialize telemetry with console output
        telemetry = Telemetry()
        telemetry.setup_console_exporter()

        # Now all SDK operations will emit traces to the console

        client = Client()
        chat = client.chat.create(model="grok-3")
        chat.append(user("Hello, how are you?"))
        response = chat.sample()
        ```

        Setup with OTLP exporter for production monitoring:
        ```python
        from xai_sdk import Client
        from xai_sdk.chat import user
        from xai_sdk.telemetry import Telemetry

        # Initialize telemetry with OTLP exporter
        telemetry = Telemetry()
        telemetry.setup_otlp_exporter(
            endpoint="https://your-observability-platform.com/traces",
            headers={"Authorization": "Bearer your-token"}
        )

        # All SDK operations will now send traces to your observability platform
        client = Client()
        chat = client.chat.create(model="grok-3")
        chat.append(user("Hello, how are you?"))
        response = chat.sample()
        ```

        Custom TracerProvider configuration:
        ```python
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from xai_sdk import Client
        from xai_sdk.telemetry import Telemetry

        # Create custom provider with specific configuration
        custom_resource = Resource.create({"service.name": "my-app"})
        custom_provider = TracerProvider(resource=custom_resource)

        # Use custom provider (won't set as global tracer provider)
        telemetry = Telemetry(provider=custom_provider)
        telemetry.setup_otlp_exporter()
        ```
    """

    def __init__(self, provider: Optional[TracerProvider] = None):
        """Initialize the Telemetry instance with TracerProvider setup.

        If no provider is given, creates a new TracerProvider with xAI SDK service metadata
        and sets it as the global OpenTelemetry tracer provider. If a provider is provided,
        uses it directly without modifying global state.

        Args:
            provider: Optional TracerProvider instance. If None, a new provider will be
                created automatically with appropriate service name and version metadata,
                and set as the global tracer provider for the process.
        """
        self.provider = provider or self._setup_provider()

    def _setup_provider(self) -> TracerProvider:
        """Setup the provider for the tracer."""
        resource = Resource.create(
            attributes={
                SERVICE_NAME: "xai-sdk",
                SERVICE_VERSION: xai_sdk_version,
            }
        )
        self.provider = TracerProvider(resource=resource)
        otel_trace.set_tracer_provider(self.provider)
        return self.provider

    def setup_otlp_exporter(self, **kwargs):
        """Configure OTLP (OpenTelemetry Protocol) trace exporter for sending telemetry data.

        Sets up an OTLP exporter to send traces to observability platforms like Jaeger,
        Langfuse, etc. The protocol (gRPC or HTTP) is determined by the
        OTEL_EXPORTER_OTLP_PROTOCOL environment variable, defaulting to "http/protobuf".

        Note:
            The OTLP exporter is not available in the Python SDK by default.
            You must install the optional telemetry dependencies to use this feature.
            For HTTP/Protobuf support, install with:
                pip install xai-sdk[telemetry-http] or uv add xai-sdk[telemetry-http]
            For gRPC support, install with:
                pip install xai-sdk[telemetry-grpc] or uv add xai-sdk[telemetry-grpc]

        Args:
            **kwargs: Additional arguments passed to the OTLPSpanExporter constructor.
                Common arguments include:
                - endpoint: OTLP endpoint URL (can also be set via OTEL_EXPORTER_OTLP_ENDPOINT)
                - headers: Authentication headers dict (can also be set via OTEL_EXPORTER_OTLP_HEADERS)
                - timeout: Request timeout in seconds (can also be set via OTEL_EXPORTER_OTLP_TIMEOUT)

        Raises:
            ValueError: If OTEL_EXPORTER_OTLP_PROTOCOL is set to an invalid value.
        """
        protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf").lower()

        if protocol == "grpc":
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
            except ImportError as exc:
                raise ImportError("Please install 'xai-sdk[telemetry-grpc]' to use gRPC OTLP exporter.") from exc
        elif protocol == "http/protobuf":
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
            except ImportError as exc:
                raise ImportError(
                    "Please install 'xai-sdk[telemetry-http]' to use HTTP/Protobuf OTLP exporter."
                ) from exc
        else:
            raise ValueError(f"Unsupported OTLP protocol: {protocol}. Valid options: 'grpc', 'http/protobuf'.")

        self.provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    **kwargs,
                )
            )
        )

    def setup_console_exporter(self, **kwargs):
        """Configure console trace exporter for debugging and development.

        Sets up a console exporter that prints trace data to stdout, useful for
        development, debugging, and testing. Traces are formatted as human-readable
        JSON output showing span details, timing, and attributes.

        Args:
            **kwargs: Additional arguments passed to the OpenTelemetry ConsoleSpanExporter constructor.
        """
        self.provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter(**kwargs)))


def get_tracer(name: str) -> otel_trace.Tracer:
    """Get an OpenTelemetry tracer for the given name.

    If the XAI_SDK_DISABLE_TRACING environment variable is set to "1" or "true", returns a NoOpTracer.
    This allows you to selectively disable xAI SDK related tracing.
    """
    if os.getenv("XAI_SDK_DISABLE_TRACING", "0").lower() in ["1", "true"]:
        return otel_trace.NoOpTracer()
    return otel_trace.get_tracer(name)


def should_disable_sensitive_attributes() -> bool:
    """Check if sensitive attributes should be disabled in telemetry.

    Returns True if XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES is set to "1" or "true".
    """
    return os.getenv("XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES", "0").lower() in ["1", "true"]
