# This module will do some bookkeeping on information of any functions that have been wrapped by autometrics decorators

from typing import List, TypedDict


class FunctionInfo(TypedDict):
    name: str
    module: str


FUNCTION_REGISTRY: List[FunctionInfo] = []


def register_function_info(func_name: str, module_name: str):
    global FUNCTION_REGISTRY
    function_info: FunctionInfo = {"name": func_name, "module": module_name}
    FUNCTION_REGISTRY.append(function_info)


def get_decorated_functions_list():
    global FUNCTION_REGISTRY
    return FUNCTION_REGISTRY
