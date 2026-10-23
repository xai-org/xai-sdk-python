"""Tests for the polling defaults and the docstrings that quote them.

Kept apart from PollTimer's own behaviour tests so the two can land in either order.
"""

import datetime

import pytest

from xai_sdk.aio.chat import Chat as AsyncChat
from xai_sdk.poll_timer import PollTimer
from xai_sdk.sync.chat import Chat as SyncChat


def test_poll_timer_defaults():
    timer = PollTimer()

    assert timer._interval == datetime.timedelta(seconds=1)
    assert timer._timeout == datetime.timedelta(minutes=10)


@pytest.mark.parametrize(
    "method",
    [SyncChat.defer, SyncChat.defer_batch, SyncChat._defer, AsyncChat.defer, AsyncChat.defer_batch, AsyncChat._defer],
    ids=lambda m: f"{m.__module__.rsplit('.', 1)[-1]}.{m.__name__}",
)
def test_defer_docstrings_quote_the_real_poll_interval_default(method):
    # The default lives in PollTimer; the docstrings restate it, and have drifted before.
    interval = PollTimer()._interval

    assert method.__doc__ is not None
    assert f"defaults to {interval.total_seconds():g} second" in method.__doc__
    assert "milliseconds" not in method.__doc__
