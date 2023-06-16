# This module will do some bookkeeping on information of any functions that have been wrapped by autometrics decorators

from typing import List, TypedDict, Optional

from ..tracker import TrackMetrics
from ..objectives import Objective


class FunctionInfo(TypedDict):
    name: str
    module: str


FUNCTION_REGISTRY: List[FunctionInfo] = []


def register_function_info(
    func_name: str,
    module_name: str,
    tracker: TrackMetrics,
    objective: Optional[Objective] = None,
):
    global FUNCTION_REGISTRY
    function_info: FunctionInfo = {"name": func_name, "module": module_name}
    FUNCTION_REGISTRY.append(function_info)

    # HACK - Initialize counter at zero
    tracker.initialize_at_zero(
        function=func_name, module=module_name, objective=objective
    )


def get_decorated_functions_list():
    global FUNCTION_REGISTRY
    return FUNCTION_REGISTRY
