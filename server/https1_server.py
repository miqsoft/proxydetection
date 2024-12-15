import http.server
import ssl
import logging

# Configure logging
log_filename = "/vagrant/results/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

RESPONSE_BODY = b"<html><body><h1>200 OK</h1><p>Custom HTTP Server Response</p></body></html>"

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(RESPONSE_BODY)

# Server address and port
server_address = ('0.0.0.0', 443)

try:
    # Create an HTTP server
    httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)
    logging.info("Server created successfully on %s:%s", *server_address)

    # Create an SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile="/vagrant/server/cert/server.pem",  # Path to your certificate file
        keyfile="/vagrant/server/cert/server.pem"   # Path to your key file
    )

    # Wrap the server socket with SSL
    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    logging.info("SSL setup completed successfully")
    print(f"Serving on https://{server_address[0]}:{server_address[1]}")
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
