from typing_extensions import Unpack


from .tracker import init_tracker, get_tracker
from .tracker.temporary import TemporaryTracker
from .settings import AutometricsOptions, init_settings

has_inited = False


def init(**kwargs: Unpack[AutometricsOptions]):
    """Initialization function to be used instead of setting environment variables. You can override settings by calling init with the new settings."""
    global has_inited
    if has_inited:
        print("Warning: init() has already been called. This call will be ignored.")
        return
    has_inited = True
    temp_tracker = get_tracker()
    if not isinstance(temp_tracker, TemporaryTracker):
        print("Expected tracker to be TemporaryTracker. This call will be ignored.")
        return
    settings = init_settings(**kwargs)
    tracker = init_tracker(settings["tracker"], settings)
    temp_tracker.replay_queue(tracker)
