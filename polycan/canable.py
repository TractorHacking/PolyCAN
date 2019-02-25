from polycan.menu import *
import time
import socket
from polycan.packet import *

def get_csv(path):
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind(("can0",))
    count = 0;

    with open(path,"w+") as f:
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        while(1):
            count += 1
            pkt = packet.getNewPacket(sock)
            if(pkt.valid):
                print(pkt.toCSV());
                f.write(pkt.toCSV());
                print(count);
                



def send_csv(path):
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind(("can0",))
    if(len(sys.argv) !=2):
        print("Usage:sendCSV file.csv")
        sys.exit()
        inlines = list()
        with open(path) as f:
            f.readline()
            inlines = f.readlines()
            for line in inlines:
                p = packet.Packet()
                p.initFromCSV(line)
                if(p.valid):
                    p.sendPacket(sock)
                    time.sleep(0.05)


