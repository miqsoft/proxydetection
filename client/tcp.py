import socket
import time

def connect_via_http_proxy(proxy_host, proxy_port, server_host, server_port):
    try:
        # Create a raw socket
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the HTTP proxy
        print(f"Connecting to HTTP proxy {proxy_host}:{proxy_port}...")
        client.connect((proxy_host, proxy_port))

        # Send the HTTP CONNECT request
        connect_request = f"CONNECT {server_host}:{server_port} HTTP/1.1\r\n"
        connect_request += f"Host: {server_host}:{server_port}\r\n"
        connect_request += "Connection: keep-alive\r\n\r\n"
        client.sendall(connect_request.encode('utf-8'))

        # Read the response
        response = client.recv(1024).decode('utf-8')
        print(f"Proxy response: {response}")

        # Check if the connection is established
        if "200 Connection established" not in response:
            print("Failed to establish connection through the proxy.")
            client.close()
            return

        print(f"Connected to {server_host}:{server_port} through proxy {proxy_host}:{proxy_port}")

        # Receive the response from the server
        server_response = client.recv(1024).decode('utf-8')
        print(f"Server response: {server_response.strip()}")

        # Send the HELLO command
        name = "Alice"
        command = f"HELLO {name}\n"
        print(f"Sending: {command.strip()}")
        client.send(command.encode('utf-8'))

        # Receive the response from the server
        server_response = client.recv(1024).decode('utf-8')
        print(f"Server response: {server_response.strip()}")

        time.sleep(1)
        # Close the connection
        client.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Proxy and server details
    proxy_ip = "192.168.56.5"
    proxy_port = 3128
    server_ip = "192.168.56.6"
    server_port = 12345

    # Connect via proxy
    connect_via_http_proxy(proxy_ip, proxy_port, server_ip, server_port)
