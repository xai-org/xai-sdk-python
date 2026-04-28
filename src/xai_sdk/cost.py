"""Helpers for surfacing cost information from `usage_pb2.SamplingUsage`."""

from typing import Optional

from .proto import usage_pb2

# 1 tick == 1e-10 USD. See `cost_in_usd_ticks` in `usage.proto` in https://github.com/xai-org/xai-proto/blob/0c0f5353aa7ab2a4ffea310f9d9364ed5c424af2/proto/xai/api/v1/usage.proto#L45.
USD_PER_TICK = 1e-10


def cost_usd_from_usage(usage: usage_pb2.SamplingUsage) -> Optional[float]:
    """Returns the request cost in USD, or None if the server did not report it."""
    if not usage.HasField("cost_in_usd_ticks"):
        return None
    return usage.cost_in_usd_ticks * USD_PER_TICK
