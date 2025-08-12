import os
from unittest import mock

import pytest
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider

from xai_sdk.__about__ import __version__ as xai_sdk_version
from xai_sdk.telemetry import Telemetry, get_tracer


def test_telemetry_creates_provider():
    telemetry = Telemetry()

    assert telemetry.provider is not None
    assert isinstance(telemetry.provider, TracerProvider)
    current_provider = otel_trace.get_tracer_provider()
    assert current_provider is telemetry.provider

    resource = telemetry.provider.resource
    attributes = resource.attributes

    assert attributes[SERVICE_NAME] == "xai-sdk"
    assert attributes[SERVICE_VERSION] == xai_sdk_version


def test_telemetry_uses_provided_provider():
    custom_provider = TracerProvider()
    telemetry = Telemetry(provider=custom_provider)

    assert telemetry.provider is custom_provider
    # Check that the global provider is not the custom provider
    assert otel_trace.get_tracer_provider() is not custom_provider


def test_get_tracer_returns_tracer_by_default():
    tracer = get_tracer("test-tracer")
    assert isinstance(tracer, otel_trace.Tracer)
    assert not isinstance(tracer, otel_trace.NoOpTracer)


def test_get_tracer_returns_tracer_when_enabled():
    with mock.patch.dict(os.environ, {"XAI_SDK_DISABLE_TRACING": "0"}):
        tracer = get_tracer("test-tracer")
        assert isinstance(tracer, otel_trace.Tracer)
        assert not isinstance(tracer, otel_trace.NoOpTracer)


@pytest.mark.parametrize("disable_value", ["1", "true", "True", "TRUE"])
def test_get_tracer_returns_noop_tracer_when_disabled(disable_value):
    with mock.patch.dict(os.environ, {"XAI_SDK_DISABLE_TRACING": disable_value}):
        tracer = get_tracer("test-tracer")
        assert isinstance(tracer, otel_trace.NoOpTracer)
