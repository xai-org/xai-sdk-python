import collections

import pytest

from xai_sdk.interceptors import (
    AuthInterceptor,
    StreamStreamAuthAioInterceptor,
    StreamStreamTimeoutAioInterceptor,
    StreamUnaryAuthAioInterceptor,
    StreamUnaryTimeoutAioInterceptor,
    TimeoutInterceptor,
    UnaryStreamAuthAioInterceptor,
    UnaryStreamTimeoutAioInterceptor,
    UnaryUnaryAuthAioInterceptor,
    UnaryUnaryTimeoutAioInterceptor,
)

_CallDetails = collections.namedtuple(
    "_CallDetails", ["method", "timeout", "metadata", "credentials", "wait_for_ready", "compression"]
)

_RPC_KINDS = ["unary_unary", "unary_stream", "stream_unary", "stream_stream"]

_EXPECTED_METADATA = [("existing", "value"), ("authorization", "Bearer test-key"), ("custom", "header")]


def _call_details() -> _CallDetails:
    return _CallDetails("/xai_api.Test/Method", None, [("existing", "value")], None, None, None)


def _continuation(client_call_details, request):
    return client_call_details, request


async def _async_continuation(client_call_details, request):
    return client_call_details, request


@pytest.mark.parametrize("rpc_kind", _RPC_KINDS)
def test_auth_interceptor_adds_metadata_for_every_rpc_kind(rpc_kind):
    interceptor = AuthInterceptor("test-key", (("custom", "header"),))
    intercept = getattr(interceptor, f"intercept_{rpc_kind}")

    details, request = intercept(_continuation, _call_details(), "request")

    assert details.metadata == _EXPECTED_METADATA
    assert request == "request"


@pytest.mark.parametrize("rpc_kind", _RPC_KINDS)
def test_timeout_interceptor_sets_timeout_for_every_rpc_kind(rpc_kind):
    interceptor = TimeoutInterceptor(42)
    intercept = getattr(interceptor, f"intercept_{rpc_kind}")

    details, request = intercept(_continuation, _call_details(), "request")

    assert details.timeout == 42
    assert request == "request"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("interceptor_cls", "rpc_kind"),
    [
        (UnaryUnaryAuthAioInterceptor, "unary_unary"),
        (UnaryStreamAuthAioInterceptor, "unary_stream"),
        (StreamUnaryAuthAioInterceptor, "stream_unary"),
        (StreamStreamAuthAioInterceptor, "stream_stream"),
    ],
)
async def test_async_auth_interceptors_add_metadata(interceptor_cls, rpc_kind):
    interceptor = interceptor_cls("test-key", (("custom", "header"),))
    intercept = getattr(interceptor, f"intercept_{rpc_kind}")

    details, request = await intercept(_async_continuation, _call_details(), "request")

    assert details.metadata == _EXPECTED_METADATA
    assert request == "request"


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("interceptor_cls", "rpc_kind"),
    [
        (UnaryUnaryTimeoutAioInterceptor, "unary_unary"),
        (UnaryStreamTimeoutAioInterceptor, "unary_stream"),
        (StreamUnaryTimeoutAioInterceptor, "stream_unary"),
        (StreamStreamTimeoutAioInterceptor, "stream_stream"),
    ],
)
async def test_async_timeout_interceptors_set_timeout(interceptor_cls, rpc_kind):
    interceptor = interceptor_cls(42)
    intercept = getattr(interceptor, f"intercept_{rpc_kind}")

    details, request = await intercept(_async_continuation, _call_details(), "request")

    assert details.timeout == 42
    assert request == "request"
