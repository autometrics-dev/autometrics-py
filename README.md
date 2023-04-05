# autometrics-py

A Python decorator that makes it easy to understand the error rate, response time, and production usage of any function in your code. Jump straight from your IDE to live Prometheus charts for each HTTP/RPC handler, database method, or other piece of application logic.

Autometrics for Python provides a decorator that can create [Prometheus](https://prometheus.io/) metrics for your functions and class methods throughout your code base, as well as a function that will write corresponding Prometheus queries for you in a Markdown file.

[See Why Autometrics?](https://github.com/autometrics-dev#why-autometrics) for more details on the ideas behind autometrics

## Features

- ✨ `autometrics` decorator instruments any function or class method to track the
  most useful metrics
- 💡 Writes Prometheus queries so you can understand the data generated without
  knowing PromQL
- 🔗 Create links to live Prometheus charts directly into each functions docstrings (with tooltips coming soon!)
- 📊 (Coming Soon!) Grafana dashboard showing the performance of all
  instrumented functions
- 🚨 (Coming Soon!) Generates Prometheus alerting rules using SLO best practices
  from simple annotations in your code
- ⚡ Minimal runtime overhead

## Using autometrics-py

- Requirement: a running [prometheus instance](https://prometheus.io/download/)
- include a .env file with your prometheus endpoint `PROMETHEUS_URL = your endpoint`, if not defined the default endpoint will be `http://localhost:9090/`
- `pip install autometrics`
- Import the library in your code and use the decorator for any function:

```
from autometrics import autometrics

@autometrics
def sayHello:
   return "hello"

```

- If you like to access the queries for your decoraded functions you can run `help(yourfunction)` or `print(yourfunction.__doc__)`

- Unfortunately it is not possible to have the queries in the tooltips due to the [static Analyzer](https://github.com/davidhalter/jedi/issues/1921). We are currently figuring out to build a VS Code PlugIn to make it work.

## Development of the package

Code in this repository is formatted using [black](https://black.readthedocs.io/en/stable/) and contains type definitions (which are linted by [pyright](https://microsoft.github.io/pyright/))
