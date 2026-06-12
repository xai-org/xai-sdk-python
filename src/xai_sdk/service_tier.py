from .proto import usage_pb2
from .types.common import ServiceTier

__all__ = [
    "ServiceTierMap",
    "service_tier_from_proto",
    "service_tier_to_proto",
]

ServiceTierMap: dict[ServiceTier, "usage_pb2.ServiceTier"] = {
    "default": usage_pb2.ServiceTier.SERVICE_TIER_DEFAULT,
    "priority": usage_pb2.ServiceTier.SERVICE_TIER_PRIORITY,
}

_SERVICE_TIER_FROM_PROTO: dict["usage_pb2.ServiceTier", ServiceTier] = {
    usage_pb2.ServiceTier.SERVICE_TIER_UNSPECIFIED: "default",
    usage_pb2.ServiceTier.SERVICE_TIER_DEFAULT: "default",
    usage_pb2.ServiceTier.SERVICE_TIER_PRIORITY: "priority",
}


def service_tier_to_proto(tier: ServiceTier) -> "usage_pb2.ServiceTier":
    """Converts a ServiceTier string to its proto enum value."""
    if tier in ServiceTierMap:
        return ServiceTierMap[tier]
    raise ValueError(f"Invalid service tier: {tier}. Must be one of: {list(ServiceTierMap.keys())}")


def service_tier_from_proto(tier: "usage_pb2.ServiceTier") -> ServiceTier:
    """Converts a proto ServiceTier enum to its string representation."""
    return _SERVICE_TIER_FROM_PROTO.get(tier, "default")
