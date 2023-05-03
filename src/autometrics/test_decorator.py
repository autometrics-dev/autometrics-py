"""Test the autometrics decorator."""
import time
from prometheus_client.exposition import generate_latest
import pytest

from .decorator import autometrics
from .objectives import ObjectiveLatency, Objective, ObjectivePercentile

from .tracker import set_tracker, TrackerType
from .utils import get_caller_function


def basic_function(sleep_duration: float = 0.0):
    """This is a basic function."""
    time.sleep(sleep_duration)
    return True


def error_function():
    """This is a function that raises an error."""
    raise RuntimeError("This is a test error")


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

        # set up the function + basic variables
        caller = get_caller_function(depth=1)
        assert caller is not None
        assert caller != ""
        function_name = basic_function.__name__
        wrapped_function = autometrics(basic_function)
        wrapped_function()

        time.sleep(1)
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="ok"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_bucket{{function="{function_name}",le="{latency.value}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data

    def test_objectives(self):
        """This is a test that covers objectives."""

        # set up the function + objective variables
        caller = get_caller_function(depth=1)
        assert caller is not None
        assert caller != ""
        objective_name = "test_objective"
        success_rate = ObjectivePercentile.P90
        latency = (ObjectiveLatency.Ms100, ObjectivePercentile.P99)
        objective = Objective(
            name=objective_name, success_rate=success_rate, latency=latency
        )
        function_name = basic_function.__name__
        wrapped_function = autometrics(objective=objective)(basic_function)

        sleep_duration = 0.25
        # call the function
        wrapped_function(sleep_duration)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 1.0"""
        assert total_count in data

        # Check the latency buckets
        for objective in ObjectiveLatency:
            count = 0 if float(objective.value) <= sleep_duration else 1
            query = f"""function_calls_duration_bucket{{function="{function_name}",le="{objective.value}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}} {count}"""
            assert query in data

        duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert duration_sum in data

    def test_exception(self):
        """This is a test that covers exceptions."""
        caller = get_caller_function(depth=1)
        assert caller is not None
        assert caller != ""

        function_name = error_function.__name__
        wrapped_function = autometrics(error_function)

        with pytest.raises(RuntimeError) as exception:
            wrapped_function()
        assert "This is a test error" in str(exception.value)

        # get the metrics
        blob = generate_latest()
        assert blob is not None
        data = blob.decode("utf-8")

        total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="error"}} 1.0"""
        assert total_count in data

        for latency in ObjectiveLatency:
            query = f"""function_calls_duration_bucket{{function="{function_name}",le="{latency.value}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
            assert query in data

        duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_count in data

        duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert duration_sum in data
