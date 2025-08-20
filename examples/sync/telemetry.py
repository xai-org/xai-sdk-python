from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.telemetry import Telemetry


def no_telemetry_example(client: Client):
    """
    Example without telemetry - no traces will be collected.
    """
    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = chat.sample()
    print(f"Response: {response.content}")


def console_export_example(client: Client):
    """
    Export traces to console for debugging and development.
    """
    telemetry = Telemetry()
    telemetry.setup_console_exporter()

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = chat.sample()
    print(f"Response: {response.content}")


def otlp_export_example(client: Client):
    """
    Export traces to an OTLP-compatible backend.

    This example respects OpenTelemetry environment variables:
    - OTEL_EXPORTER_OTLP_PROTOCOL (default: "http/protobuf")
    - OTEL_EXPORTER_OTLP_ENDPOINT
    - OTEL_EXPORTER_OTLP_HEADERS
    """
    telemetry = Telemetry()
    telemetry.setup_otlp_exporter()

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = chat.sample()
    print(f"Response: {response.content}")


def custom_tracer_provider_example(client: Client):
    """
    Example using a custom TracerProvider, useful for applications that already have a TracerProvider.
    """

    tracer_provider = TracerProvider(resource=Resource.create({"service.name": "xai-sdk-example"}))
    trace.set_tracer_provider(tracer_provider)

    telemetry = Telemetry(tracer_provider)
    telemetry.setup_otlp_exporter()

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = chat.sample()
    print(f"Response: {response.content}")


def main():
    client = Client()

    # Uncomment the example you want to run:

    # No telemetry (baseline)
    # no_telemetry_example(client)

    # Console export (for debugging)
    console_export_example(client)

    # OTLP export (make sure you have the relevant environment variables set)
    # otlp_export_example(client)

    # Custom tracer provider
    # custom_tracer_provider_example(client)


if __name__ == "__main__":
    main()
