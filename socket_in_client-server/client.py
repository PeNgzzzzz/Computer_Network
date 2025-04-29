from socket import *
import sys
import os
import pickle
from dataclasses import dataclass

CHUNK_SIZE = 1024

# A Request contains information clients should send to server
@dataclass
class Request:
    cmd: str
    filename: str
    r_port: int
    
if __name__ == "__main__":
    # Make sure the number of parameters is correct
    argc = len(sys.argv)
    if argc != 5:
        print("Incorrect number of parameters: ")
        print("Please give four parameters <server_address>, <n_port>, <command>, <filename>.")
        exit(-1)
        
    # Retrieve parameters and error checking
    server_address = sys.argv[1]
    try:
        n_port = int(sys.argv[2])
    except ValueError:
        print('n_port should be an integer!')
        exit(-1)
    command = sys.argv[3]
    filename = sys.argv[4]
    
    if command == "GET":
        ### Negotiation Stage
        # Create sockets
        clientUDPSocket = socket(AF_INET, SOCK_DGRAM)
        clientTCPSocket = socket(AF_INET, SOCK_STREAM)
        clientTCPSocket.bind(('', 0))
        # Get the port number on which the client is expecting the file
        _, r_port = clientTCPSocket.getsockname()
        clientTCPSocket.listen(5)
        # Make a request
        request = Request(command, filename, r_port)
        # Pickle the request
        request = pickle.dumps(request)
        # Send to server
        clientUDPSocket.sendto(request, (server_address, n_port))
        # Get response
        response, _ = clientUDPSocket.recvfrom(CHUNK_SIZE)
        response = response.decode()
        # If the file is not found
        if response == "404 Not Found":
            print(f"{filename} is not found")
            exit(-1)
            
        ### Transaction Stage
        # Wait for the connection from server to transfer file
        transmissionSocket, _ = clientTCPSocket.accept()
        # Open the file
        content = open(filename, 'wb')
        while True:
            # Get a chunk from server
            chunk = transmissionSocket.recv(CHUNK_SIZE)
            # No more chunk to write
            if not chunk:
                break
            # Write to the file
            content.write(chunk)
        # Close file and sockets
        content.close()
        clientUDPSocket.close()
        clientTCPSocket.close()
    elif command == "PUT":
        ### Negotiation Stage
        # Create UDP socket
        clientUDPSocket = socket(AF_INET, SOCK_DGRAM)
        # Make a request
        request = Request("PUT", filename, -1)
        # Pickle the request
        request = pickle.dumps(request)
        # Send to server
        clientUDPSocket.sendto(request, (server_address, n_port))
        # Get response
        response, _ = clientUDPSocket.recvfrom(CHUNK_SIZE)
        response = response.decode()
        # r_port must be an integer
        try:
            r_port = int(response)
        except ValueError:
            print('r_port should be an integer!')
            exit(-1)
            
        ### Transaction Stage
        # Create TCP Socket
        clientTCPSocket = socket(AF_INET, SOCK_STREAM)
        # Connect to the server
        clientTCPSocket.connect((server_address, r_port))
        # If the file to update is not found
        if not os.path.isfile(filename):
            print(f"{filename} is not found")
            exit(-1)
        # Open the file
        content = open(filename, 'rb')
        while True:
            # Read a chunk from the file
            chunk = content.read(CHUNK_SIZE)
            # No more chunk to read
            if not chunk:
                break
            # Send chunk to server
            clientTCPSocket.sendall(chunk)
        # Close file and sockets
        content.close()
        clientUDPSocket.close()
        clientTCPSocket.close()
    else:
        # Invalid command
        print(f"<command> {command} is not valid")
        exit(-1)
        