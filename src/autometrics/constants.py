"""Constants used by autometrics"""

COUNTER_DESCRIPTION = "Autometrics counter for tracking function calls"
HISTOGRAM_DESCRIPTION = "Autometrics histogram for tracking function call duration"

# The following constants are used to create the labels
OBJECTIVE_NAME = "objective.name".replace(".", "_")
OBJECTIVE_PERCENTILE = "objective.percentile".replace(".", "_")
OBJECTIVE_LATENCY_THRESHOLD = "objective.latency_threshold".replace(".", "_")

# The values are updated to use underscores instead of periods to avoid issues with prometheus.
# A similar thing is done in the rust library, which supports multiple exporters
OBJECTIVE_NAME_PROMETHEUS = OBJECTIVE_NAME.replace(".", "_")
OBJECTIVE_PERCENTILE_PROMETHEUS = OBJECTIVE_PERCENTILE.replace(".", "_")
OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS = OBJECTIVE_LATENCY_THRESHOLD.replace(".", "_")

# Env var names
ENV_FP_METRICS_URL = "FP_METRICS_URL"
ENV_PROMETHEUS_URL_DEPRECATED = "PROMETHEUS_URL"