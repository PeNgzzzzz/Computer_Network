from packet import Packet
from socket import *
import argparse

LOG_FILE_NAME = "arrival.log"
CHUNK_SIZE = 1024

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", type=str, help="hostname for the network emulator")
    parser.add_argument("send_port", type=int, help="UDP port number used by the link emulator to receive ACKs from the receiver")
    parser.add_argument("receive_port", type=int, help="UDP port number used by the receiver to receive data from the emulator")
    parser.add_argument("filename", type=str, help="name of the file into which the received data is written")
    args = parser.parse_args()
    
    # Variables
    expected = 0
    buffer = {}
    
    # Open the log file
    arrival_log = open(LOG_FILE_NAME, "w")
    
    # Open the file to write
    file = open(args.filename, "w")
    
    # Create UDP socket
    receiverSocket = socket(AF_INET, SOCK_DGRAM)
    receiverSocket.bind(('', args.receive_port))
    
    while True:
        # Get the packet
        packet = Packet(receiverSocket.recv(CHUNK_SIZE))
        typ, seqnum, length, data = packet.decode()
        
        # Write seqnum to the log file
        if typ == 2:
            arrival_log.write("EOT\n")
        else:
            arrival_log.write(str(seqnum) + "\n")
        
        # If the received packet follows the last packet written to the file
        if (seqnum == expected):
            # If the packet is an EOT packet
            if typ == 2:
                eot = Packet(2, seqnum, 0, '')
                receiverSocket.sendto(eot.encode(), (args.hostname, args.send_port))
                arrival_log.close()
                file.close()
                receiverSocket.close()
                break
            else:
                # Write packet to the file
                file.write(data)
                expected = expected + 1
                while expected in buffer:
                    # Extract the packet from the buffer
                    _, _, _, data = buffer[expected].decode()
                    # Remove it
                    buffer.pop(expected)
                    # Write packet to the file
                    file.write(data)
                    expected = expected + 1
        # If the packet was not previously written
        elif seqnum > expected:
            buffer[seqnum] = packet   
        
        print("Sending ack packet {}".format(seqnum))
        # Send a ACK for the packet because it is not an EOT packet
        ack = Packet(0, seqnum, 0, '')
        receiverSocket.sendto(ack.encode(), (args.hostname, args.send_port)) 