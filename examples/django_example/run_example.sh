#!/bin/sh

export AUTOMETRICS_COMMIT=67a1b3a
export AUTOMETRICS_VERSION=0.1.0
export AUTOMETRICS_BRANCH=main
export AUTOMETRICS_TRACKER=prometheus

# run the server itself
poetry run python manage.py runserver 8080 &
# run the locust load test and pipe stdout to dev/null
poetry run locust --host=http://localhost:8080 --users=100 --headless &

# kill all child processes on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
wait