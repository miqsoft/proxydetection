import argparse
import asyncio
import logging
import time
from email.utils import formatdate

from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import H3Event, HeadersReceived, DataReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, ProtocolNegotiated

LOG_FILENAME = "/output/server_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SERVER_NAME = "aioquic/" + "version"  # Replace "version" with aioquic.__version__ if desired.

class HttpServerProtocol(QuicConnectionProtocol):
    """
    A minimal HTTP/3 server protocol that responds to requests with a simple message.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None  # Will be set once ALPN negotiation completes.

    def quic_event_received(self, event: QuicEvent) -> None:
        # Once protocol negotiation is done, initialize the HTTP/3 layer.
        if isinstance(event, ProtocolNegotiated):
            if event.alpn_protocol in H3_ALPN:
                self._http = H3Connection(self._quic)
        if self._http is None:
            return

        # Pass the QUIC event to the HTTP/3 layer and handle resulting HTTP events.
        for http_event in self._http.handle_event(event):
            self.http_event_received(http_event)

    def http_event_received(self, event: H3Event) -> None:
        if isinstance(event, HeadersReceived):
            # (Optional) Extract method and path for logging.
            method = None
            path = None
            for name, value in event.headers:
                if name == b":method":
                    method = value.decode()
                elif name == b":path":
                    path = value.decode()
            logger.info("Received HTTP request: %s %s", method, path)

            # Respond with a simple text message.
            response_body = b"Hello, World!"
            self._http.send_headers(
                stream_id=event.stream_id,
                headers=[
                    (b":status", b"200"),
                    (b"server", SERVER_NAME.encode()),
                    (b"date", formatdate(time.time(), usegmt=True).encode()),
                    (b"content-type", b"text/plain"),
                ],
            )
            self._http.send_data(
                stream_id=event.stream_id,
                data=response_body,
                end_stream=True,
            )
            logger.info(f'Sent response: {response_body.decode()}')
            self.transmit()

        elif isinstance(event, DataReceived):
            # (Optional) Handle request body data if needed.
            pass

async def main(host: str, port: int, configuration: QuicConfiguration) -> None:
    # Start the server and wait indefinitely.
    await serve(
        host,
        port,
        configuration=configuration,
        create_protocol=HttpServerProtocol,
    )
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Simple HTTP/3 Server")
    parser.add_argument(
        "--host",
        type=str,
        default="::",
        help="Listen on the specified address (default: ::)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4433,
        help="Listen on the specified port (default: 4433)",
    )
    parser.add_argument(
        "--certificate",
        type=str,
        required=True,
        help="Path to the TLS certificate file (PEM format)",
    )
    parser.add_argument(
        "--private-key",
        type=str,
        required=True,
        help="Path to the TLS private key file (PEM format)",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Create the QUIC configuration with HTTP/3 ALPN.
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=H3_ALPN,
    )
    configuration.max_datagram_frame_size = 1500
    configuration.load_cert_chain(args.certificate, args.private_key)

    asyncio.run(main(args.host, args.port, configuration))
