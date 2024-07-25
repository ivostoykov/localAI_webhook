# main.py
from http.server import HTTPServer
import sys
from logger import logger  # This will initialize logging
from request_handler import RequestHandler

def start_server(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    base_url = f"http://localhost:{httpd.server_port}"
    logger.info(f"Local AI helper server running on port {port} ({base_url})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server has been stopped.")
        httpd.server_close()

if __name__ == "__main__":
    port = 10001
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    start_server(port)
