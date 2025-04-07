import asyncio
import websockets
import logging
import ssl

# Configure logging
LOG_FILENAME = "/output/server_wss.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

PORT = 8101
HOST = "0.0.0.0"
CERTFILE = "/cert/tls/fullchain1.pem"
KEYFILE = "/cert/tls/privkey1.pem"

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

async def echo(websocket):
    async for message in websocket:
        logging.info(f"Received: {message}")
        await websocket.send(f"Echo: {message}")
        logging.info(f"Sent: Echo: {message}")

async def main():
    async with websockets.serve(echo, HOST, PORT, ssl=ssl_context):
        logging.info(f"WebSocket server started on wss://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket server shutting down...")