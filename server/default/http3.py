import asyncio
import logging
from pathlib import Path

from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

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

CERTFILE = Path("/cert/cert.pem")
KEYFILE = Path("/cert/key.pem")

class EchoQuicConnectionProtocol(QuicConnectionProtocol):
    """
    Echoes back any data received on a stream.
    """

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            # Echo back the data on the same stream
            self._quic.send_stream_data(
                stream_id=event.stream_id,
                data=event.data,
                end_stream=event.end_stream,
            )


async def run_server(host, port, cert, key):
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=["h3"],  # or "h3" depending on your use
        certificate=cert,
        private_key=key,
    )

    # Start the QUIC server
    await serve(
        host=host,
        port=port,
        configuration=configuration,
        create_protocol=EchoQuicConnectionProtocol,
    )


def main():
    asyncio.run(run_server(HOST, PORT, CERTFILE, KEYFILE))


if __name__ == "__main__":
    main()
