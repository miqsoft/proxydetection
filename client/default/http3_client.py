import asyncio
import sys
import ssl
from urllib.parse import urlparse

from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection, H3_ALPN
from aioquic.h3.events import DataReceived, HeadersReceived


class HTTP3Client(QuicConnectionProtocol):
    """
    HTTP/3 client that sends a GET request and prints any response headers and body.
    """
    def __init__(self, quic_connection, host: str, path: str):
        super().__init__(quic_connection)
        self._host = host
        self._path = path
        self._http = H3Connection(self._quic)
        self._stream_id = None
        self.response_headers = None
        self.response_body = b""

    def quic_event_received(self, event) -> None:
        """Process incoming QUIC events and route HTTP/3 frames."""
        http_events = self._http.handle_event(event)
        for http_event in http_events:
            if isinstance(http_event, HeadersReceived):
                # Store or print received headers
                self.response_headers = [
                    (name.decode(), value.decode()) for name, value in http_event.headers
                ]
                print("Received Headers:", self.response_headers)

            elif isinstance(http_event, DataReceived):
                self.response_body += http_event.data
                print("Received Data Chunk:", http_event.data.decode(errors='replace'))

                if http_event.stream_ended:
                    print("\nFull Response Body:")
                    print(self.response_body.decode(errors='replace'))
                    # Close the connection once we've received the full response
                    self._quic.close(error_code=0, reason_phrase="done")

    def send_request(self, data: bytes = None) -> None:
        """Send an HTTP/3 GET request (optionally with a body)."""
        if self._stream_id is None:
            # Reserve a bidirectional stream
            self._stream_id = self._quic.get_next_available_stream_id(is_unidirectional=False)

        headers = [
            (b":method", b"GET"),
            (b":scheme", b"https"),
            (b":authority", self._host.encode()),
            (b":path", self._path.encode()),
            (b"user-agent", b"aioquic-client"),
        ]
        # Send request headers
        self._http.send_headers(self._stream_id, headers, end_stream=(data is None))

        # If there's body data, send it and end the stream
        if data:
            self._http.send_data(self._stream_id, data, end_stream=True)

        # Actually send the QUIC packets
        self.transmit()


async def http3_request(url: str, msg: bytes = None):
    """Perform an HTTP/3 GET request to the given URL, optionally with a body."""
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 443
    path = parsed.path or "/"

    configuration = QuicConfiguration(is_client=True)
    # Use HTTP/3 ALPN
    configuration.alpn_protocols = H3_ALPN
    # For testing with self-signed certs, disable verification
    configuration.verify_mode = ssl.CERT_NONE

    try:
        print(f"Connecting to {host}:{port} via QUIC...")
        async with connect(
            host,
            port,
            configuration=configuration,
            create_protocol=lambda quic_conn, **kwargs: HTTP3Client(quic_conn, host, path)
        ) as client:
            client.send_request(data=msg)

            # Give some time for the response to come back
            # You might want to monitor events more robustly in a real app
            await asyncio.sleep(5)
    except ConnectionError as e:
        print(f"❌ QUIC Connection failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def run_client(url: str, msg: bytes = None):
    """Run the client in an event loop that works for Windows and Unix."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(http3_request(url, msg))
    except KeyboardInterrupt:
        print("\nClient interrupted.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py https://localhost:8002")
        sys.exit(1)

    url = sys.argv[1]
    # Optional body data
    msg = b"X"
    run_client(url, msg)
