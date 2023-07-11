from prometheus_client.exposition import generate_latest
import asyncio
import pytest


from .tracker import set_tracker, TrackerType

from ..decorator import autometrics
from ..utils import get_function_name, get_module_name


@autometrics(track_concurrency=True)
async def sleep(time):
    await asyncio.sleep(time)


@pytest.mark.asyncio
async def test_concurrency_tracking_prometheus(monkeypatch):
    # HACK - We need to set the tracker explicitly here, instead of using `init_tracker`
    #        because the library was already initialized with the OpenTelemetry tracker
    set_tracker(TrackerType.PROMETHEUS)

    func_name = get_function_name(sleep)
    module_name = get_module_name(sleep)

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
        f"""# TYPE function_calls_concurrent gauge\nfunction_calls_concurrent{{function="sleep",module="autometrics.tracker.test_concurrency"}} 1.0"""
        in data
    )


# NOTE - Gauges are not supported by the OTEL collector (yet)
#        https://github.com/open-telemetry/opentelemetry-python/pull/3306
#
# @pytest.mark.asyncio
# async def test_concurrency_tracking_opentelemetry(monkeypatch):
#     # HACK - We need to set the tracker explicitly here, instead of using `init_tracker`
#     #        because the library was already initialized with the OpenTelemetry tracker
#     set_tracker(TrackerType.OPENTELEMETRY)

#     # Create a 200ms async task
#     loop = asyncio.get_event_loop()
#     task = loop.create_task(sleep(0.2))

#     # Await a separate 100ms async task.
#     # This way, the 200ms task will still running once this task is done.
#     # We have to do this to ensure that the 200ms task is kicked off before we call `generate_latest`
#     await sleep(0.1)
#     blob = generate_latest()
#     await task
#     assert blob is not None
#     data = blob.decode("utf-8")
#     print(data)
#     assert (
#         f"""# TYPE function_calls_concurrent gauge\nfunction_calls_concurrent{{function="sleep",module="test_concurrency"}} 1.0"""
#         in data
#     )
