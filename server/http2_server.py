from quart import Quart
import logging

log_filename = "/vagrant/results/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Quart(__name__)
PORT = 80
HOST = "0.0.0.0"

@app.route('/')
async def home():
    return "Hello, HTTP/2!"


if __name__ == "__main__":
    import asyncio
    from hypercorn.config import Config
    from hypercorn.asyncio import serve

    config = Config()
    config.bind = [f'{HOST}:{PORT}']  # Address and port
    config.alpn_protocols = ["h2"]  # Ensure HTTP/2 support

    asyncio.run(serve(app, config))
