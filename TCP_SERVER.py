import socket
import threading
import json



class ChatServer:


    def __init__(self):
        self.connected_clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost',9799))
        self.server_socket.listen()
        print("Server is up and running...")

    def handle_client(self, client_socket, address):
        try:
            while True:
                message = client_socket.recv(2048).decode()


                if not message:
                    break  # Client has disconnected, break out of the loop

                elif message == '/list':

                    self.send_online_users(client_socket)
                    continue

                elif message.startswith("/visibility"):
                    _, username, new_visibility = message.split(maxsplit=2)
                    # Update the client's visibility in the server's records
                    print("update recieved")
                    if username in self.connected_clients:
                        IP_address, UDP_port, _ = self.connected_clients[username]
                        self.connected_clients[username] = (IP_address, UDP_port, new_visibility)
                        print("update processed")

                elif message.startswith("/connect"):
                    target_user = message.split(':')[1]
                    self.connect_to_user(client_socket, target_user)
                    continue

                else:
                    if not message.strip():
                     continue
                    else:
                        client_info = json.loads(message)
                        username = client_info[0]
                        UDP_port = client_info[1]
                        visibility = client_info[2]
                        IP_address = address[0]
                        self.connected_clients[username] = (IP_address, UDP_port, visibility)

        except Exception as e:
            if username and username in self.connected_clients:
                del self.connected_clients[username]
            print(f"Error or disconnection, removed client {username}.")

    def send_online_users(self, client_socket):
        visible_users = {username: data for username, data in self.connected_clients.items() if data[2] == "y"}  # Filter by visibility "y"
        encoded_data = json.dumps(visible_users).encode()
        client_socket.send(encoded_data)

    def connect_to_user(self, client_socket, target_user):
        if target_user in self.connected_clients:
            target_info = self.connected_clients[target_user]
            # Send both the client's and target user's information to each other
            client_socket.send(json.dumps(target_info).encode())
            # Use the target user's socket object as the key to access its information
        else:
            client_socket.send("User not found.".encode())

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_handler.start()


if __name__ == "__main__":
    server = ChatServer()
    server.start()
