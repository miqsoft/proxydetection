import asyncio
import logging
from pathlib import Path

from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.h3.connection import H3Connection, H3_ALPN
from aioquic.h3.events import H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ProtocolNegotiated, QuicEvent

LOG_FILENAME = "/output/server_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

# Server configuration
HOST = "0.0.0.0"
PORT = 8002
CERTFILE = Path("/cert/cert.pem")
KEYFILE = Path("/cert/key.pem")


class HttpServerProtocol(QuicConnectionProtocol):
    """
    A very basic HTTP/3 protocol that replies to all requests with a plain text message.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = None  # Will hold the H3Connection once ALPN negotiation succeeds

    def quic_event_received(self, event: QuicEvent):
        log.debug(f"Received QUIC event: {event}")
        if isinstance(event, ProtocolNegotiated):
            self._http = H3Connection(self._quic)

        if self._http is None:
            return

        # Let the H3Connection convert QUIC events to HTTP/3 events.
        for http_event in self._http.handle_event(event):
            self.handle_http_event(http_event)

    def handle_http_event(self, event: H3Event):
        log.debug(f"Received HTTP/3 event: {event}")
        if isinstance(event, HeadersReceived):
            stream_id = event.stream_id
            headers = [
                (b":status", b"200"),
                (b"content-type", b"text/plain"),
            ]
            log.debug(f"sending response headers: {headers}")
            self._http.send_headers(stream_id=stream_id, headers=headers)
            self._http.send_data(
                stream_id=stream_id, data=b"Hello, HTTP3!", end_stream=True
            )
            self.transmit()
            log.debug(f"response sent on stream {stream_id}")


async def main():
    # Create and configure the QUIC configuration.
    configuration = QuicConfiguration(is_client=False)
    configuration.alpn_protocols = H3_ALPN  # Enable HTTP/3 ALPNs
    configuration.load_cert_chain(CERTFILE, KEYFILE)

    # Start the server. The serve() call returns after binding, so we wait forever.
    await serve(
        HOST,
        PORT,
        configuration=configuration,
        create_protocol=HttpServerProtocol,
    )
    await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
