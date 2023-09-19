from enum import Enum
from typing import Literal, Optional, Protocol

from ..objectives import Objective

TrackerMessage = tuple[Literal["start", "finish", "initialize_counters"], ...]
MessageQueue = list[TrackerMessage]


class Result(Enum):
    """Result of the function call."""

    OK = "ok"
    ERROR = "error"


class TrackMetrics(Protocol):
    """Protocol for tracking metrics."""

    def set_build_info(self, commit: str, version: str, branch: str):
        """Observe the build info. Should only be called once per tracker instance"""

    def start(
        self, function: str, module: str, track_concurrency: Optional[bool] = False
    ):
        """Start tracking metrics for a function call."""

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

    def initialize_counters(
        self,
        function: str,
        module: str,
        objective: Optional[Objective] = None,
    ):
        """Initialize (counter) metrics for a function at zero."""

    def replay_queue(self, queue: MessageQueue):
        """Replay a queue of messages"""


class TrackerType(Enum):
    """Type of tracker."""

    OPENTELEMETRY = "opentelemetry"
    PROMETHEUS = "prometheus"
