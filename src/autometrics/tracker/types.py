from enum import Enum
from typing import Union, Optional, Protocol, List, Literal, Tuple

from ..objectives import Objective


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


class TrackerType(Enum):
    """Type of tracker."""

    OPENTELEMETRY = "opentelemetry"
    PROMETHEUS = "prometheus"


TrackerMessage = Union[
    Tuple[Literal["start"], str, str, Optional[bool]],
    Tuple[
        Literal["finish"],
        float,
        str,
        str,
        str,
        str,
        Result,
        Optional[Objective],
        Optional[bool],
    ],
    Tuple[Literal["initialize_counters"], str, str, Optional[Objective]],
]
MessageQueue = List[TrackerMessage]
