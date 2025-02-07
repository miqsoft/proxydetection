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
    def __init__(self, quic_connection, host: str, path: str):
        super().__init__(quic_connection)
        self._host = host
        self._path = path
        # Initialize HTTP/3: this will automatically create the client control stream and QPACK streams.
        self._http = H3Connection(self._quic)
        self._stream_id = None

        # Attributes to store response data
        self.response_headers = None
        self.response_body = b""

    def quic_event_received(self, event) -> None:
        # Process QUIC events through the HTTP/3 layer and get HTTP/3 events.
        http_events = self._http.handle_event(event)
        for http_event in http_events:
            print("HTTP event:", http_event)
            if isinstance(http_event, HeadersReceived):
                # Decode headers from bytes to strings.
                self.response_headers = [
                    (name.decode(), value.decode()) for name, value in http_event.headers
                ]
                print("Headers:", self.response_headers)
            elif isinstance(http_event, DataReceived):
                # Append data to the response body.
                self.response_body += http_event.data
                print("Received data chunk:", http_event.data.decode(errors='replace'))
                if http_event.stream_ended:
                    # The stream is finished; print the full response.
                    print("\nFull response body:")
                    print(self.response_body.decode(errors='replace'))
                    # Optionally, close the connection after receiving the full response.
                    self._quic.close(error_code=0, reason_phrase="done")

    def send_request(self, data: bytes = None) -> None:
        # Open a client-initiated bidirectional stream.
        self._stream_id = self._quic.get_next_available_stream_id(is_unidirectional=False)

        headers = [
            (b":method", b"GET"),
            (b":scheme", b"https"),
            (b":authority", self._host.encode()),
            (b":path", self._path.encode()),
            (b"user-agent", b"aioquic-client"),
        ]
        self._http.send_headers(self._stream_id, headers, end_stream=(data is None))
        if data is not None:
            # Send the request data and mark the stream as ended.
            self._http.send_data(self._stream_id, data, end_stream=True)
        self.transmit()

async def http3_request(url: str, msg: bytes = None) -> None:
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or 443
    path = parsed.path or "/"

    # Configure QUIC with HTTP/3 ALPN.
    configuration = QuicConfiguration(is_client=True)
    # Set ALPN to the HTTP/3 values (this ensures the server will negotiate HTTP/3).
    configuration.alpn_protocols = H3_ALPN
    # Optionally disable certificate verification for testing purposes:
    configuration.verify_mode = ssl.CERT_NONE

    async with connect(
        host,
        port,
        configuration=configuration,
        create_protocol=lambda quic_conn, **kwargs: HTTP3Client(quic_conn, host, path)
    ) as client:
        if msg:
            client.send_request(data=msg)
        else:
            client.send_request()
        # Wait long enough to allow the response to arrive.
        await asyncio.sleep(10)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py https://example.com/path")
        sys.exit(1)
    url = sys.argv[1]
    msg = b"X"
    asyncio.run(http3_request(url, msg))
