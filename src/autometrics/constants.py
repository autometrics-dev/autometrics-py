"""Constants used by autometrics"""

SPEC_VERSION = "1.0.0"

COUNTER_NAME = "function.calls"
HISTOGRAM_NAME = "function.calls.duration"
CONCURRENCY_NAME = "function.calls.concurrent"
# NOTE - The Rust implementation does not use `build.info`, instead opts for just `build_info`
BUILD_INFO_NAME = "build_info"
SERVICE_NAME = "service.name"
REPOSITORY_URL = "repository.url"
REPOSITORY_PROVIDER = "repository.provider"
AUTOMETRICS_VERSION = "autometrics.version"


COUNTER_NAME_PROMETHEUS = COUNTER_NAME.replace(".", "_")
HISTOGRAM_NAME_PROMETHEUS = HISTOGRAM_NAME.replace(".", "_")
CONCURRENCY_NAME_PROMETHEUS = CONCURRENCY_NAME.replace(".", "_")
SERVICE_NAME_PROMETHEUS = SERVICE_NAME.replace(".", "_")
REPOSITORY_URL_PROMETHEUS = REPOSITORY_URL.replace(".", "_")
REPOSITORY_PROVIDER_PROMETHEUS = REPOSITORY_PROVIDER.replace(".", "_")
AUTOMETRICS_VERSION_PROMETHEUS = AUTOMETRICS_VERSION.replace(".", "_")

COUNTER_DESCRIPTION = "Autometrics counter for tracking function calls"
HISTOGRAM_DESCRIPTION = "Autometrics histogram for tracking function call duration"
CONCURRENCY_DESCRIPTION = "Autometrics gauge for tracking function call concurrency"
BUILD_INFO_DESCRIPTION = (
    "Autometrics info metric for tracking software version and build details"
)

# The following constants are used to create the labels
OBJECTIVE_NAME = "objective.name"
OBJECTIVE_PERCENTILE = "objective.percentile"
OBJECTIVE_LATENCY_THRESHOLD = "objective.latency_threshold"
VERSION_KEY = "version"
COMMIT_KEY = "commit"
BRANCH_KEY = "branch"

# The values are updated to use underscores instead of periods to avoid issues with prometheus.
# A similar thing is done in the rust library, which supports multiple exporters
OBJECTIVE_NAME_PROMETHEUS = OBJECTIVE_NAME.replace(".", "_")
OBJECTIVE_PERCENTILE_PROMETHEUS = OBJECTIVE_PERCENTILE.replace(".", "_")
OBJECTIVE_LATENCY_THRESHOLD_PROMETHEUS = OBJECTIVE_LATENCY_THRESHOLD.replace(".", "_")
