![GitHub_headerImage](https://user-images.githubusercontent.com/3262610/221191767-73b8a8d9-9f8b-440e-8ab6-75cb3c82f2bc.png)

# autometrics-py

A Python library that exports a decorator that makes it easy to understand the error rate, response time, and production usage of any function in your code. Jump straight from your IDE to live Prometheus charts for each HTTP/RPC handler, database method, or other piece of application logic.

Autometrics for Python provides:

1. A decorator that can create [Prometheus](https://prometheus.io/) metrics for your functions and class methods throughout your code base.
2. A helper function that will write corresponding Prometheus queries for you in a Markdown file.

See [Why Autometrics?](https://github.com/autometrics-dev#why-autometrics) for more details on the ideas behind autometrics.

## Features

- ✨ `autometrics` decorator instruments any function or class method to track the
  most useful metrics
- 💡 Writes Prometheus queries so you can understand the data generated without
  knowing PromQL
- 🔗 Create links to live Prometheus charts directly into each function's docstring
- [🔍 Identify commits](#identifying-commits-that-introduced-problems) that introduced errors or increased latency
- [🚨 Define alerts](#alerts--slos) using SLO best practices directly in your source code
- [📊 Grafana dashboards](#dashboards) work out of the box to visualize the performance of instrumented functions & SLOs
- [⚙️ Configurable](#metrics-libraries) metric collection library (`opentelemetry`, `prometheus`, or `metrics`)
- ⚡ Minimal runtime overhead

1. Add `autometrics` to your project:

   ```sh
   pip3 install autometrics
   ```

2. Instrument your functions with the [`@autometrics`](https://pypi.org/project/autometrics/) decorator

   <details>

   <summary> Tip: Adding autometrics to all <code>pub</code> functions (not necessarily recommended 😅)
   </summary>
     <br />

   You can use a search and replace to add autometrics to all public functions. Yes, this is a bit nuts.

   Use a regular expression search to replace:

   ```
   ((?:async)? def .*)
   ```

   With:

   ```
   @autometrics
   $1
   ```

   And then check which files you need to add `from autometrics import autometrics` at the top of.

   </details>

3. Export the metrics for Prometheus

   <details>

     <summary>
     For projects not currently using Prometheus metrics
     </summary>

     <br />

   Autometrics includes optional functions to help collect and prepare metrics to be collected by Prometheus.

   Create a route on your API (probably mounted under `/metrics`) that returns the following:

   ```py
   from autometrics import autometrics
   from fastapi import FastAPI, Response
   from prometheus_client import start_http_server

   app = FastAPI()

   @app.get("/metrics")
   def metrics():
       return Response(generate_latest())

   ```

     </details>

     <details>

     <summary>
     For projects already using custom Prometheus metrics
     </summary>

     <br />

   Configure `autometrics` to use the same underlying metrics library you use with the appropriate feature flag (see [below](#metrics-libraries)).

   The `autometrics` metrics will be produced alongside yours.

   You do not need to use the Prometheus exporter functions this library provides (you can leave out the `prometheus-exporter` feature flag) and you do not need a separate endpoint for autometrics' metrics.

     </details>

4. [Configure Prometheus](https://github.com/autometrics-dev#5-configuring-prometheus) to scrape your metrics endpoint
5. (Optional) If you have Grafana, import the [Autometrics dashboards](https://github.com/autometrics-dev/autometrics-shared#dashboards) for an overview and detailed view of the function metrics

## Using autometrics-py

- Set up a [Prometheus instance](https://prometheus.io/download/)
- Configure prometheus to scrape your application ([check our instructions if you need help](https://github.com/autometrics-dev#5-configuring-prometheus))
- Include a .env file with your prometheus endpoint `PROMETHEUS_URL=your endpoint`. If this is not defined, the default endpoint will be `http://localhost:9090/`
- `pip install autometrics`
- Import the library in your code and use the decorator for any function:

```py
from autometrics import autometrics

@autometrics
def sayHello:
   return "hello"

```

- To access the PromQL queries for your decorated functions, run `help(yourfunction)` or `print(yourfunction.__doc__)`.

- To show tooltips over decorated functions in VSCode, with links to Prometheus queries, try installing [the VSCode extension](https://marketplace.visualstudio.com/items?itemName=Fiberplane.autometrics).

> Note that we cannot support tooltips without a VSCode extension due to behavior of the [static analyzer](https://github.com/davidhalter/jedi/issues/1921) used in VSCode.

## Dashboards

Autometrics provides [Grafana dashboards](https://github.com/autometrics-dev/autometrics-shared#dashboards) that will work for any project instrumented with the library.

## Alerts / SLOs

Autometrics makes it easy to add Prometheus alerts using Service-Level Objectives (SLOs) to a function or group of functions.

In order to receive alerts you need to add a set of rules to your Prometheus set up. You can find out more about those rules here: [Prometheus alerting rules](https://github.com/autometrics-dev/autometrics-shared#prometheus-recording--alerting-rules). Once added, most of the recording rules are dormant. They are enabled by specific metric labels that can be automatically attached by autometrics.

To use autometrics SLOs and alerts, create one or multiple `Objective`s based on the function(s) success rate and/or latency, as shown below. The `Objective` can be passed as an argument to the `autometrics` macro to include the given function in that objective.

```python
from autometrics import autometrics
from autometrics.objectives import Objective, ObjectiveLatency, ObjectivePercentile

API_SLO = Objective(
    "random",
    success_rate=ObjectivePercentile.P99_9,
    latency=(ObjectiveLatency.Ms250, ObjectivePercentile.P99),
)

@autometrics(objective=API_SLO)
def api_handler():
  # ...
```

Autometrics by default will try to store information on which function calls a decorated function. As such you may want to place the autometrics in the top/first decorator, as otherwise you may get `inner` or `wrapper` as the caller function.

So instead of writing:

```py
from functools import wraps
from typing import Any, TypeVar, Callable

R = TypeVar("R")

def noop(func: Callable[..., R]) -> Callable[..., R]:
    """A noop decorator that does nothing."""

    @wraps(func)
    def inner(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return inner

@noop
@autometrics
def api_handler():
  # ...
```

You may want to switch the order of the decorator

```py
@autometrics
@noop
def api_handler():
  # ...
```

#### Metrics Libraries

Configure the crate that autometrics will use to produce metrics by using one of the following feature flags:

- `opentelemetry` - (enabled by default, can also be explicitly set using the AUTOMETRICS_TRACKER="OPEN_TELEMETERY" env var) uses
- `prometheus` - (using the AUTOMETRICS_TRACKER env var set to "PROMETHEUS")

## Identifying commits that introduced problems

> **NOTE** - As of writing, `build_info` will not work correctly when using the default tracker (`AUTOMETRICS_TRACKER=OPEN_TELEMETRY`).
> This will be fixed once the following PR is merged on the opentelemetry-python project: https://github.com/open-telemetry/opentelemetry-python/pull/3306
>
> autometrics-py will track support for build_info using the OpenTelemetry tracker via #38

Autometrics makes it easy to identify if a specific version or commit introduced errors or increased latencies.

It uses a separate metric (`build_info`) to track the version and, optionally, git commit of your service. It then writes queries that group metrics by the `version` and `commit` labels so you can spot correlations between those and potential issues.

The `version` is read from the `AUTOMETRICS_VERSION` environment variable, and the `commit` value uses the environment variable `AUTOMETRICS_COMMIT`.

This follows the method outlined in [Exposing the software version to Prometheus](https://www.robustperception.io/exposing-the-software-version-to-prometheus/).

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
- contains type definitions (which are linted by [pyright](https://microsoft.github.io/pyright/))
- tested using [pytest](https://docs.pytest.org/)

In order to run these tools locally you have to install them, you can install them using poetry:

```sh
poetry install --with dev
```

After that you can run the tools individually

```sh
# Formatting using black
poetry run black .
# Lint using pyright
poetry run pyright
# Run the tests using pytest
poetry run pytest
# Run a single test, and clear the cache
poetry run pytest --cache-clear -k test_tracker
```
