
FROM python:latest
ARG COPY_PATH
ARG COMMAND
ARG PORT
WORKDIR /app
RUN apt-get update
RUN pip install poetry
COPY pyproject.toml poetry.lock src ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --with examples --extras "exporter-otlp-proto-http"
COPY $COPY_PATH ./
ENV OTEL_EXPORTER_OTLP_ENDPOINT http://host.docker.internal:4318
ENV COMMAND $COMMAND
ENV PORT $PORT
EXPOSE $PORT
CMD ["sh", "-c", "$COMMAND"]