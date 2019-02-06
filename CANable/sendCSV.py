import socket
import time
import sys
import packet 
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))
if(len(sys.argv) !=2):
    print("Usage:sendCSV file.csv")
    sys.exit()
file = sys.argv[1]
inlines = list()
with open(file) as f:
    f.readline()
    inlines = f.readlines()
    for line in inlines:
        p = packet.Packet()
        p.initFromCSV(line)
        if(p.valid):
            sock.send(p.toPkt())
            time.sleep(0.02)

