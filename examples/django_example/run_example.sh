#!/bin/sh

# run the server itself
poetry run python manage.py runserver 0.0.0.0:9464 &
# run the locust load test
poetry run locust --host=http://localhost:9464 --users=100 --headless --skip-log-setup &

# kill all child processes on exit
trap "trap - SIGTERM && kill -- -$$" INT TERM EXIT
wait