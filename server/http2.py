from quart import Quart
import logging

log_filename = "/vagrant/results/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
PORT = 80
HOST = "0.0.0.0"
RESPONSE="Hello, HTTP2!"

app = Quart(__name__)

@app.route('/')
async def home():
    return RESPONSE


if __name__ == "__main__":
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = [f'{HOST}:{PORT}']  # Address and port
    config.alpn_protocols = ["h2"]  # Ensure HTTP/2 support

    # Disallow fallback to HTTP/1.1 by omitting it in alpn_protocols
    config.http1 = False  # Explicitly disable HTTP/1.1 support
    config.h2 = True  # Ensure HTTP/2 is enabled

    asyncio.run(serve(app, config))
