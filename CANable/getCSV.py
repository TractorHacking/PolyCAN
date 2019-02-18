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
        pkt = packet.getNewPacket(sock)
        if(pkt.valid):
            print(pkt.toCSV());
            f.write(pkt.toCSV());
            print(count);
        


