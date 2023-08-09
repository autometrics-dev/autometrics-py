"""Test the autometrics decorator."""
import time
import asyncio
from prometheus_client.exposition import generate_latest
import pytest

from .decorator import autometrics
from .objectives import ObjectiveLatency, Objective, ObjectivePercentile
from .tracker import set_tracker, TrackerType
from .utils import get_function_name, get_module_name


def basic_function(sleep_duration: float = 0.0):
    """This is a basic function."""
    time.sleep(sleep_duration)
    return True


def error_function():
    """This is a function that raises an error."""
    raise RuntimeError("This is a test error")


async def basic_async_function(sleep_duration: float = 1.0):
    """This is a basic async function."""
    await asyncio.sleep(sleep_duration)
    return True


async def error_async_function():
    """This is an async function that raises an error."""
    await asyncio.sleep(0.5)
    raise RuntimeError("This is a test error")


def never_called_function():
    """This is a sync function that should never be called. Used for testing initialization at zero for counters"""
    raise RuntimeError("This function should never be called")


async def never_called_async_function():
    """This is an async function that should never be called. Used for testing initialization at zero for counters"""
    raise RuntimeError("This function should never be called")


tracker_types = [TrackerType.PROMETHEUS, TrackerType.OPENTELEMETRY]


@pytest.fixture(scope="class", params=tracker_types)
def setup_tracker_type(request):
    """Force the use of a specific metrics tracker"""
    set_tracker(request.param)


@pytest.mark.usefixtures("setup_tracker_type")
class TestDecoratorClass:
    """Test the autometrics decorator. These tests are run multiple times with different trackers."""

    def test_basic(self):
        """This is a basic test."""

        wrapped_function = autometrics(basic_function)
        wrapped_function()

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="basic_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="basic_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data

    @pytest.mark.asyncio
    async def test_basic_async(self):
        """This is a basic test."""

        wrapped_function = autometrics(basic_async_function)

        # Test that the function is *still* async after we wrap it
        assert asyncio.iscoroutinefunction(wrapped_function) == True

        await wrapped_function()

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="basic_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="basic_async_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data

    def test_objectives(self):
        """This is a test that covers objectives."""

        # set up the function + objective variables
        objective_name = "test_objective"
        success_rate = ObjectivePercentile.P90
        latency = (ObjectiveLatency.Ms100, ObjectivePercentile.P99)
        objective = Objective(
            name=objective_name, success_rate=success_rate, latency=latency
        )
        function_name = get_function_name(basic_function)
        module_name = get_module_name(basic_function)
        wrapped_function = autometrics(objective=objective)(basic_function)

        sleep_duration = 0.25
        # call the function
        wrapped_function(sleep_duration)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="{function_name}",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 1.0"""
        assert total_count in data

        # Check the latency buckets
        for objective in ObjectiveLatency:
            count = 0 if float(objective.value) <= sleep_duration else 1
            query = f"""function_calls_duration_seconds_bucket{{function="{function_name}",le="{objective.value}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}} {count}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="{function_name}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="{function_name}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_sum in data

    @pytest.mark.asyncio
    async def test_objectives_async(self):
        """This is a test that covers objectives for async functions."""

        # set up the function + objective variables
        objective_name = "test_objective"
        success_rate = ObjectivePercentile.P90
        latency = (ObjectiveLatency.Ms100, ObjectivePercentile.P99)
        objective = Objective(
            name=objective_name, success_rate=success_rate, latency=latency
        )
        wrapped_function = autometrics(objective=objective)(basic_async_function)

        sleep_duration = 0.25

        # Test that the function is *still* async after we wrapped it
        assert asyncio.iscoroutinefunction(wrapped_function) == True

        await wrapped_function(sleep_duration)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="basic_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 1.0"""
        assert total_count in data

        # Check the latency buckets
        for objective in ObjectiveLatency:
            count = 0 if float(objective.value) <= sleep_duration else 1
            query = f"""function_calls_duration_seconds_bucket{{function="basic_async_function",le="{objective.value}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}} {count}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_sum in data

    def test_exception(self):
        """This is a test that covers exceptions."""

        wrapped_function = autometrics(error_function)

        with pytest.raises(RuntimeError) as exception:
            wrapped_function()
        assert "This is a test error" in str(exception.value)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="error_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data

    @pytest.mark.asyncio
    async def test_async_exception(self):
        """This is a test that covers exceptions."""

        wrapped_function = autometrics(error_async_function)

        # Test that the function is *still* async after we wrap it
        assert asyncio.iscoroutinefunction(wrapped_function) == True

        with pytest.raises(RuntimeError) as exception:
            await wrapped_function()
        assert "This is a test error" in str(exception.value)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller="",function="error_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="error_async_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="error_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="error_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data

    def test_initialize_counters_sync(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator."""

        autometrics(never_called_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller="",function="never_called_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller="",function="never_called_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error"}} 0.0"""
        assert total_count_error in data

    def test_initialize_counters_sync_with_objective(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator."""

        objective_name = "test_objective"
        success_rate = ObjectivePercentile.P90
        objective = Objective(name=objective_name, success_rate=success_rate)

        autometrics(objective=objective)(never_called_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller="",function="never_called_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller="",function="never_called_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="error"}} 0.0"""
        assert total_count_error in data

    @pytest.mark.asyncio
    async def test_initialize_counters_async(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator for an async function"""

        autometrics(never_called_async_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it even without ever calling it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error"}} 0.0"""
        assert total_count_error in data

    @pytest.mark.asyncio
    async def test_initialize_counters_async_with_objective(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator for an async function"""

        objective_name = "test_objective"
        success_rate = ObjectivePercentile.P90
        objective = Objective(name=objective_name, success_rate=success_rate)

        autometrics(objective=objective)(never_called_async_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it even without ever calling it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="error"}} 0.0"""
        assert total_count_error in data
