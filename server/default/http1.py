from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

log_filename = "/output/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
RESPONSE="Hello, HTTP1!"
HOST = "0.0.0.0"
PORT = 80

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set HTTP status code
        self.send_response(200)
        # Set headers
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Write a simple response
        self.wfile.write(RESPONSE.encode())

    def log_message(self, format, *args):
        # Optional: Log requests to stdout
        print(f"{self.address_string()} - {format % args}")



if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), CustomHandler)
    server.serve_forever()
