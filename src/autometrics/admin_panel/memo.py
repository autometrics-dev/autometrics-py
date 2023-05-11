FUNCTIONS = []


def add_to_admin_panel(func_name: str, module_name: str):
    global FUNCTIONS
    FUNCTIONS.append([func_name, module_name])


def get_decorated_functions_list():
    global FUNCTIONS
    return FUNCTIONS
