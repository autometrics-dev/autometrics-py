import logging

from autometrics.objectives import Objective


def test_objective_name_warning(caplog):
    """Test that a warning is logged when an objective name contains invalid characters."""
    caplog.set_level(logging.WARNING)
    caplog.clear()
    Objective("Incorrect name.")
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "contains invalid characters" in caplog.records[0].message
    caplog.clear()
    Objective("correct-name-123")
    assert len(caplog.records) == 0
