FROM python:3.11
# Install dependencies manually
# This is the easiest way in the current set up (given that this example is nested in 
# the autometrics-py repository) but it's in no way a best practice. :)
RUN pip install fastapi autometrics prometheus-client uvicorn

WORKDIR /code

# Copy the python code into the container
COPY app.py /code/

# Expose the port that the app (by default) is running on
EXPOSE 8080

# Start the app in a flexible way, so it can be run on Heroku, Azure App Services, or locally
# Heroku uses PORT, Azure App Services uses WEBSITES_PORT, Fly.io uses 8080 by default
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-${WEBSITES_PORT:-8080}}"]