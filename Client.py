import socket
import threading
import json
import select
import queue
import traceback
import random
import os
import math

class ChatClient:
    def __init__(self):

        self.server_address = ('localhost', 9799)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.username = None
        self.udp_port = random.randint(8000,15000)
        self.udp_server = socket.socket(/socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_server.bind(('localhost', self.udp_port))
        self.visibility = "y"  # Default visibility is True
        self.MAX_SEGMENT = 500
        self.file_data = {}
        self.messages = queue.Queue()
        self.currentstate = ""

    def receive(self):
        while True:  # Keep receiving messages while the server is running
            try:
                readable, _, _ = select.select([self.udp_server], [], [], 0.1)
                for sock in readable:

                    message, addr = sock.recvfrom(4096)

                    file = message.decode()
                    info = file.split(':')  # Adjusted to split correctly
                    header = info[0]

                    if header == "FILE_INFO":
                        Filename = info[1]
                        data = info[2]
                        file_name = Filename
                        num_segments = int(data)
                        self.file_data[file_name] = {'received_segments': 0, 'num_segments': num_segments, 'data': []}

                    elif header == "SEGMENT":

                        data = data.encode()
                        if file_name in self.file_data:
                            self.file_data[file_name]['data'].append((num_segments, data))
                            self.file_data[file_name]['received_segments'] += 1

                            if self.file_data[file_name]['received_segments'] == self.file_data[file_name]['num_segments']:
                                # Sort segments by their number and concatenate
                                sorted_segments = sorted(self.file_data[file_name]['data'], key=lambda x: x[0])
                                file_content = b''.join(segment[1] for segment in sorted_segments)

                                with open(file_name, 'wb') as file:
                                    file.write(file_content)
                                print(f"File {file_name} received and assembled successfully.")
                                del self.file_data[file_name]
                        else:
                            print("Received segment for unknown file.")

                    elif header != "FILE_INFO" and header != "SEGMENT":
                        self.messages.put((message, addr))
                    else:
                        pass


            except Exception as e:
                traceback.print_exc()

    def broadcast(self):
        while True:  # Keep broadcasting messages while the server is running
            try:
                if not self.messages.empty():

                    message, addr = self.messages.get()
                    message = message.decode()

                    actualMessage = message
                    oldOrNew = actualMessage[:3]

                    if oldOrNew == "New":
                        # Trim "New" out of the message
                        trimmedMessage = actualMessage[3:]
                        username = trimmedMessage[:trimmedMessage.index(":")]

                        if self.currentstate != username:


                            print("New message from " + username)

                            self.messages.put((trimmedMessage.encode(), addr))

                        else:
                            print(f"{trimmedMessage}")

                    else:
                        # If the message doesn't start with "New", just put it back in the queue
                        if self.currentstate == username:

                            print(f"{message}")

                        else:
                            self.messages.put((message.encode(), addr))

            except Exception as e:
                traceback.print_exc()
                print(f"Error broadcasting message: {e}")



    def login(self, username, visibility):
        self.username = username
        self.visibility = visibility
        client_info = json.dumps([self.username, self.udp_port, self.visibility]).encode()
        self.client_socket.send(client_info)

    def send_file(self, file_path, target_addr):
        """
        Send a file through UDP in segments.
        :param file_path: Path to the file to send.
        :param target_addr: Tuple containing the IP address and port of the receiver.
        """
        file_size = os.path.getsize(file_path)
        num_segments = math.ceil(file_size / self.MAX_SEGMENT)  # Calculate the number of segments needed

        # Send file info (e.g., name, number of segments) to receiver
        file_name = os.path.basename(file_path)
        file_info = f"FILE_INFO:{file_name}:{num_segments}"
        self.udp_server.sendto(file_info.encode(), target_addr)

        # Open the file and send it in segments
        with open(file_path, 'rb') as file:
            for segment_num in range(num_segments):
                segment = file.read(self.MAX_SEGMENT)

                # Optionally prepend segment with its number for reassembly
                data = f"SEGMENT:{file_name}:{segment_num}"
                self.udp_server.sendto(data.encode(), target_addr)

                # Implement acknowledgment reception and retransmission logic here, if needed

        print(f"File {file_name} sent in {num_segments} segments.")

    def list_online_users(self):
        self.client_socket.send("/list".encode())
        online_users_data = self.client_socket.recv(2048).decode()
        online_users = json.loads(online_users_data)
        print("Online users:")
        for username, (IP_Adr, UDP_port, visibility) in online_users.items():
            if (self.username != username and visibility):
                print(username)

    def connect_to_user(self, target_username):
        message = f"/connect:{target_username}".encode()
        self.client_socket.send(message)
        target_info_data = self.client_socket.recv(2048).decode()
        if target_info_data != "User not found.":
            target_info = json.loads(target_info_data)
            print(f"Connected to {target_username} - IP: {target_info[0]}, UDP port: {target_info[1]}\nEnter @exit to quit/@file 'filename'.\n")
            self.currentstate = target_username


            while True:
                message = input("You: ")
                if (message == "@exit"):
                    self.currentstate = ""
                    break
                elif (message.startswith("@file")):
                    filename = message.split(" ")[1]
                    self.send_file(filename,(target_info[0], target_info[1]))
                else:
                    message = f"New{self.username}: {message}"  # Include the state in the message
                    self.udp_server.sendto(message.encode(), (target_info[0], target_info[1]))  # Send message with state via UDP

        else:
             print("User not found.")


    def change_visibility(self, visibility):
        self.visibility = visibility
        visibility_command = f"/visibility {self.username} {visibility}"
        self.client_socket.send(visibility_command.encode())

if __name__ == "__main__":
    client = ChatClient()
    print("Connected to server.")

    username = input("Username:\n")
    visiblity = input("Do you want to be visible to other user y/n:\n")

    if visiblity.lower() == "n":
        client.visibility = "n"
    else:
        client.visibility = "y"

    receive_thread = threading.Thread(target=client.receive)
    broadcast_thread = threading.Thread(target=client.broadcast)


    receive_thread.start()
    broadcast_thread.start()

    client.login(username, visiblity)  # Enter your desired username

    while True:
        print("\nAvailable Options:")
        print("1. List online users")
        print("2. Connect to user")
        print("3. Change visibility")
        print("4. Help")
        print("5. Exit")

        option = input("Choose an option:\n")

        if option == "1":
            client.list_online_users()
            continue
        elif option == "2":
            target_username = input("Enter the username to connect to:\n ")
            client.connect_to_user(target_username)
            continue
        elif option == "3":
            visible = input("Enter visibility y/n:\n")
            if visible.lower() == "n":
                    client.change_visibility("n")
            else:
                    client.change_visibility("y")
            continue
        elif option == "4":
            print("\nHelp:")
            print("1. To list online users, simply choose option 1.")
            print("2. To connect to a user, choose option 2 and enter the username of the user you want to connect to.")
            print("3. To change visibility, choose option 6 and enter 'True' or 'False' to set your visibility.")
            print("4. Choose option 5 to exit the application.")
            continue
        elif option == "5":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please choose again.")
            continue
