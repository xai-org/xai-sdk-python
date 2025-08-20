import asyncio

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

from xai_sdk import AsyncClient
from xai_sdk.chat import user
from xai_sdk.telemetry import Telemetry


async def no_telemetry_example(client: AsyncClient):
    """
    Example without telemetry - no traces will be collected.
    """
    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()
    print(f"Response: {response.content}")


async def console_export_example(client: AsyncClient):
    """
    Export traces to console for debugging and development.
    """
    telemetry = Telemetry()
    telemetry.setup_console_exporter()

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()
    print(f"Response: {response.content}")


async def otlp_export_example(client: AsyncClient):
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
    response = await chat.sample()
    print(f"Response: {response.content}")


async def custom_tracer_provider_example(client: AsyncClient):
    """
    Example using a custom TracerProvider, useful for applications that already have a TracerProvider.
    """

    tracer_provider = TracerProvider(resource=Resource.create({"service.name": "xai-sdk-example"}))
    trace.set_tracer_provider(tracer_provider)

    telemetry = Telemetry(tracer_provider)
    telemetry.setup_otlp_exporter()

    chat = client.chat.create(model="grok-3")
    chat.append(user("Hello, how are you?"))
    response = await chat.sample()
    print(f"Response: {response.content}")


async def main():
    client = AsyncClient()

    # Uncomment the example you want to run:

    # No telemetry (baseline)
    # await no_telemetry_example(client)

    # Console export (for debugging)
    await console_export_example(client)

    # OTLP export (make sure you have the relevant environment variables set)
    # await otlp_export_example(client)

    # Custom tracer provider
    # await custom_tracer_provider_example(client)


if __name__ == "__main__":
    asyncio.run(main())
