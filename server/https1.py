import http.server
import ssl
import logging
from socketserver import ThreadingMixIn

# Configure logging
LOG_FILENAME = "/vagrant/results/server.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
RESPONSE = "Hello, HTTPS1!"
HOST = "0.0.0.0"
PORT = 443
CERTFILE = "/vagrant/server/cert/server.pem"
KEYFILE = "/vagrant/server/cert/server.pem"


class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """A simple HTTP request handler."""

    def do_GET(self):
        """Handle GET requests."""
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(RESPONSE)))
            self.end_headers()
            self.wfile.write(RESPONSE.encode())
            logging.info("Handled GET request from %s", self.client_address)
        except Exception as e:
            logging.error("Error handling GET request: %s", e)
            self.send_response(500)
            self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """A threaded HTTP server to handle multiple connections."""


def create_ssl_context(certfile, keyfile):
    """Create and configure an SSL context."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    logging.info("SSL context created with certfile: %s and keyfile: %s", certfile, keyfile)
    return context


def run_server(host, port, certfile, keyfile):
    """Run the HTTPS server."""
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, SimpleHTTPRequestHandler)

    try:
        # Set up SSL
        ssl_context = create_ssl_context(certfile, keyfile)
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

        logging.info("Starting server on https://%s:%d", host, port)
        print(f"Serving on https://{host}:{port}")
        httpd.serve_forever()
    except FileNotFoundError as fnf_error:
        logging.error("File not found: %s", fnf_error)
        print(f"Error: {fnf_error}. Check the certificate and key file paths.")
    except PermissionError as perm_error:
        logging.error("Permission error: %s", perm_error)
        print(f"Error: {perm_error}. Try running the script with elevated privileges or change the port to above 1024.")
    except Exception as e:
        logging.error("Server failed with error: %s", e)
        print(f"Server failed with error: {e}")
    finally:
        httpd.server_close()
        logging.info("Server shut down.")


def main():
    """Main entry point for the script."""
    run_server(HOST, PORT, CERTFILE, KEYFILE)


if __name__ == "__main__":
    main()
