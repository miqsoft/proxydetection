import asyncio
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived

import logging

# Logging setup
log_filename = "/vagrant/results/server.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
PORT = 8080  # Changed to avoid privilege issues
HOST = "0.0.0.0"
RESPONSE_BODY = "Hello, HTTP3!"
RESPONSE = (
    "HTTP/3 200 OK\r\n"
    "Content-Type: text/plain\r\n"
    f"Content-Length: {len(RESPONSE_BODY)}\r\n\r\n"
    f"{RESPONSE_BODY}"
)


class Http3ServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handshake_complete = False

    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            self.handshake_complete = True
            logging.info("Handshake completed with %s", self._quic.peer_address)

        elif isinstance(event, StreamDataReceived):
            stream_id = event.stream_id
            try:
                data = event.data.decode()
                logging.info("Received data on stream %d: %s", stream_id, data)

                if self.handshake_complete:
                    # Respond with a simple HTTP/3 response
                    self._quic.send_stream_data(
                        stream_id, RESPONSE.encode(), end_stream=True
                    )
                    logging.info("Sent response on stream %d", stream_id)
            except Exception as e:
                logging.error("Error handling stream %d: %s", stream_id, e)


async def main():
    configuration = QuicConfiguration(is_client=False)

    logging.info("Starting HTTP/3 server on %s:%d", HOST, PORT)
    await serve(
        (HOST, PORT),
        configuration=configuration,
        create_protocol=Http3ServerProtocol,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped.")
