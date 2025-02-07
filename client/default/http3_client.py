import asyncio
import logging
import ssl
import sys

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection, H3_ALPN
from aioquic.h3.events import H3Event, HeadersReceived, DataReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ProtocolNegotiated, QuicEvent

LOG_FILENAME = "/output/client_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class SimpleHttpClientProtocol(QuicConnectionProtocol):
    """
    A minimal QUIC client protocol that upgrades to HTTP/3.
    It sends a GET request and gathers the response.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None  # Will be assigned an H3Connection after negotiation.
        self.response_headers = None
        self.response_data = b""
        self._response_received = asyncio.Event()

    def quic_event_received(self, event: QuicEvent):
        # When the protocol is negotiated, initialize the HTTP/3 layer.
        if isinstance(event, ProtocolNegotiated):
            self._http = H3Connection(self._quic)

        if self._http is None:
            return

        # Let H3Connection process QUIC events into HTTP/3 events.
        for http_event in self._http.handle_event(event):
            self.handle_http_event(http_event)

    def handle_http_event(self, event: H3Event):
        if isinstance(event, HeadersReceived):
            logging.info("Received headers: %s", event.headers)
            self.response_headers = event.headers
        elif isinstance(event, DataReceived):
            self.response_data += event.data
            if event.stream_ended:
                self._response_received.set()

    async def wait_for_response(self):
        await self._response_received.wait()


async def main(host: str, port: int):
    # Configure QUIC for the client.
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE  # Do not validate the server certificate.
    configuration.alpn_protocols = H3_ALPN

    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=SimpleHttpClientProtocol,
    ) as client:
        protocol: SimpleHttpClientProtocol = client

        # Build a simple GET request.
        stream_id = protocol._quic.get_next_available_stream_id()
        headers = [
            (b":method", b"GET"),
            (b":scheme", b"https"),
            (b":authority", host.encode()),
            (b":path", b"/"),
        ]
        protocol._http.send_headers(stream_id, headers)
        protocol._http.send_data(stream_id, b"", end_stream=True)
        protocol.transmit()

        # Wait for the full response to be received.
        await protocol.wait_for_response()

        logging.info("Response headers: %s", protocol.response_headers)
        logging.info("Response data: %s", protocol.response_data.decode())


if __name__ == "__main__":
    # Default values for host and port can be overridden via command-line:
    #   python client.py 127.0.0.1 8002
    HOST = "0.0.0.0"
    PORT = 8002

    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])

    asyncio.run(main(HOST, PORT))
