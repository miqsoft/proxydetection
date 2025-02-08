import socket

HOST = '0.0.0.0'
PORT = 12345

def handle_client(client_socket):
    try:
        client_socket.send(b"Welcome to the Custom TCP Server!\n")
        client_socket.send(b"Available commands: HELLO, ADD, BYE\n")

        while True:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                break

            print(f"Received: {data}")

            # Split the command and argument
            parts = data.split(" ")
            command = parts[0].upper()

            if command == "HELLO" and len(parts) == 2:
                name = parts[1]
                response = f"Hello, {name}!\n"

            elif command == "ADD" and len(parts) == 3:
                try:
                    x = int(parts[1])
                    y = int(parts[2])
                    result = x + y
                    response = f"Result: {result}\n"
                except ValueError:
                    response = "ERROR: ADD requires two numbers.\n"

            elif command == "BYE":
                response = "Goodbye!\n"
                client_socket.send(response.encode('utf-8'))
                break

            else:
                response = "ERROR: Unknown command.\n"

            client_socket.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
