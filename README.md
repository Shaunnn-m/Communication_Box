Python Chat Application
This Python chat application provides a basic framework for a chat system using TCP sockets. It consists of two main components: the ChatClient and the ChatServer.

Files Description
Client.py: Implements the client-side logic of the chat application. It is responsible for establishing a connection to the chat server, handling user input, and receiving messages from the server. The client uses TCP sockets for communication and includes features such as setting up a username and supporting UDP for certain operations.

TCP_SERVER.py: Implements the server-side logic of the chat application. It handles incoming connections from clients, manages client messages, and broadcasts messages to all connected clients. The server is designed to support multiple client connections simultaneously and uses TCP sockets for communication.

Requirements
Python 3.x
Standard Python libraries: socket, threading, json, select, queue, traceback, random, os, math
Setup and Execution
Server Setup: Run the TCP_SERVER.py script on the host machine to start the chat server. Ensure the server is running before clients attempt to connect.

python3 TCP_SERVER.py
Client Connection: Run the Client.py script from the client machine to connect to the chat server. The client will prompt for a username or other necessary inputs to join the chat.

Copy code
python3 Client.py
Features
TCP-based Communication: Utilizes TCP sockets for reliable data transmission between the client and server.
Concurrent Client Handling: The server can handle multiple clients simultaneously, thanks to threading.
Dynamic UDP Port Allocation: The client dynamically chooses a UDP port for certain operations (if applicable based on the full code review).
Message Broadcasting: The server can broadcast messages to all connected clients, enabling real-time chat functionality.
Note
This README provides a basic overview of the application. For detailed implementation and customization, refer to the comments and documentation within the Client.py and TCP_SERVER.py scripts.
