import os
import http.server
import socketserver
import threading
import logging
import json

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


def get_autometrics_admin_html(
    cdn_root=None, css_hash=None, js_hash=None, prom_url=None
):
    cdn_root = cdn_root or "https://quickmetrics-ui.pages.dev"
    css_hash = css_hash or "3527160e"
    js_hash = js_hash or "24432f8e"
    prom_url = prom_url or os.getenv("PROMETHEUS_URL")
    return f"""
    <!DOCTYPE html><html lang="en"><head><link rel="stylesheet" href="{cdn_root}/static/css/index.{css_hash}.css"><meta charset="utf-8"><link rel="icon" type="image/svg" href="/favicon.raw.d2e6412d.svg"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Fiberplane</title></head><body> <noscript>You need to enable JavaScript to run this app.</noscript> <div id="root"></div> <textarea id="autometrics-data" style="display:none">
     {json.dumps(get_decorated_functions_list())}
    </textarea>
    <textarea id="am-prometheus-url" style="display: none" role="hidden">{prom_url}</textarea>
    <script type="module" src="{cdn_root}/static/js/index.{js_hash}.js"></script> </body></html>
    """
