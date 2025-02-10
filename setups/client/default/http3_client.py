import argparse
import asyncio
import logging
import ssl
import time
from collections import deque
from urllib.parse import urlparse
from typing import Deque, Optional, Dict

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3Connection, H3_ALPN, ErrorCode
from aioquic.h3.events import DataReceived, H3Event
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent


LOG_FILENAME = "/output/client_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Simple URL helper class.
class URL:
    def __init__(self, url: str) -> None:
        parsed = urlparse(url)
        self.scheme = parsed.scheme
        self.authority = parsed.netloc
        # Default to "/" if no path is provided; include query if present.
        self.full_path = parsed.path or "/"
        if parsed.query:
            self.full_path += f"?{parsed.query}"

# Container for HTTP request information.
class HttpRequest:
    def __init__(
        self,
        method: str,
        url: URL,
        content: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.method = method
        self.url = url
        self.content = content
        self.headers = headers or {}

USER_AGENT = "aioquic/" + "version"  # Replace "version" with aioquic.__version__ if desired.

class HttpClient(QuicConnectionProtocol):
    """
    A minimal HTTP/3 client that supports issuing a request and collecting the response.
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Always use the HTTP/3 layer.
        self._http = H3Connection(self._quic)
        # Dictionaries to track events per stream.
        self._request_events: Dict[int, deque] = {}
        self._request_waiter: Dict[int, asyncio.Future] = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        # Pass incoming QUIC events to the HTTP/3 layer.
        if self._http is not None:
            for http_event in self._http.handle_event(event):
                self.http_event_received(http_event)

    def http_event_received(self, event: H3Event) -> None:
        stream_id = event.stream_id
        if stream_id in self._request_events:
            self._request_events[stream_id].append(event)
            # Once the stream ends, resolve the future.
            if event.stream_ended:
                waiter = self._request_waiter.pop(stream_id)
                waiter.set_result(self._request_events.pop(stream_id))

    async def request(self, request: HttpRequest) -> Deque[H3Event]:
        """
        Sends the HTTP request and waits for the response events.
        """
        stream_id = self._quic.get_next_available_stream_id()

        # Build the mandatory HTTP/3 headers.
        headers = [
            (b":method", request.method.encode()),
            (b":scheme", request.url.scheme.encode()),
            (b":authority", request.url.authority.encode()),
            (b":path", request.url.full_path.encode()),
            (b"user-agent", USER_AGENT.encode()),
        ]
        # Append any additional headers.
        headers.extend((k.encode(), v.encode()) for k, v in request.headers.items())
        self._http.send_headers(
            stream_id=stream_id,
            headers=headers,
            end_stream=not request.content,
        )
        if request.content:
            self._http.send_data(
                stream_id=stream_id,
                data=request.content,
                end_stream=True,
            )

        # Create a future and record events for this stream.
        loop = asyncio.get_event_loop()
        waiter = loop.create_future()
        self._request_events[stream_id] = deque()
        self._request_waiter[stream_id] = waiter

        self.transmit()  # Ensure data is sent.
        return await asyncio.shield(waiter)

async def main(args):
    # Use the provided host and port.
    host = args.host
    port = args.port

    # Build a QUIC configuration with HTTP/3 ALPN.
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=H3_ALPN,
    )
    configuration.max_datagram_frame_size = 1500
    # Load the server certificate PEM for verifying the server.
    #configuration.load_verify_locations(args.server_cert)
    # disable certificate verification
    configuration.verify_mode = ssl.CERT_NONE

    # Compose a URL to request (for example, GET /).
    url_str = f"https://{host}/"
    url = URL(url_str)

    async with connect(
            host,
            port,
            configuration=configuration,
            create_protocol=HttpClient,
        ) as client:
        client: HttpClient

        # Build and send a GET request.
        request = HttpRequest(method="GET", url=url)
        print(f"Request: {request.method} {request.url.full_path}")
        start = time.time()
        events = await client.request(request)
        elapsed = time.time() - start

        total_bytes = sum(
            len(event.data)
            for event in events
            if isinstance(event, DataReceived)
        )
        data = b"".join(event.data for event in events if isinstance(event, DataReceived))
        print(f'Response: {data.decode()}')
        logger.info("Response received: %d bytes in %.3f seconds", total_bytes, elapsed)

        # Close the connection.
        client.close(error_code=ErrorCode.H3_NO_ERROR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Simple HTTP/3 Client")
    parser.add_argument(
        "--host", type=str, required=True, help="Server hostname to connect to"
    )
    parser.add_argument(
        "--port", type=int, default=443, help="Server port (default: 443)"
    )
    parser.add_argument(
        "--server_cert",
        type=str,
        required=True,
        help="Path to the server certificate PEM file",
    )
    args = parser.parse_args()
    asyncio.run(main(args))
