import datetime
import time
from typing import Optional


class PollTimer:
    """Utility for making sure the request timeout is not exceeded when polling.

    When polling, there is no persistent connection to the server that can time out. Instead, we
    have to manually keep track of time.
    """

    def __init__(
        self,
        timeout: Optional[datetime.timedelta] = None,
        interval: Optional[datetime.timedelta] = None,
        context: Optional[str] = None,
    ) -> None:
        """Creates a new instance of the `PollTimer` class.

        Args:
            timeout: Maximum time to wait before aborting the RPC.
            interval: Time to wait between polls.
            context: A description of what is being waited on (e.g. "waiting for document to be indexed").
                Included in the TimeoutError message for easier debugging.
        """
        self._start = time.time()
        self._timeout = timeout or datetime.timedelta(minutes=10)
        self._interval = interval or datetime.timedelta(seconds=1)
        self._context = context

    def sleep_interval_or_raise(self) -> float:
        """Returns the time to sleep until the next poll.

        Returns:
            Time to sleep until the next poll.

        Raises:
            TimeoutError when the total polling time is used up.
        """
        runtime = time.time() - self._start
        if runtime > self._timeout.total_seconds():
            message = f"Polling timed out after {runtime:.1f}s"
            if self._context:
                message += f": {self._context}"
            raise TimeoutError(message)
        else:
            return min(self._timeout.total_seconds() - runtime, self._interval.total_seconds())
