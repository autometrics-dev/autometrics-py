from prometheus_client.exposition import generate_latest
import asyncio
import pytest


from .tracker import init_tracker, TrackerType

from ..decorator import autometrics


@pytest.mark.asyncio
async def test_concurrency_tracking(monkeypatch):
    @autometrics(track_concurrency=True)
    async def sleep(time):
        await asyncio.sleep(time)

    tracker = init_tracker(TrackerType.OPENTELEMETRY)

    tasks = [sleep(1), sleep(1)]
    sleep(2)
    await asyncio.gather(*tasks)
    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")
    print(data)
    assert (
        f"""# TYPE function_calls_concurrent gauge function_calls_concurrent{{function="sleep",module="test_concurrency"}} 1.0"""
        in data
    )
