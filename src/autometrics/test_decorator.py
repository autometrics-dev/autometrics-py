"""Test the autometrics decorator."""
import time
import asyncio
from typing import Optional, Coroutine
from prometheus_client.exposition import generate_latest
import pytest
from requests import HTTPError, Response

from .decorator import autometrics
from .initialization import init
from .objectives import ObjectiveLatency, Objective, ObjectivePercentile
from .tracker import TrackerType
from .utils import get_function_name, get_module_name

HTTP_ERROR_TEXT = "This is an http error"
CODE_NOT_SET_TEXT = "status code not set"


def basic_http_error_function(status_code: Optional[int] = 404):
    """This is a basic function that raises an HTTPError. Unless the status_code parameter is set to None"""

    if status_code is None:
        return CODE_NOT_SET_TEXT

    response = Response()
    response.status_code = status_code
    raise HTTPError(HTTP_ERROR_TEXT, response=response)


async def async_http_error_function(status_code: Optional[int] = 404):
    """This is a basic function that raises an HTTPError. Unless the status_code parameter is set to None"""
    await asyncio.sleep(0.2)

    if status_code is None:
        return CODE_NOT_SET_TEXT

    response = Response()
    response.status_code = status_code
    raise HTTPError(HTTP_ERROR_TEXT, response=response)


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


@pytest.fixture(params=tracker_types)
def setup_tracker_type(request):
    """Force the use of a specific metrics tracker"""
    init(tracker=request.param.value)


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

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="basic_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
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

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="basic_async_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
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

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="{function_name}",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        # Check the latency buckets
        for objective in ObjectiveLatency:
            count = 0 if float(objective.value) <= sleep_duration else 1
            query = f"""function_calls_duration_seconds_bucket{{function="{function_name}",le="{objective.value}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}} {count}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="{function_name}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="{function_name}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}}"""
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
        assert asyncio.iscoroutinefunction(wrapped_function) is True
        await wrapped_function(sleep_duration)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        # Check the latency buckets
        for objective in ObjectiveLatency:
            count = 0 if float(objective.value) <= sleep_duration else 1
            query = f"""function_calls_duration_seconds_bucket{{function="basic_async_function",le="{objective.value}",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}} {count}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_async_function",module="autometrics.test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}",service_name="autometrics"}}"""
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

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="error_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_sum in data

    def test_record_success_if(self):
        """This is a test that tests exceptions that may or may not be reported as an error"""

        def record_success_if(exception: Exception):
            return isinstance(exception, HTTPError)

        def record_error_if(result: str):
            return result == CODE_NOT_SET_TEXT

        wrapped_function = autometrics(
            record_success_if=record_success_if, record_error_if=record_error_if
        )(basic_http_error_function)

        with pytest.raises(HTTPError) as exception:
            wrapped_function(status_code=404)

        assert HTTP_ERROR_TEXT in str(exception.value)
        assert exception.value.response.status_code == 404

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 0.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="basic_http_error_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="basic_http_error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="basic_http_error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_sum in data

        # Calling the test function with None should result in no exception but it should still be marked as an error according to the metrics
        result = wrapped_function(status_code=None)
        assert result == CODE_NOT_SET_TEXT

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data
        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="basic_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 1.0"""
        assert total_count in data

    @pytest.mark.asyncio
    async def test_async_record_success_or_ok_if(self):
        """This is a test that tests exceptions that may or may not be reported as an error"""

        def record_success_if(exception: Exception):
            return isinstance(exception, HTTPError)

        def record_error_if(result: str):
            return result == CODE_NOT_SET_TEXT

        wrapped_function = autometrics(
            record_success_if=record_success_if, record_error_if=record_error_if
        )(async_http_error_function)

        with pytest.raises(HTTPError) as exception:
            await wrapped_function(status_code=404)

        assert HTTP_ERROR_TEXT in str(exception.value)
        assert exception.value.response.status_code == 404

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="async_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="async_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 0.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="async_http_error_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="async_http_error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="async_http_error_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_sum in data

        # Calling the test function with None should result in no exception but it should still be marked as an error according to the metrics
        result = await wrapped_function(status_code=None)
        assert result == CODE_NOT_SET_TEXT

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="async_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 1.0"""
        assert total_count in data
        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="async_http_error_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 1.0"""
        assert total_count in data

    @pytest.mark.asyncio
    async def test_async_exception(self):
        """This is a test that covers exceptions."""

        wrapped_function = autometrics(error_async_function)

        # Test that the function is *still* async after we wrap it
        assert asyncio.iscoroutinefunction(wrapped_function) is True

        with pytest.raises(RuntimeError) as exception:
            await wrapped_function()
        assert "This is a test error" in str(exception.value)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_total{{caller_function="",caller_module="",function="error_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_seconds_bucket{{function="error_async_function",le="{latency.value}",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
            assert query in data

        duration_count = f"""function_calls_duration_seconds_count{{function="error_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_seconds_sum{{function="error_async_function",module="autometrics.test_decorator",objective_latency_threshold="",objective_name="",objective_percentile="",service_name="autometrics"}}"""
        assert duration_sum in data

    def test_initialize_counters_sync(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator."""

        autometrics(never_called_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 0.0"""
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

        total_count_ok = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok",service_name="autometrics"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="error",service_name="autometrics"}} 0.0"""
        assert total_count_error in data

    @pytest.mark.asyncio
    async def test_initialize_counters_async(self):
        """This is a test to see if the function calls metric initializes at 0 after invoking the decorator for an async function"""

        autometrics(never_called_async_function)
        # NOTE - Do not call the function! We want to see if we get counter data for it even without ever calling it

        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count_ok = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="ok",service_name="autometrics"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="",objective_percentile="",result="error",service_name="autometrics"}} 0.0"""
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

        total_count_ok = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok",service_name="autometrics"}} 0.0"""
        assert total_count_ok in data

        total_count_error = f"""function_calls_total{{caller_function="",caller_module="",function="never_called_async_function",module="autometrics.test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="error",service_name="autometrics"}} 0.0"""
        assert total_count_error in data
