"""Constants used by autometrics"""

COUNTER_NAME = "function.calls.count"
HISTOGRAM_NAME = "function.calls.duration"
BUILD_INFO_NAME = "build.info"

COUNTER_NAME_PROMETHEUS = COUNTER_NAME.replace(".", "_")
HISTOGRAM_NAME_PROMETHEUS = HISTOGRAM_NAME.replace(".", "_")
BUILD_INFO_NAME_PROMETHEUS = BUILD_INFO_NAME.replace(".", "_")

COUNTER_DESCRIPTION = "Autometrics counter for tracking function calls"
HISTOGRAM_DESCRIPTION = "Autometrics histogram for tracking function call duration"
BUILD_INFO_DESCRIPTION = "Autometrics info metric for tracking software version and build details"

# The following constants are used to create the labels
OBJECTIVE_NAME = "objective.name"
OBJECTIVE_PERCENTILE = "objective.percentile"
OBJECTIVE_LATENCY_THRESHOLD = "objective.latency_threshold"
VERSION_KEY = "version"
COMMIT_KEY = "commit"

# The values are updated to use underscores instead of periods to avoid issues with prometheus.
# A similar thing is done in the rust library, which supports multiple exporters
OBJECTIVE_NAME_PROMETHEUS = OBJECTIVE_NAME.replace(".", "_")
OBJECTIVE_PERCENTILE_PROMETHEUS = OBJECTIVE_PERCENTILE.replace(".", "_")
OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS = OBJECTIVE_LATENCY_THRESHOLD.replace(".", "_")
