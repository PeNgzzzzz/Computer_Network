from socket import *
import sys
import os
import pickle
from client import Request

CHUNK_SIZE = 1024

if __name__ == "__main__":
    # Make sure the number of parameters is correct
    argc = len(sys.argv)
    if (argc != 2):
        print("Incorrect number of parameters: ")
        print("Please give only one parameter <storage_directory>.")
        exit(-1)
    
    # Retrieve parameter and error checking
    dir = sys.argv[1]
    if not os.path.isdir(dir):
        print(f"<storage_directory> {dir} does not exist")
        exit(-1)
    
    ### Negotiation Stage
    # Create UDP socket
    serverUDPSocket = socket(AF_INET, SOCK_DGRAM)
    serverUDPSocket.bind(('', 0))
    # Get negotiation port of the server
    _, n_port = serverUDPSocket.getsockname()
    print(f"SERVER_PORT={n_port}")
    while True:
        # Get request and address from clients
        request, clientAddress = serverUDPSocket.recvfrom(CHUNK_SIZE)
        # Unpickle the request
        request = pickle.loads(request)
        if request.cmd == "GET":
            # Get the file from storage_directory
            file = os.path.join(dir, request.filename)
            # If the file is not found
            if not os.path.isfile(file):
                # Send 404 to the client
                serverUDPSocket.sendto('404 Not Found'.encode(), clientAddress)
                continue
            # Extract the r_port of the client
            r_port = request.r_port
            # Send 200 to the client
            serverUDPSocket.sendto('200 OK'.encode(), clientAddress)
            
            ### Transaction Stage
            # Create TCP socket
            serverTCPSocket = socket(AF_INET, SOCK_STREAM)
            # Connect to the client
            serverTCPSocket.connect((clientAddress[0], r_port))
            # Open the file
            content = open(file, 'rb')
            while True:
                # Read a chunk from the file
                chunk = content.read(CHUNK_SIZE)
                # No more chunk to read
                if not chunk:
                    break
                # Send to the client
                serverTCPSocket.sendall(chunk)
            # Close file and socket
            content.close()
            serverTCPSocket.close()
        elif request.cmd == "PUT":
            # Get the file from storage_directory
            file = os.path.join(dir, request.filename)
            # Create TCP socket
            serverTCPSocket = socket(AF_INET, SOCK_STREAM)
            serverTCPSocket.bind(('', 0))
            # Get the port number on which the server is expecting the file
            _, r_port = serverTCPSocket.getsockname()
            # Send to the client
            serverUDPSocket.sendto(str(r_port).encode(), clientAddress)
            serverTCPSocket.listen(5)
            
            ### Transaction Stage
            # Wait for the connection from client to transfer file
            transmissionSocket, _ = serverTCPSocket.accept()
            # Open the file
            content = open(file, 'wb')
            while True:
                # Get a chunk from the client
                chunk = transmissionSocket.recv(CHUNK_SIZE)
                # No more chunk to write
                if not chunk:
                    break
                # Write to the file
                content.write(chunk)
            # Close file and socket
            content.close()
            serverTCPSocket.close()
        else:
            # Invalid request
            serverUDPSocket.sendto('401 Invalid Request'.encode(), clientAddress)