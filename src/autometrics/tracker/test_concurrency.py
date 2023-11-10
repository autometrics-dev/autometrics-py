from prometheus_client.exposition import generate_latest
import asyncio
import pytest

from ..decorator import autometrics
from ..initialization import init


@autometrics(track_concurrency=True)
async def sleep(time: float):
    await asyncio.sleep(time)


@pytest.mark.asyncio
async def test_concurrency_tracking_prometheus(monkeypatch):
    init(tracker="prometheus")

    # Create a 200ms async task
    loop = asyncio.get_event_loop()
    task = loop.create_task(sleep(0.2))

    # Await a separate 100ms async task.
    # This way, the 200ms task will still running once this task is done.
    # We have to do this to ensure that the 200ms task is kicked off before we call `generate_latest`
    await sleep(0.1)
    blob = generate_latest()
    await task
    assert blob is not None
    data = blob.decode("utf-8")

    assert (
        f"""# TYPE function_calls_concurrent gauge\nfunction_calls_concurrent{{function="sleep",module="autometrics.tracker.test_concurrency",service_name="autometrics"}} 1.0"""
        in data
    )


@pytest.mark.asyncio
async def test_concurrency_tracking_opentelemetry(monkeypatch):
    init(tracker="opentelemetry")

    # Create a 200ms async task
    loop = asyncio.get_event_loop()
    task = loop.create_task(sleep(0.2))

    # Await a separate 100ms async task.
    # This way, the 200ms task will still running once this task is done.
    # We have to do this to ensure that the 200ms task is kicked off before we call `generate_latest`
    await sleep(0.1)
    blob = generate_latest()
    await task
    assert blob is not None
    data = blob.decode("utf-8")
    assert (
        f"""# TYPE function_calls_concurrent gauge\nfunction_calls_concurrent{{function="sleep",module="autometrics.tracker.test_concurrency",service_name="autometrics"}} 1.0"""
        in data
    )
