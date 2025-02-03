import logging
from quart import Quart
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Configure logging
LOG_FILENAME = "/vagrant/results/server.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
PORT = 4001
HOST = "0.0.0.0"
CERTFILE = "/vagrant/server/cert/server.pem"  # Path to SSL certificate
KEYFILE = "/vagrant/server/cert/server.pem"  # Path to SSL key

# Create a Quart app
app = Quart(__name__)

@app.route("/")
async def home():
    """Handle requests to the root URL."""
    logging.info("Root endpoint accessed.")
    return "Hello, HTTP/2 with TLS!"


def configure_hypercorn():
    """Configure Hypercorn for HTTP/2 and SSL."""

    config = Config()
    config.bind = [f"{HOST}:{PORT}"]  # Bind to host and port
    config.alpn_protocols = ["h2"]  # Enable HTTP/2
    config.http1 = False  # Disable HTTP/1.1
    config.h2 = True  # Ensure HTTP/2 is enabled
    config.certfile = CERTFILE
    config.keyfile = KEYFILE

    logging.info("Hypercorn configured with SSL and HTTP/2.")
    return config


async def run_server():
    """Run the Quart application with Hypercorn."""

    config = configure_hypercorn()
    try:
        logging.info("Starting HTTPS server on %s:%d", HOST, PORT)
        await serve(app, config)
    except FileNotFoundError as fnf_error:
        logging.error("File not found: %s", fnf_error)
        print(f"Error: {fnf_error}. Check the certificate and key file paths.")
    except PermissionError as perm_error:
        logging.error("Permission error: %s", perm_error)
        print(f"Error: {perm_error}. Try running the script with elevated privileges or change the port to above 1024.")
    except Exception as e:
        logging.error("Server failed with error: %s", e)
        print(f"Server failed with error: {e}")


def main():
    """Main entry point for the script."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
