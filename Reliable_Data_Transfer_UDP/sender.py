from packet import Packet
from socket import *
import argparse
import time
import threading

SEQNUM_LOG_FILE_NAME = "seqnum.log"
ACK_LOG_FILE_NAME = "ack.log"
CHUNK_SIZE = 1024
MAX_DATA_SIZE = 500

if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("host_addr", type=str, help="host address of the network emulator")
    parser.add_argument("send_port", type=int, help="UDP port number used by the emulator to receive data from the sender")
    parser.add_argument("receive_port", type=int, help="UDP port number used by the sender to receive ACKs from the emulator")
    parser.add_argument("timeout", type=int, help="timeout interval in units of millisecond")
    parser.add_argument("filename", type=str, help="name of the file to be transferred")
    args = parser.parse_args()
    
    # Variables
    cur_seqnum = 0
    unsent_packets = []
    lock = threading.Lock()
    
     # Open the log files
    seqnum_log = open(SEQNUM_LOG_FILE_NAME, "w")
    ack_log = open(ACK_LOG_FILE_NAME, "w")
    
    # Get the content of the file as packets
    with open(args.filename, "r") as file:
        while True:
            data = file.read(MAX_DATA_SIZE)
            # No more data to read
            if not data:
                break
            unsent_packets.append(Packet(1, cur_seqnum, len(data), data))
            cur_seqnum += 1
    
    # Create an EOT packet that will be sent later
    eot = Packet(2, cur_seqnum, 0, '')
    
     # Create UDP socket
    senderSocket = socket(AF_INET, SOCK_DGRAM)
    senderSocket.bind(('', args.receive_port))
    
    def receive(senderSocket, seqnum_log, ack_log):
        # Receive and send must use the same instance of unsent_packets and lock
        global unsent_packets, lock
        while True:
            # Get the packet
            packet = Packet(senderSocket.recv(CHUNK_SIZE))
            typ, seqnum, _, _ = packet.decode()
            print("Receiving packet {}".format(seqnum))
            # Prevent multiple threads from accessing and modifying unsent_packets
            with lock:
                # EOT received
                if typ == 2:
                    ack_log.write("EOT\n")
                    seqnum_log.close()
                    ack_log.close()
                    senderSocket.close()
                    exit()
                # Data packet received
                else:
                    ack_log.write(str(seqnum) + "\n")
                    # Remove received data packet from unsent_packets
                    for packet in unsent_packets:
                        if packet.seqnum == seqnum:
                            unsent_packets.remove(packet)
                            break  
                    
    def send(senderSocket, seqnum_log, idx, addr, port, eot):
        # Receive and send must use the same instance of unsent_packets and lock
        global unsent_packets, lock
        while True:
            # Prevent multiple threads from accessing and modifying unsent_packets
            with lock:
                # If no more unsent data packets
                if len(unsent_packets) == 0:
                    break
                # Send first 10 packets at a time (if there exists)
                while idx < 10 and idx < len(unsent_packets):
                    packet = unsent_packets[idx]
                    print("Sending packet {}".format(packet.seqnum))
                    senderSocket.sendto(packet.encode(), (addr, port))
                    seqnum_log.write(str(packet.seqnum) + "\n")
                    idx += 1
            idx = 0
            # Wait timeout
            time.sleep(args.timeout / 1000.0)
        # Send an EOT because no more unsent data packets
        senderSocket.sendto(eot.encode(), (addr, port))
        seqnum_log.write("EOT\n")
            
    receive_thread = threading.Thread(target=receive, args=(senderSocket, seqnum_log, ack_log))
    send_thread = threading.Thread(target=send, args=(senderSocket, seqnum_log, 0, args.host_addr, args.send_port, eot))
    
    receive_thread.start()
    send_thread.start()
    
    receive_thread.join()
    send_thread.join()
    