#!/usr/bin/env python3
import argparse
import asyncio
import logging

from aioquic.asyncio.client import connect
from aioquic.asyncio import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

# Logging setup
LOG_FILENAME = "/output/server_http3.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class EchoClientProtocol(QuicConnectionProtocol):
    """
    Sends a message on a stream immediately after connection is made,
    then prints the echoed data received from the server.
    """

    def __init__(self, quic, message: str, loop: asyncio.AbstractEventLoop):
        super().__init__(quic)
        self._message = message
        self._loop = loop
        self._stream_id = None

    def connection_made(self, transport):
        """
        Called once the underlying UDP transport is active.
        We can immediately open a stream and send our message.
        """
        super().connection_made(transport)
        # Open the next available stream
        self._stream_id = self._quic.get_next_available_stream_id()
        self._quic.send_stream_data(
            stream_id=self._stream_id,
            data=self._message.encode("utf-8"),
            end_stream=True,
        )
        logging.info(f"Sent message to server: {self._message}")

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            logging.info(f"Received echo: {event.data.decode('utf-8')}")
            # If the server signaled end of stream, close the connection
            if event.end_stream:
                # Schedule closing on the next event loop tick
                self._loop.call_soon(self.close)

    def close(self):
        # Close the QUIC connection
        self._quic.close()
        logging.info("Connection closed")


async def run_client(host, port, message):
    configuration = QuicConfiguration(
        is_client=True,
        alpn_protocols=["hq-29"],  # or "h3"
    )

    # Connect to the QUIC server
    async with connect(
        host=host,
        port=port,
        configuration=configuration,
        server_name=host,  # SNI
        create_protocol=lambda quic: EchoClientProtocol(quic, message, asyncio.get_event_loop()),
    ) as client:
        # Wait for the connection to close (either by server or an error)
        await client.wait_closed()


def main():
    parser = argparse.ArgumentParser(description="QUIC Echo Client")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server hostname or IP")
    parser.add_argument("--port", type=int, default=4433, help="Server port")
    parser.add_argument("--message", type=str, default="Hello QUIC!", help="Message to send")
    args = parser.parse_args()

    asyncio.run(run_client(args.host, args.port, args.message))


if __name__ == "__main__":
    main()
