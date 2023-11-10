import inspect
import os

from collections.abc import Callable
from typing import Optional
from urllib.parse import urlparse
from prometheus_client import start_wsgi_server, REGISTRY, CollectorRegistry

from .prometheus_url import Generator


def get_module_name(func: Callable) -> str:
    """Get the name of the module that contains the function."""
    module = inspect.getmodule(func)
    if module is None or module.__name__ == "__main__":
        return get_filename_as_module(func)
    return module.__name__


def get_filename_as_module(func: Callable) -> str:
    """Get the filename of the module that contains the function."""
    fullpath = inspect.getsourcefile(func)
    if fullpath is None:
        return ""

    filename = os.path.basename(fullpath)
    module_part = os.path.splitext(filename)[0]
    return module_part


def get_function_name(func: Callable) -> str:
    """Get the name of the function."""
    return func.__qualname__ or func.__name__


def write_docs(func_name: str, module_name: str):
    """Write the prometheus query urls to the function docstring."""
    generator = Generator(func_name, module_name)
    docs = f"Prometheus Query URLs for Function - {func_name} and Module - {module_name}: \n\n"

    urls = generator.create_urls()
    for key, value in urls.items():
        docs = f"{docs}{key} : {value} \n\n"

    docs = f"{docs}-------------------------------------------\n"
    return docs


def append_docs_to_docstring(func, func_name, module_name):
    """Helper for appending docs to a function's docstring."""
    if func.__doc__ is None:
        return write_docs(func_name, module_name)
    else:
        return f"{func.__doc__}\n{write_docs(func_name, module_name)}"


def start_http_server(
    port: int = 9464, addr: str = "0.0.0.0", registry: CollectorRegistry = REGISTRY
):
    """Starts a WSGI server for prometheus metrics as a daemon thread."""
    start_wsgi_server(port, addr, registry)


def read_repository_url_from_fs() -> Optional[str]:
    """Read the repository url from git config."""
    try:
        with open(".git/config", "r") as f:
            git_config = f.read()
            return get_repository_url(git_config)
    except:
        return None


def get_repository_url(git_config: str) -> Optional[str]:
    """Get the repository url from git config."""
    lines = git_config.split("\n")
    is_in_remote_origin = False
    for line in lines:
        stripped_line = line.strip()
        # skip empty lines and comments
        if (
            line == "\n"
            or stripped_line.startswith("#")
            or stripped_line.startswith(";")
        ):
            continue

        if not is_in_remote_origin:
            lower_line = stripped_line.lower()
            # we are looking for the remote origin section
            # and skip everything else
            if lower_line in ['[remote "origin"]', "[remote.origin]"]:
                is_in_remote_origin = True
            continue

        # once inside the remote origin section, we are looking for key/value pairs
        # they are required to have '=' in them
        equal_index = stripped_line.find("=")
        if equal_index == -1:
            if stripped_line.startswith("["):
                # we have reached the end of the remote origin section
                is_in_remote_origin = False
            continue

        key = stripped_line[:equal_index].strip()
        # we are looking for the url key
        if key != "url":
            continue

        value = stripped_line[equal_index + 1 :].strip()
        # remove quotes and escape sequences
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace("\\\\", "\\").replace('\\"', '"')

        return value

    return None


def extract_repository_provider(url: str) -> Optional[str]:
    # we assume that there will be two types of urls:
    # https and ssh. urlparse can handle first type
    # so we try that first
    parsed_url = urlparse(url)
    if parsed_url.scheme == "https" and parsed_url.hostname:
        return get_provider_by_hostname(parsed_url.hostname)
    # if that fails, we try the second type, but we will need to
    # append the scheme to the url for urlparse to work
    parsed_url = urlparse(f"ssh://{url}")
    if parsed_url.hostname:
        return get_provider_by_hostname(parsed_url.hostname)
    return None


def get_provider_by_hostname(hostname: str) -> str:
    if hostname in ["github.com", "gitlab.com", "bitbucket.org"]:
        return hostname.split(".")[0]
    return hostname
