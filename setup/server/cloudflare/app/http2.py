from quart import Quart, request
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import logging

LOG_FILENAME = "/output/server_http2.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

PORT = 8080
HOST = "0.0.0.0"
RESPONSE="Hello, HTTP2!"

app = Quart(__name__)

# Middleware to log requests and responses
@app.before_request
async def log_request():
    """Log details of incoming requests."""
    logging.info(f"Received request: {request.method} {request.path}")
    if request.args:
        logging.info(f"Query Params: {request.args}")
    if request.content_length:
        data = await request.get_data()
        logging.info(f"Request Body: {data.decode('utf-8', errors='ignore')}")

@app.after_request
async def log_response(response):
    """Log details of outgoing responses."""
    logging.info(f"Response Status: {response.status}")
    return response

@app.route('/')
async def home():
    return RESPONSE


if __name__ == "__main__":
    config = Config()
    config.bind = [f'{HOST}:{PORT}']  # Address and port
    config.alpn_protocols = ["h2"]  # Ensure HTTP/2 support

    # Disallow fallback to HTTP/1.1 by omitting it in alpn_protocols
    config.http1 = False  # Explicitly disable HTTP/1.1 support
    config.h2 = True  # Ensure HTTP/2 is enabled

    asyncio.run(serve(app, config))