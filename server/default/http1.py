from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

LOG_FILENAME = "../server_http1.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
RESPONSE="Hello, HTTP1.1!"
HOST = "0.0.0.0"
PORT = 8000

class CustomHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # 🔥 Use HTTP/1.1

    def do_GET(self):
        response_body = RESPONSE.encode()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(response_body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")




if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), CustomHandler)
    server.serve_forever()
