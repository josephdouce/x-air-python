# Import
import socket
import sys

# Import needed modules from osc4py3
from osc4py3.oscbuildparse import *

# Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Server
server_address = ('192.168.1.101', 10024)

# Build Message
msg = OSCMessage("/batchsubscribe",",ssiii",["meters/2", "/meters/2", 0,0,1])
#msg = OSCMessage("/info","",[])

# Send
sent = sock.sendto(encode_packet(msg), server_address)
print(msg)

# Recieve
while True:
    data, server = sock.recvfrom(512)
    try:
        print(decode_packet(data))
    except:
        print(data)

# Close
sock.close()