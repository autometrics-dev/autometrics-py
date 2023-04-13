import os
import yaml
from dotenv import load_dotenv, find_dotenv
from typing import Any, Dict
from .constants import ENV_FP_METRICS_URL

load_dotenv()

LOADED_CONFIG = None

APP_NAME_KEY = "app_name"
PUBLISH_METHOD_KEY = "publish_method"


# HACK - Use the dotenv `find_dotenv`` function to locate the autometrics.yaml file (searches recursively in parent dirs)
def find_autometrics_yaml() -> str:
    """Find the autometrics.yaml file in the project root. Returns empty string if not found"""
    yaml_file_path = find_dotenv("autometrics.yaml")
    if yaml_file_path == "":
        yaml_file_path = find_dotenv("autometrics.yml")
    return yaml_file_path


# TODO - Narrow type definition, add a decoder for our config file
def load_config_file() -> Dict[str, Any]:
    global LOADED_CONFIG
    """Load the autometrics.yaml file."""
    if LOADED_CONFIG is not None:
        return LOADED_CONFIG
    config_path = find_autometrics_yaml()
    try:
        with open(config_path, "r") as config_file:
            LOADED_CONFIG = yaml.safe_load(config_file)
    except FileNotFoundError:
        LOADED_CONFIG = {}
    return LOADED_CONFIG


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a value from the autometrics.yaml file."""
    config = load_config_file()
    return config.get(key, default)


def get_app_name() -> str:
    """Get the app name from the autometrics.yaml file."""
    return get_config_value(APP_NAME_KEY, "default_app_name")


def get_is_pushing_metrics() -> str:
    """Get whether or not we should push metrics to a gateway from the autometrics.yaml file."""
    return get_config_value(PUBLISH_METHOD_KEY, "XXX") == "push"


def get_push_gateway_url() -> str:
    """Get the push gateway URL from the autometrics.yaml file."""
    return os.getenv(ENV_FP_METRICS_URL, "")
