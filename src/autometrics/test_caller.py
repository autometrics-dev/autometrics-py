"""Tests for caller tracking."""
from functools import wraps
from prometheus_client.exposition import generate_latest

from .decorator import autometrics


def test_caller_detection():
    """This is a test to see if the caller is properly detected."""

    def dummy_decorator(func):
        @wraps(func)
        def dummy_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return dummy_wrapper

    def another_decorator(func):
        @wraps(func)
        def another_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return another_wrapper

    @dummy_decorator
    @autometrics
    @another_decorator
    def foo():
        pass

    @autometrics
    def bar():
        foo()

    bar()

    blob = generate_latest()
    assert blob is not None
    data = blob.decode("utf-8")

    expected = """function_calls_count_total{caller="test_caller_detection.<locals>.bar",function="test_caller_detection.<locals>.foo",module="autometrics.test_caller",objective_name="",objective_percentile="",result="ok"} 1.0"""
    assert "wrapper" not in data
    assert expected in data
