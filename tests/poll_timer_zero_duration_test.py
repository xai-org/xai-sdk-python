import datetime
from unittest.mock import patch

from xai_sdk.poll_timer import PollTimer


def _frozen_clock():
    return (
        patch("xai_sdk.poll_timer.time.time", return_value=100.0),
        patch("xai_sdk.poll_timer.time.monotonic", return_value=100.0),
    )


def test_zero_timeout_is_not_replaced_by_default():
    wall_clock, monotonic_clock = _frozen_clock()
    with wall_clock, monotonic_clock:
        timer = PollTimer(
            timeout=datetime.timedelta(0),
            interval=datetime.timedelta(seconds=5),
        )
        assert timer.sleep_interval_or_raise() == 0


def test_zero_interval_is_not_replaced_by_default():
    wall_clock, monotonic_clock = _frozen_clock()
    with wall_clock, monotonic_clock:
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(0),
        )
        assert timer.sleep_interval_or_raise() == 0
