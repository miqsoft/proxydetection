import asyncio
import websockets
import logging

# Configure logging
LOG_FILENAME = "/output/server.log"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

PORT = 8765
HOST = "0.0.0.0"

async def echo(websocket, path):
    async for message in websocket:
        logging.info(f"Received: {message}")
        await websocket.send(f"Echo: {message}")
        logging.info(f"Sent: Echo: {message}")

start_server = websockets.serve(echo, HOST, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
