import logging

from typing import Optional

from .types import Result, TrackerMessage, MessageQueue, TrackMetrics
from ..objectives import Objective


class TemporaryTracker:
    """A tracker that temporarily stores metrics only to hand them off to another tracker."""

    _queue: MessageQueue = []
    _is_closed: bool = False
    _new_tracker: Optional[TrackMetrics] = None

    def set_build_info(self, commit: str, version: str, branch: str):
        """Observe the build info. Should only be called once per tracker instance"""
        pass

    def start(
        self, function: str, module: str, track_concurrency: Optional[bool] = False
    ):
        """Start tracking metrics for a function call."""
        self.append_to_queue(("start", function, module, track_concurrency))

    def finish(
        self,
        duration: float,
        function: str,
        module: str,
        caller_module: str,
        caller_function: str,
        result: Result = Result.OK,
        objective: Optional[Objective] = None,
        track_concurrency: Optional[bool] = False,
    ):
        """Finish tracking metrics for a function call."""
        self.append_to_queue(
            (
                "finish",
                duration,
                function,
                module,
                caller_module,
                caller_function,
                result,
                objective,
                track_concurrency,
            )
        )

    def initialize_counters(
        self,
        function: str,
        module: str,
        objective: Optional[Objective] = None,
    ):
        """Initialize (counter) metrics for a function at zero."""
        self.append_to_queue(("initialize_counters", function, module, objective))

    def append_to_queue(self, message: TrackerMessage):
        """Append a message to the queue."""
        if not self._is_closed:
            self._queue.append(message)
            if len(self._queue) > 999:
                self._is_closed = True
        elif self._new_tracker is not None:
            function_name, *args = message
            function = getattr(self._new_tracker, function_name)
            function(*args)
        else:
            logging.error(
                "Temporary tracker queue is filled, this metric will be dropped. Please run init() when your application starts."
            )

    def replay_queue(self, tracker: TrackMetrics):
        """Replay a queue of messages on a different tracker."""
        self._new_tracker = tracker
        self._is_closed = True
        for function_name, *args in self._queue:
            function = getattr(tracker, function_name)
            function(*args)
