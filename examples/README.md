# autometrics-py examples

You should be able to run each example by:

- cloning this repository
- run `poetry install --with examples`
- and execute `poetry run python examples/<example>.py` from the root of the repo.
- for django and starlette examples, you can find the exact commands below

You can change the base url for Prometheus links via the `PROMETHEUS_URL` environment variable. So, if your local Prometheus were on a non-default port, like 9091, you would run:

```sh
PROMETHEUS_URL=http://localhost:9091/ python examples/example.py
```

Read more below about each example, and what kind of features they demonstrate.

Also, for the examples that expose a `/metrics` endpoint, you will need to configure Prometheus to scrape that endpoint. There is an example `prometheus.yaml` file in the root of this project, but here is the relevant part:

```yaml
# Example prometheus.yaml
scrape_configs:
  - job_name: "python-autometrics-example"
    metrics_path: /metrics
    static_configs:
      - targets: ["localhost:8080"]
    # For a real deployment, you would want the scrape interval to be
    # longer but for testing, you want the data to show up quickly
    scrape_interval: 500ms
```

## `docs-example.py`

This script shows how the autometrics decorator augments the docstring for a python function.

We simply decorate a function, then print its docstring to the console using the built-in `help` function.

## `example.py`

This script demonstrates the basic usage of the `autometrics` decorator. When you run `python examples/example.py`, it will output links to metrics in your configured prometheus instance.

You can read the script for comments on how it works, but the basic idea is that we have a division function (`div_unhandled`) that occasionally divides by zero and does not catch its errors. We can see its error rate in prometheus via the links in its doc string.

Note that the script starts an HTTP server on port 8080 using the Prometheus client library, which exposes metrics to prometheus (via a `/metrics` endpoint).

Then, it enters into an infinite loop (with a 2 second sleep period), calling methods repeatedly with different input parameters. This should start generating data that you can explore in Prometheus. Just follow the links that are printed to the console!

> Don't forget to configure Prometheus itself to scrape the metrics endpoint. Refer to the example `prometheus.yaml` file in the root of this project on how to set this up.

## `caller-example.py`

Autometrics also tracks a label, `caller`, which is the name of the function that called the decorated function. The `caller-example.py` script shows how to use that label. It uses the same structure as the `example.py` script, but it prints a PromQL query that you can use to explore the caller data yourself.

> Don't forget to configure Prometheus itself to scrape the metrics endpoint. Refer to the example `prometheus.yaml` file in the root of this project on how to set this up.

## `fastapi-example.py`

This is an example that shows you how to use autometrics to get metrics on http handlers with FastAPI. In this case, we're setting up the API ourselves, which means we need to expose a `/metrics` endpoint manually.

> Don't forget to configure Prometheus itself to scrape the metrics endpoint. Refer to the example `prometheus.yaml` file in the root of this project on how to set this up.

## `django-example`

This is a default Django project with autometrics configured. You can find examples of instrumenting function and class based views in `django_example/views`. To run the example, navigate to `django_example` directory and run the standard command:

`python manage.py runserver 8080`

> Don't forget to configure Prometheus itself to scrape the metrics endpoint. Refer to the example `prometheus.yaml` file in the root of this project on how to set this up.

## `starlette-otel-exemplars.py`

This app shows how to use the OpenTelemetry integration to add exemplars to your metrics. In a distributed system, it allows you to track a request as it flows through your system by adding trace/span ids to it. We can catch these ids from OpenTelemetry and expose them to Prometheus as exemplars. Do note that exemplars are an experimental feature and you need to enable it in Prometheus with a `--enable-feature=exemplar-storage` flag.

> Don't forget to configure Prometheus itself to scrape the metrics endpoint. Refer to the example `prometheus.yaml` file in the root of this project on how to set this up.
