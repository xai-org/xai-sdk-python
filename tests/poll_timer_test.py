"""PollTimer must account elapsed time on a monotonic clock.

time.time() is a wall clock: NTP corrections, manual clock changes or VM
suspend/restore can move it, making a healthy poll time out immediately
(a forward adjustment) or poll far beyond the caller's timeout (a
backward adjustment). Regression for #203.
"""

import datetime
from unittest.mock import patch

from xai_sdk.poll_timer import PollTimer


def test_forward_wall_clock_adjustment_does_not_time_out():
    # The wall clock jumps forward 9900s between construction and the first
    # sleep computation; monotonic elapsed time is still ~0.5s.
    with patch("xai_sdk.poll_timer.time.monotonic", side_effect=[100.0, 100.5]):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=20),
        )
        interval = timer.sleep_interval_or_raise()

    assert interval == 9.5


def test_backward_wall_clock_adjustment_does_not_extend_timeout():
    # The wall clock jumps backward while 15s actually elapse: the poll must
    # still time out instead of quietly polling beyond the caller's timeout.
    with patch("xai_sdk.poll_timer.time.monotonic", side_effect=[10_000.0, 10_015.0]):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=1),
        )
        try:
            timer.sleep_interval_or_raise()
        except TimeoutError as e:
            assert "timed out after 15.0s" in str(e)
        else:
            raise AssertionError("expected TimeoutError")


def test_timeout_still_raises_on_real_elapsed_time():
    with patch("xai_sdk.poll_timer.time.monotonic", side_effect=[100.0, 200.0]):
        timer = PollTimer(
            timeout=datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=1),
        )
        try:
            timer.sleep_interval_or_raise()
        except TimeoutError as e:
            assert "timed out after 100.0s" in str(e)
        else:
            raise AssertionError("expected TimeoutError")
