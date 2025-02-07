import asyncio
import logging
from pathlib import Path
import sys

from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection, H3_ALPN
from aioquic.h3.events import DataReceived, HeadersReceived, H3Event

# Logging setup
LOG_FILENAME = "/output/server_http3.log"
LOG_FILENAME = "../server_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
PORT = 8002
HOST = "0.0.0.0"
RESPONSE_BODY = "Hello, HTTP3!"

CERTFILE = Path("/cert/cert.pem")
KEYFILE = Path("/cert/key.pem")
CERTFILE = Path("../../cert/cert.pem")
KEYFILE = Path("../../cert/key.pem")


class Http3ServerProtocol(QuicConnectionProtocol):
    """
    Simple HTTP/3 server protocol that returns a plain text response
    to all GET requests.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = H3Connection(self._quic)

    def quic_event_received(self, event):
        """Handle QUIC events and process any HTTP/3 frames."""
        http_events = self._http.handle_event(event)
        for http_event in http_events:
            if isinstance(http_event, HeadersReceived):
                stream_id = http_event.stream_id
                headers = [(name.decode(), value.decode()) for name, value in http_event.headers]
                logging.info("Received headers on stream %d: %s", stream_id, headers)

                # Send HTTP/3 response headers
                response_headers = [
                    (b":status", b"200"),
                    (b"content-type", b"text/plain"),
                    (b"content-length", str(len(RESPONSE_BODY)).encode()),
                ]
                self._http.send_headers(stream_id, response_headers)
            elif isinstance(http_event, DataReceived):
                stream_id = http_event.stream_id
                data = http_event.data.decode(errors="replace")
                logging.info("Received data on stream %d: %s", stream_id, data)

                if http_event.stream_ended:
                    # Send the response body and end stream
                    self._http.send_data(stream_id, RESPONSE_BODY.encode(), end_stream=True)
                    logging.info("Sent response on stream %d", stream_id)

        # Transmit any pending packets
        self.transmit()


async def start_server():
    """Asynchronously start the HTTP/3 server on the specified HOST and PORT."""
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=H3_ALPN,
    )

    try:
        configuration.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)
    except FileNotFoundError:
        logging.error("Certificate or key file not found. Make sure cert.pem and key.pem exist.")
        return

    logging.info("Starting HTTP/3 server on %s:%d", HOST, PORT)
    print(f"Starting HTTP/3 server on {HOST}:{PORT}...")

    # Start serving
    await serve(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=Http3ServerProtocol,
    )


def run_server():
    """Run the server with a proper event loop to support Windows and Unix."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_server())
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped via KeyboardInterrupt.")
        print("Server stopped.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    run_server()
