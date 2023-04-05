# autometrics-py examples

You should be able to run each example by running `python examples/<example>.py` from the root of the repo.

You can change the base url for Prometheus links via the `PROMETHEUS_URL` environment variable. For example:

```sh
PROMETHEUS_URL=http://localhost:9091/ python examples/example.py
```

Read more below about each example, and what kind of features they demonstrate.

## `docs-example.py`

This script shows how the autometrics decorator augments the docstring for a python function.

We simply decorate a function, then print its docstring to the console using the built-in `help` function.

## `example.py`

This script demonstrates the basic usage of the `autometrics` decorator. When you run `python examples/example.py`, it will output links to metrics in your configured prometheus instance. You can change the base url for prometheus links via the `PROMETHEUS_URL` environment variable

```sh
PROMETHEUS_URL=http://localhost:9091/ python examples/example.py
```

This Python script defines a class called "Operations" that has too methods: "add", "div_handled". These methods perform addition and division operations, respectively, and include code to handle potential errors.

There is also a top-level function named "div_unhandled", which performs division without handling any errors.

To test out autometrics, we start an HTTP server on port 8080 using the Prometheus client library, which exposes our metrics to prometheus (via a `/metrics` endpoint).

Then, we enter an infinite loop (with a 2 second sleep period), calling the "div_handled", "add", and "div_unhandled" methods repeatedly with different input parameters.

This should start generating data that you can explore in prometheus. Just follow the links that are printed to the console!

Don't forget to configure prometheus to scrape the metrics endpoint!

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
