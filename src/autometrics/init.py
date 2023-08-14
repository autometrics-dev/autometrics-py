from typing_extensions import Unpack

from .settings import AutometricsOptions, init_settings
from .tracker import set_tracker, get_tracker_type


def init(**kwargs: Unpack[AutometricsOptions]):
    """Optional initialization function to be used instead of setting environment variables. You can override settings by calling init with the new settings."""
    init_settings(**kwargs)
    tracker_type = get_tracker_type()
    set_tracker(tracker_type)
