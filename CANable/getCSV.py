import time
import socket
import packet

sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))
count = 0;

with open("outPutFile.csv","w+") as f:
    f.write("Time,PGN,DA,SA,Priority,Data\n")
    while(1):
        count += 1
        p = sock.recv(1024)
        pkt = packet.Packet()
        pkt.initFromPkt(p);
        if(pkt.valid):
            f.write(pkt.toCSV());
            print(count);
        


