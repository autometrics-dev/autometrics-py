"""Test the autometrics decorator."""
from prometheus_client.exposition import generate_latest
from prometheus_client import registry, Metric
from pytest import raises

from .decorator import autometrics
from .objectives import ObjectiveLatency, Objective, ObjectivePercentile
from .utils import get_caller_function


def basic_function():
    """This is a basic function."""
    return True


def find_metric_with_name(metrics: "list[Metric]", name: str):
    """Find a metric with a given name."""
    for metric in metrics:
        if metric.name == name:
            return metric

    return None


def test_basic():
    """This is a basic test."""

    # set up the function + basic variables
    caller = get_caller_function(depth=1)
    assert caller is not None
    assert caller != ""
    function_name = basic_function.__name__
    wrapped_function = autometrics(basic_function)
    wrapped_function()

    # get the metrics
    blob = generate_latest(registry.REGISTRY)
    assert blob is not None
    data = blob.decode("utf-8")

    total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="ok"}} 1.0"""
    assert total_count in data
    count_created = f"""function_calls_count_created{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="ok"}}"""
    assert count_created in data

    for latency in ObjectiveLatency:
        query = f"""function_calls_duration_bucket{{function="{function_name}",le="{latency.value}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert query in data

    duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_count in data

    duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_sum in data

    duration_created = f"""function_calls_duration_created{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_created in data


def test_objectives():
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

    # call the function
    wrapped_function()

    # get the metrics
    blob = generate_latest(registry.REGISTRY)
    assert blob is not None
    data = blob.decode("utf-8")

    total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}} 1.0"""
    assert total_count in data
    count_created = f"""function_calls_count_created{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="{objective_name}",objective_percentile="{success_rate.value}",result="ok"}}"""
    assert count_created in data

    for objective in ObjectiveLatency:
        query = f"""function_calls_duration_bucket{{function="{function_name}",le="{objective.value}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
        assert query in data

    duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
    assert duration_count in data

    duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
    assert duration_sum in data

    duration_created = f"""function_calls_duration_created{{function="{function_name}",module="test_decorator",objective_latency_threshold="{latency[0].value}",objective_name="{objective_name}",objective_percentile="{latency[1].value}"}}"""
    assert duration_created in data


def error_function():
    """This is a function that raises an error."""
    raise RuntimeError("This is a test error")


def test_exception():
    caller = get_caller_function(depth=1)
    assert caller is not None
    assert caller != ""
    function_name = error_function.__name__
    wrapped_function = autometrics(error_function)
    with raises(RuntimeError) as exception:
        wrapped_function()
    assert "This is a test error" in str(exception.value)

    # get the metrics
    blob = generate_latest(registry.REGISTRY)
    assert blob is not None
    data = blob.decode("utf-8")
    print("data", data)

    total_count = f"""function_calls_count_total{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="error"}} 1.0"""
    assert total_count in data
    count_created = f"""function_calls_count_created{{caller="{caller}",function="{function_name}",module="test_decorator",objective_name="",objective_percentile="",result="error"}}"""
    assert count_created in data

    for latency in ObjectiveLatency:
        query = f"""function_calls_duration_bucket{{function="{function_name}",le="{latency.value}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
        assert query in data

    duration_count = f"""function_calls_duration_count{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_count in data

    duration_sum = f"""function_calls_duration_sum{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_sum in data

    duration_created = f"""function_calls_duration_created{{function="{function_name}",module="test_decorator",objective_latency_threshold="",objective_name="",objective_percentile=""}}"""
    assert duration_created in data
