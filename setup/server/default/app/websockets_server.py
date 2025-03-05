import asyncio
import websockets
import logging

# Configure logging
LOG_FILENAME = "/output/server_ws.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

PORT = 8100
HOST = "0.0.0.0"

async def echo(websocket):
    async for message in websocket:
        logging.info(f"Received: {message}")
        await websocket.send(f"Echo: {message}")
        logging.info(f"Sent: Echo: {message}")

async def main():
    async with websockets.serve(echo, HOST, PORT):
        logging.info(f"WebSocket server started on ws://{HOST}:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("WebSocket server shutting down...")