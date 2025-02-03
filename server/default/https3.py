import asyncio
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived
import logging

# Configure logging
LOG_FILENAME = "/vagrant/results/server.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
HOST = "0.0.0.0"
PORT = 4003
RESPONSE_BODY = "Hello, HTTP3 with TLS!"
CERTFILE = "/vagrant/server/cert/server.pem"  # Path to SSL certificate
KEYFILE = "/vagrant/server/cert/server.pem"  # Path to SSL private key


class Http3ServerProtocol(QuicConnectionProtocol):
    """Custom QUIC protocol for HTTP/3 server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handshake_complete = False

    def quic_event_received(self, event):
        """Handle QUIC events."""
        if isinstance(event, HandshakeCompleted):
            self.handshake_complete = True
            logging.info("Handshake completed with %s", self._quic.peer_address)

        elif isinstance(event, StreamDataReceived):
            stream_id = event.stream_id
            try:
                data = event.data.decode()
                logging.info("Received data on stream %d: %s", stream_id, data)

                if self.handshake_complete:
                    # HTTP/3 response
                    response = (
                        "HTTP/3 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(RESPONSE_BODY)}\r\n\r\n"
                        f"{RESPONSE_BODY}"
                    )
                    self._quic.send_stream_data(stream_id, response.encode(), end_stream=True)
                    logging.info("Sent response on stream %d", stream_id)
            except Exception as e:
                logging.error("Error handling stream %d: %s", stream_id, e)


async def run_server():
    """Start the HTTP/3 server."""
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    logging.info("Starting HTTP/3 server on %s:%d", HOST, PORT)
    await serve(
        (HOST, PORT),
        configuration=configuration,
        create_protocol=Http3ServerProtocol,
    )


def main():
    """Main entry point for the script."""
    try:
        asyncio.run(run_server())
    except FileNotFoundError as fnf_error:
        logging.error("File not found: %s", fnf_error)
        print(f"Error: {fnf_error}. Check the certificate and key file paths.")
    except PermissionError as perm_error:
        logging.error("Permission error: %s", perm_error)
        print(f"Error: {perm_error}. Try running the script with elevated privileges or change the port to above 1024.")
    except Exception as e:
        logging.error("Server failed with error: %s", e)
        print(f"Server failed with error: {e}")


if __name__ == "__main__":
    main()
