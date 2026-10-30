import json

import grpc
import pytest

from xai_sdk import RetryPolicy
from xai_sdk.client import _DEFAULT_CHANNEL_OPTIONS, _format_duration


def _retry_policy_config(policy: RetryPolicy) -> dict:
    service_config = dict(policy._channel_options())["grpc.service_config"]
    return json.loads(service_config)["methodConfig"][0]["retryPolicy"]


def test_default_policy_matches_default_channel_options():
    options = dict(_DEFAULT_CHANNEL_OPTIONS)

    assert options["grpc.enable_retries"] == 1
    assert json.loads(options["grpc.service_config"]) == {
        "methodConfig": [
            {
                "name": [{}],
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "0.1s",
                    "maxBackoff": "1s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }
        ]
    }
    assert RetryPolicy()._channel_options() == [
        ("grpc.enable_retries", 1),
        ("grpc.service_config", options["grpc.service_config"]),
    ]


def test_custom_policy_service_config():
    policy = RetryPolicy(
        max_attempts=3,
        initial_backoff=0.5,
        max_backoff=2,
        backoff_multiplier=1.5,
        retryable_status_codes=[grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.RESOURCE_EXHAUSTED],
    )

    assert _retry_policy_config(policy) == {
        "maxAttempts": 3,
        "initialBackoff": "0.5s",
        "maxBackoff": "2s",
        "backoffMultiplier": 1.5,
        "retryableStatusCodes": ["UNAVAILABLE", "RESOURCE_EXHAUSTED"],
    }


def test_single_attempt_disables_retries():
    assert RetryPolicy(max_attempts=1)._channel_options() == [("grpc.enable_retries", 0)]


def test_retryable_status_codes_are_stored_as_tuple():
    policy = RetryPolicy(retryable_status_codes=[grpc.StatusCode.RESOURCE_EXHAUSTED])

    assert policy.retryable_status_codes == (grpc.StatusCode.RESOURCE_EXHAUSTED,)
    assert hash(policy) == hash(RetryPolicy(retryable_status_codes=(grpc.StatusCode.RESOURCE_EXHAUSTED,)))


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0.1, "0.1s"), (1, "1s"), (2.0, "2s"), (10, "10s"), (1.25, "1.25s"), (0.000000001, "0.000000001s")],
)
def test_format_duration(seconds, expected):
    assert _format_duration(seconds) == expected


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"max_attempts": 0}, "max_attempts must be an integer between 1 and 5"),
        ({"max_attempts": 6}, "max_attempts must be an integer between 1 and 5"),
        ({"max_attempts": 2.5}, "max_attempts must be an integer between 1 and 5"),
        ({"max_attempts": True}, "max_attempts must be an integer between 1 and 5"),
        ({"initial_backoff": 0}, "initial_backoff must be positive"),
        ({"max_backoff": -1}, "max_backoff must be positive"),
        ({"backoff_multiplier": 0}, "backoff_multiplier must be positive"),
        ({"initial_backoff": 3.0, "max_backoff": 2.0}, "initial_backoff .* can't be greater than max_backoff"),
        ({"retryable_status_codes": []}, "retryable_status_codes must not be empty"),
        ({"retryable_status_codes": [grpc.StatusCode.OK]}, "retryable_status_codes must not contain"),
    ],
)
def test_invalid_policies_are_rejected(kwargs, message):
    with pytest.raises(ValueError, match=message):
        RetryPolicy(**kwargs)


@pytest.mark.parametrize("codes", [["UNAVAILABLE"], [14], [grpc.StatusCode.UNAVAILABLE, None]])
def test_non_status_code_items_are_rejected(codes):
    with pytest.raises(TypeError, match="must be instances of grpc.StatusCode"):
        RetryPolicy(retryable_status_codes=codes)


def test_equal_initial_and_max_backoff_are_allowed():
    assert _retry_policy_config(RetryPolicy(initial_backoff=1, max_backoff=1))["maxBackoff"] == "1s"
