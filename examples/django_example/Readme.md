# Autometrics Django example

This example project illustrates how you can integrate autometrics into a Django application.

## Running the example

**Note:** You will need [prometheus](https://prometheus.io/download/) installed locally.

Install dependencies from root project:

```shell
poetry install --with examples
```

Next, run the Django server:

```shell
poetry run python3 manage.py runserver
```

Now when you visit any of the routes marked with `@autometrics`, you should see metrics added to prometheus.
