import os
import http.server
import socketserver
import threading
import logging
from .function_registry import get_decorated_functions_list


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello, World!")


def _start_admin_server():
    port = int(os.getenv("AUTOMETRICS_ADMIN_PORT") or "5761")
    handler = MyHTTPRequestHandler
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"Autometrics admin panel running on http://localhost:{port}")
        httpd.serve_forever


# FIXME - This server dies when called externally
def run_admin_server():
    server_thread = threading.Thread(target=_start_admin_server)
    server_thread.daemon = True
    server_thread.start()


def get_functions_as_html_list_items():
    functions = get_decorated_functions_list()
    return "\n".join(
        [f"""<li>{func["module"]}:{func["name"]}</li>""" for func in functions]
    )


def get_autometrics_admin_html():
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Autometrics Overview</title>
</head>
<body>
  <h1>Hello, Autometrics!</h1>
  <h2>This is a list of the functions you are tracking.</h2>
  <ul>
    {get_functions_as_html_list_items()}
  </ul>
</body>
</html>"""
