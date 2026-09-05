import datetime
from unittest.mock import patch

import pytest

from xai_sdk.poll_timer import PollTimer


def test_sleep_interval_or_raise_unaffected_by_wall_clock_jump_forward():
    """Wall-clock jumps must not affect timeout accounting (uses monotonic)."""
    with (
        patch("xai_sdk.poll_timer.time.time", side_effect=[100.0, 10_000.0]),
        patch("xai_sdk.poll_timer.time.monotonic", side_effect=[0.0, 1.0]),
    ):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=20),
        )
        assert timer.sleep_interval_or_raise() == pytest.approx(9.0)


def test_sleep_interval_or_raise_unaffected_by_wall_clock_jump_backward():
    with (
        patch("xai_sdk.poll_timer.time.time", side_effect=[10_000.0, 100.0]),
        patch("xai_sdk.poll_timer.time.monotonic", side_effect=[0.0, 2.0]),
    ):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=20),
        )
        assert timer.sleep_interval_or_raise() == pytest.approx(8.0)


def test_sleep_interval_or_raise_times_out_based_on_monotonic_elapsed():
    with patch("xai_sdk.poll_timer.time.monotonic", side_effect=[0.0, 11.0]):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=1),
            context="waiting for document to be indexed",
        )
        with pytest.raises(TimeoutError, match=r"Polling timed out after 11\.0s: waiting for document"):
            timer.sleep_interval_or_raise()


def test_sleep_interval_or_raise_returns_min_of_remaining_and_interval():
    with patch("xai_sdk.poll_timer.time.monotonic", side_effect=[0.0, 0.5]):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=1),
        )
        assert timer.sleep_interval_or_raise() == pytest.approx(1.0)
