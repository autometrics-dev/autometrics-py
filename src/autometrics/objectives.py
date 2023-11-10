import logging

from enum import Enum
from re import match
from typing import Optional, Tuple


class ObjectivePercentile(Enum):
    """The percentage of requests that must meet the given criteria (success rate or latency)."""

    P90 = "90"
    P95 = "95"
    P99 = "99"
    P99_9 = "99.9"


class ObjectiveLatency(Enum):
    """The latency threshold for the given percentile."""

    Ms5 = "0.005"
    Ms10 = "0.01"
    Ms25 = "0.025"
    Ms50 = "0.05"
    Ms75 = "0.075"
    Ms100 = "0.1"
    Ms250 = "0.25"
    Ms500 = "0.5"
    Ms750 = "0.75"
    Ms1000 = "1.0"
    Ms2500 = "2.5"
    Ms5000 = "5.0"
    Ms7500 = "7.5"
    Ms10000 = "10.0"


# This represents a Service-Level Objective (SLO) for a function or group of functions.
# The objective should be given a descriptive name and can represent
# a success rate and/or latency objective.
#
# For details on SLOs, see <https://sre.google/sre-book/service-level-objectives/>
#
# Example:
# ```python
# from autometrics import autometrics
# from autometrics.objectives import Objective, ObjectivePercentile, ObjectiveLatency
# API_SLO = Objective(
#     "api",
#     success_rate=ObjectivePercentile.P99_9,
#     latency=(ObjectiveLatency.Ms250, ObjectivePercentile.P99),
# )
#
# @autometrics(objective = API_SLO)
# def api_handler() :
#    # ...
# ```
#
# ## How this works
#
# When an objective is added to a function, the metrics for that function will
# have additional labels attached to specify the SLO details.
#
# Autometrics comes with a set of Prometheus [recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
# and [alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
# that will fire alerts when the given objective is being violated.
#
# By default, these recording rules will effectively lay dormant.
# However, they are enabled when the special labels are present on certain metrics.
class Objective:
    """A Service-Level Objective (SLO) for a function or group of functions."""

    name: str
    """name: The name of the objective. This should be something descriptive of the function or group of functions it covers."""
    success_rate: Optional[ObjectivePercentile]
    """Specify the success rate for this objective.

    This means that the function or group of functions that are part of this objective
    should return an `Ok` result at least this percentage of the time."""
    latency: Optional[Tuple[ObjectiveLatency, ObjectivePercentile]]

    def __init__(
        self,
        name: str,
        success_rate: Optional[ObjectivePercentile] = None,
        latency: Optional[Tuple[ObjectiveLatency, ObjectivePercentile]] = None,
    ):
        """Create a new objective with the given name.

        The name should be something descriptive of the function or group of functions it covers.
        For example, if you have an objective covering all of the HTTP handlers in your API you might call it "api".
        """

        self.name = name
        self.success_rate = success_rate
        self.latency = latency

        # Check that name only contains alphanumeric characters and hyphens
        if match(r"^[\w-]+$", name) is None:
            logging.getLogger().warning(
                f"Objective name '{name}' contains invalid characters. Only alphanumeric characters and hyphens are allowed."
            )
