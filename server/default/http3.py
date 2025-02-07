import asyncio
import logging
from pathlib import Path

from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection, H3_ALPN
from aioquic.h3.events import DataReceived, HeadersReceived, H3Event

# Logging setup
LOG_FILENAME = "/output/server_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
PORT = 8002
HOST = "0.0.0.0"
RESPONSE_BODY = "Hello, HTTP3!"

CERTFILE = Path("/cert/server.pem")
KEYFILE = Path("/cert/server.pem")


class Http3ServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create an HTTP/3 connection to manage HTTP/3 frames.
        self._http = H3Connection(self._quic)

    def quic_event_received(self, event):
        # Feed the event into the HTTP/3 connection.
        http_events = self._http.handle_event(event)
        for http_event in http_events:
            if isinstance(http_event, HeadersReceived):
                stream_id = http_event.stream_id
                headers = [(name.decode(), value.decode()) for name, value in http_event.headers]
                logging.info("Received headers on stream %d: %s", stream_id, headers)
                # Prepare an HTTP/3 response.
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
                # For simplicity, we ignore request body data in this example.
                if http_event.stream_ended:
                    # Send the response body.
                    self._http.send_data(stream_id, RESPONSE_BODY.encode(), end_stream=True)
                    logging.info("Sent response on stream %d", stream_id)
        # Transmit any pending data.
        self.transmit()


async def main():
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=H3_ALPN,  # Ensure HTTP/3 ALPN is set
    )
    try:
        configuration.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)
    except FileNotFoundError:
        logging.error("Certificate or key file not found. Ensure the cert files exist.")
        return

    logging.info("Starting HTTP/3 server on %s:%d", HOST, PORT)

    await serve(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=Http3ServerProtocol,
    )

if __name__ == "__main__":
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped.")
    except Exception as e:
        logging.error("Unexpected error: %s", e)
