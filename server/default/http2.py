from quart import Quart
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import logging

LOG_FILENAME = "/output/server_http2.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
PORT = 8001
HOST = "0.0.0.0"
RESPONSE="Hello, HTTP2!"

app = Quart(__name__)

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
