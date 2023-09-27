import logging
import os

from typing_extensions import Unpack


from .tracker import init_tracker, get_tracker
from .tracker.temporary import TemporaryTracker
from .settings import AutometricsOptions, init_settings

has_inited = False
DOUBLE_INIT_ERROR = "Cannot call init() more than once."
NOT_TEMP_TRACKER_ERROR = "Expected tracker to be TemporaryTracker."


def init(**kwargs: Unpack[AutometricsOptions]):
    """Initialization function that is used to configure autometrics. This function should be called
    immediately after starting your app. You cannot call this function more than once.
    """
    global has_inited
    if has_inited:
        if os.environ.get("AUTOMETRICS_DEBUG") == "true":
            raise RuntimeError(DOUBLE_INIT_ERROR)
        else:
            logging.warn(f"{DOUBLE_INIT_ERROR} This init() call will be ignored.")
            return
    has_inited = True

    temp_tracker = get_tracker()
    if not isinstance(temp_tracker, TemporaryTracker):
        if os.environ.get("AUTOMETRICS_DEBUG") == "true":
            raise RuntimeError(NOT_TEMP_TRACKER_ERROR)
        else:
            logging.warn(f"{NOT_TEMP_TRACKER_ERROR} This init() call will be ignored.")
            return
    settings = init_settings(**kwargs)
    tracker = init_tracker(settings["tracker"], settings)
    temp_tracker.replay_queue(tracker)
