![GitHub_headerImage](https://user-images.githubusercontent.com/3262610/221191767-73b8a8d9-9f8b-440e-8ab6-75cb3c82f2bc.png)

[![Tests](https://github.com/autometrics-dev/autometrics-py/actions/workflows/main.yml/badge.svg)](https://github.com/autometrics-dev/autometrics-py/actions/workflows/main.yml)
[![Discord Shield](https://discordapp.com/api/guilds/950489382626951178/widget.png?style=shield)](https://discord.gg/kHtwcH8As9)

> A Python port of the Rust
> [autometrics-rs](https://github.com/fiberplane/autometrics-rs) library

Metrics are a powerful and cost-efficient tool for understanding the health and performance of your code in production. But it's hard to decide what metrics to track and even harder to write queries to understand the data.

Autometrics provides a decorator that makes it trivial to instrument any function with the most useful metrics: request rate, error rate, and latency. It standardizes these metrics and then generates powerful Prometheus queries based on your function details to help you quickly identify and debug issues in production.

See [Why Autometrics?](https://github.com/autometrics-dev#why-autometrics) for more details on the ideas behind autometrics.

## Features

- ✨ `@autometrics` decorator instruments any function or class method to track the
  most useful metrics
- 💡 Writes Prometheus queries so you can understand the data generated without
  knowing PromQL
- 🔗 Create links to live Prometheus charts directly into each function's docstring
- 🔍 [Identify commits](#build-info) that introduced errors or increased latency
- 🚨 [Define alerts](#alerts--slos) using SLO best practices directly in your source code
- 📊 [Grafana dashboards](#dashboards) work out of the box to visualize the performance of instrumented functions & SLOs
- ⚙️ [Configurable](#settings) metric collection library (`opentelemetry` or `prometheus`)
- 📍 [Attach exemplars](#exemplars) to connect metrics with traces
- ⚡ Minimal runtime overhead

## Quickstart

1. Add `autometrics` to your project's dependencies:

```shell
pip install autometrics
```

2. Instrument your functions with the `@autometrics` decorator

```python
from autometrics import autometrics

@autometrics
def my_function():
  # ...
```

3. Configure autometrics by calling the `init` function:

```python
from autometrics import init

init(tracker="prometheus", service_name="my-service")
```

4. Export the metrics for Prometheus

```python
# This example uses FastAPI, but you can use any web framework
from fastapi import FastAPI, Response
from prometheus_client import generate_latest

# Set up a metrics endpoint for Prometheus to scrape
#   `generate_latest` returns metrics data in the Prometheus text format
@app.get("/metrics")
def metrics():
    return Response(generate_latest())
```

5. Run Prometheus locally with the [Autometrics CLI](https://docs.autometrics.dev/local-development#getting-started-with-am) or [configure it manually](https://github.com/autometrics-dev#5-configuring-prometheus) to scrape your metrics endpoint

```sh
# Replace `8080` with the port that your app runs on
am start :8080
```

6. (Optional) If you have Grafana, import the [Autometrics dashboards](https://github.com/autometrics-dev/autometrics-shared#dashboards) for an overview and detailed view of all the function metrics you've collected

## Using `autometrics-py`

- You can import the library in your code and use the decorator for any function:

```python
from autometrics import autometrics

@autometrics
def sayHello:
  return "hello"

```

- To show tooltips over decorated functions in VSCode, with links to Prometheus queries, try installing [the VSCode extension](https://marketplace.visualstudio.com/items?itemName=Fiberplane.autometrics).

  > **Note**: We cannot support tooltips without a VSCode extension due to behavior of the [static analyzer](https://github.com/davidhalter/jedi/issues/1921) used in VSCode.

- You can also track the number of concurrent calls to a function by using the `track_concurrency` argument: `@autometrics(track_concurrency=True)`.

  > **Note**: Concurrency tracking is only supported when you set with the environment variable `AUTOMETRICS_TRACKER=prometheus`.

- To access the PromQL queries for your decorated functions, run `help(yourfunction)` or `print(yourfunction.__doc__)`.

  > For these queries to work, include a `.env` file in your project with your prometheus endpoint `PROMETHEUS_URL=your endpoint`. If this is not defined, the default endpoint will be `http://localhost:9090/`

## Dashboards

Autometrics provides [Grafana dashboards](https://github.com/autometrics-dev/autometrics-shared#dashboards) that will work for any project instrumented with the library.

## Alerts / SLOs

Autometrics makes it easy to add intelligent alerting to your code, in order to catch increases in the error rate or latency across multiple functions.

```python
from autometrics import autometrics
from autometrics.objectives import Objective, ObjectiveLatency, ObjectivePercentile

# Create an objective for a high success rate
# Here, we want our API to have a success rate of 99.9%
API_SLO_HIGH_SUCCESS = Objective(
    "My API SLO for High Success Rate (99.9%)",
    success_rate=ObjectivePercentile.P99_9,
)

@autometrics(objective=API_SLO_HIGH_SUCCESS)
def api_handler():
  # ...
```

The library uses the concept of Service-Level Objectives (SLOs) to define the acceptable error rate and latency for groups of functions. Alerts will fire depending on the SLOs you set.

> Not sure what SLOs are? [Check out our docs](https://docs.autometrics.dev/slo) for an introduction.

In order to receive alerts, **you need to add a special set of rules to your Prometheus setup**. These are configured automatically when you use the [Autometrics CLI](https://docs.autometrics.dev/local-development#getting-started-with-am) to run Prometheus.

> Already running Prometheus yourself? [Read about how to load the autometrics alerting rules into Prometheus here](https://github.com/autometrics-dev/autometrics-shared#prometheus-recording--alerting-rules).

Once the alerting rules are in Prometheus, you're ready to go.

To use autometrics SLOs and alerts, create one or multiple `Objective`s based on the function(s) success rate and/or latency, as shown above.

The `Objective` can be passed as an argument to the `autometrics` decorator, which will include the given function in that objective.

The example above used a success rate objective. (I.e., we wanted to be alerted when the error rate started to increase.)

You can also create an objective for the latency of your functions like so:

```python
from autometrics import autometrics
from autometrics.objectives import Objective, ObjectiveLatency, ObjectivePercentile

# Create an objective for low latency
#   - Functions with this objective should have a 99th percentile latency of less than 250ms
API_SLO_LOW_LATENCY = Objective(
    "My API SLO for Low Latency (99th percentile < 250ms)",
    latency=(ObjectiveLatency.Ms250, ObjectivePercentile.P99),
)

@autometrics(objective=API_SLO_LOW_LATENCY)
def api_handler():
  # ...
```

## The `caller` Label

Autometrics keeps track of instrumented functions that call each other. So, if you have a function `get_users` that calls another function `db.query`, then the metrics for latter will include a label `caller="get_users"`.

This allows you to drill down into the metrics for functions that are _called by_ your instrumented functions, provided both of those functions are decorated with `@autometrics`.

In the example above, this means that you could investigate the latency of the database queries that `get_users` makes, which is rather useful.

## Settings and Configuration

Autometrics makes use of a number of environment variables to configure its behavior. All of them are also configurable with keyword arguments to the `init` function.

- `tracker` - Configure the package that autometrics will use to produce metrics. Default is `opentelemetry`, but you can also use `prometheus`. Look in `pyproject.toml` for the corresponding versions of packages that will be used.
- `histogram_buckets` - Configure the buckets used for latency histograms. Default is `[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]`.
- `enable_exemplars` - Enable [exemplar collection](#exemplars). Default is `False`.
- `service_name` - Configure the [service name](#service-name).
- `version`, `commit`, `branch`, `repository_url`, `repository_provider` - Used to configure [build_info](#build-info).

Below is an example of initializing autometrics with build information, as well as the `prometheus` tracker. (Note that you can also accomplish the same confiugration with environment variables.)

```python
from autometrics import autometrics, init
from git_utils import get_git_commit, get_git_branch

VERSION = "0.0.1"

init(
  tracker="prometheus",
  version=VERSION,
  commit=get_git_commit(),
  branch=get_git_branch()
)
```

## Identifying commits that introduced problems <span name="build-info" />

Autometrics makes it easy to identify if a specific version or commit introduced errors or increased latencies.

> **NOTE** - As of writing, `build_info` will not work correctly when using the default setting of `AUTOMETRICS_TRACKER=opentelemetry`. If you wish to use `build_info`, you must use the `prometheus` tracker instead (`AUTOMETRICS_TRACKER=prometheus`).
>
> The issue will be fixed once the following PR is merged and released on the opentelemetry-python project: https://github.com/open-telemetry/opentelemetry-python/pull/3306
>
> autometrics-py will track support for build_info using the OpenTelemetry tracker via [this issue](https://github.com/autometrics-dev/autometrics-py/issues/38)

The library uses a separate metric (`build_info`) to track the version and git metadata of your code - repository url, provider name, commit and branch.

It then writes queries that group metrics by these metadata, so you can spot correlations between code changes and potential issues.

Configure these labels by setting the following environment variables:

| Label                 | Run-Time Environment Variables        | Default value |
| --------------------- | ------------------------------------- | ------------- |
| `version`             | `AUTOMETRICS_VERSION`                 | `""`          |
| `commit`              | `AUTOMETRICS_COMMIT` or `COMMIT_SHA`  | `""`          |
| `branch`              | `AUTOMETRICS_BRANCH` or `BRANCH_NAME` | `""`          |
| `repository_url`      | `AUTOMETRICS_REPOSITORY_URL`          | `""`\*        |
| `repository_provider` | `AUTOMETRICS_REPOSITORY_PROVIDER`     | `""`\*        |

\* Autometrics will attempt to automagically infer these values from the git config inside your working directory. To disable this behavior, explicitly set the corresponding setting or environment variable to `""`.

This follows the method outlined in [Exposing the software version to Prometheus](https://www.robustperception.io/exposing-the-software-version-to-prometheus/).

## Service name

All metrics produced by Autometrics have a label called `service.name` (or `service_name` when exported to Prometheus) attached, in order to identify the logical service they are part of.

You may want to override the default service name, for example if you are running multiple instances of the same code base as separate services, and you want to differentiate between the metrics produced by each one.

The service name is loaded from the following environment variables, in this order:

1. `AUTOMETRICS_SERVICE_NAME` (at runtime)
2. `OTEL_SERVICE_NAME` (at runtime)
3. First part of `__package__` (at runtime)

## Exemplars

> **NOTE** - As of writing, exemplars aren't supported by the default tracker (`AUTOMETRICS_TRACKER=opentelemetry`).
> You can track the progress of this feature here: https://github.com/autometrics-dev/autometrics-py/issues/41

Exemplars are a way to associate a metric sample to a trace by attaching `trace_id` and `span_id` to it. You can then use this information to jump from a metric to a trace in your tracing system (for example Jaeger). If you have an OpenTelemetry tracer configured, autometrics will automatically pick up the current span from it.

To use exemplars, you need to first switch to a tracker that supports them by setting `AUTOMETRICS_TRACKER=prometheus` and enable
exemplar collection by setting `AUTOMETRICS_EXEMPLARS=true`. You also need to enable exemplars in Prometheus by launching Prometheus with the `--enable-feature=exemplar-storage` flag.

## Exporting metrics

There are multiple ways to export metrics from your application, depending on your setup. You can see examples of how to do this in the [examples/export_metrics](https://github.com/autometrics-dev/autometrics-py/tree/main/examples/export_metrics) directory.

If you want to export metrics to Prometheus, you have two options in case of both `opentelemetry` and `prometheus` trackers:

1. Create a route inside your app and respond with `generate_latest()`

```python
# This example uses FastAPI, but you can use any web framework
from fastapi import FastAPI, Response
from prometheus_client import generate_latest

# Set up a metrics endpoint for Prometheus to scrape
@app.get("/metrics")
def metrics():
    return Response(generate_latest())
```

2. Specify `prometheus` as the exporter type, and a separate server will be started to expose metrics from your app:

```python
exporter = {
    "type": "prometheus",
    "address": "localhost",
    "port": 9464
}
init(tracker="prometheus", service_name="my-service", exporter=exporter)
```

For the OpenTelemetry tracker, you have more options, including a custom metric reader. You can specify the exporter type to be `otlp-proto-http` or `otlp-proto-grpc`, and metrics will be exported to a remote OpenTelemetry collector via the specified protocol. You will need to install the respective extra dependency in order for this to work, which you can do when you install autometrics:

```sh
pip install autometrics[exporter-otlp-proto-http]
pip install autometrics[exporter-otlp-proto-grpc]
```

After installing it you can configure the exporter as follows:

```python
exporter = {
    "type": "otlp-proto-grpc",
    "address": "http://localhost:4317",
    "insecure": True
}
init(tracker="opentelemetry", service_name="my-service", exporter=exporter)
```

To use a custom metric reader you can specify the exporter type to be `otel-custom` and provide a custom metric reader:

```python
my_custom_metric_reader = PrometheusMetricReader("")
exporter = {
    "type": "otel-custom",
    "reader": my_custom_metric_reader
}
init(tracker="opentelemetry", service_name="my-service", exporter=exporter)
```

## Development of the package

This package uses [poetry](https://python-poetry.org) as a package manager, with all dependencies separated into three groups:

- root level dependencies, required
- `dev`, everything that is needed for development or in ci
- `examples`, dependencies of everything in `examples/` directory

By default, poetry will only install required dependencies, if you want to run examples, install using this command:

```sh
poetry install --with examples
```

Code in this repository is:

- formatted using [black](https://black.readthedocs.io/en/stable/).
- contains type definitions (which are linted by [mypy](https://www.mypy-lang.org/))
- tested using [pytest](https://docs.pytest.org/)

In order to run these tools locally you have to install them, you can install them using poetry:

```sh
poetry install --with dev --all-extras
```

After that you can run the tools individually

```sh
# Formatting using black
poetry run black .
# Lint using mypy
poetry run mypy .
# Run the tests using pytest
poetry run pytest
# Run a single test, and clear the cache
poetry run pytest --cache-clear -k test_tracker
```
