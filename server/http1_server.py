from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

log_filename = "/vagrant/results/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set HTTP status code
        self.send_response(200)
        # Set headers
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Write a simple response
        self.wfile.write(b"<html><body><h1>200 OK</h1><p>Custom HTTP Server Response</p></body></html>")

    def log_message(self, format, *args):
        # Optional: Log requests to stdout
        print(f"{self.address_string()} - {format % args}")


# Server setup
host = "0.0.0.0"
port = 80

if __name__ == "__main__":
    server = HTTPServer((host, port), CustomHandler)
    print(f"Starting server on {host}:{port}")
    server.serve_forever()
