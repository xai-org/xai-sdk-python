import datetime
from unittest.mock import patch

import pytest

from xai_sdk.poll_timer import PollTimer


def test_zero_timeout_is_not_replaced_by_default():
    with patch("xai_sdk.poll_timer.time.time", return_value=100.0):
        timer = PollTimer(
            timeout=datetime.timedelta(0),
            interval=datetime.timedelta(seconds=5),
        )
        assert timer.sleep_interval_or_raise() == 0


def test_zero_timeout_expires_as_soon_as_time_advances():
    with patch("xai_sdk.poll_timer.time.time", side_effect=[100.0, 100.001]):
        timer = PollTimer(timeout=datetime.timedelta(0))
        with pytest.raises(TimeoutError, match="Polling timed out"):
            timer.sleep_interval_or_raise()


def test_zero_interval_is_not_replaced_by_default():
    with patch("xai_sdk.poll_timer.time.time", return_value=100.0):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(0),
        )
        assert timer.sleep_interval_or_raise() == 0


def test_none_still_uses_documented_defaults():
    with patch("xai_sdk.poll_timer.time.time", return_value=100.0):
        timer = PollTimer(timeout=None, interval=None)
        assert timer.sleep_interval_or_raise() == 1
