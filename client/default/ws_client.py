import asyncio
import websockets
import sys
import ssl

async def connect(server_url, ssl_context):
    async with websockets.connect(server_url, ssl=ssl_context) as websocket:
        await websocket.send("Hello, Server!")
        response = await websocket.recv()
        print(f"Server response: {response}")

if __name__ == "__main__":
    uri = sys.argv[1]
    tls = sys.argv[2].lower() == "true"  # Convert to boolean

    if tls:
        url = f"wss://{uri}"
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Disable certificate validation
    else:
        url = f"ws://{uri}"
        ssl_context = None  # No SSL context for ws://

    asyncio.run(connect(url, ssl_context))