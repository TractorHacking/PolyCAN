from polycan.menu import *
import time
import socket
import sys
import select
from polycan.packet import *

def get_csv(path):
    try:
        sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind(("can0",))
    except OSError:
        print('Looks like there is no CANable board setup to this computer. First estable can0 device first and try again');
        return

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
                


def sendCSVWhileRead(pathR,pathW):
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind(("can0",))
    countIn = 0;
    countOut = 0;
    waitToDump = True

    with open(pathW,"w+") as f:
       with open(pathR,'r+') as outF:
        outF.readline()
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        while(1):
            count += 1
            ifdata = select.select([sys.stdin],[],[],0)[0]
            if(ifdata[0] == sys.stdin):
               waitToDump = False;
            if(not waitToDump):
               line = outF.readline()
               p = packet.Packet()
               p.initFromCSV(line)
               if(p.valid):
                   p.sendPacket(sock)
               f.write('-'+pkt.toCSV)
            pkt = packet.getNewPacket(sock)
            if(pkt.valid):
                print(pkt.toCSV())
                f.write(pkt.toCSV())
                print(count)
 

def send_csv(path):
    try:
        sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind(("can0",))
    except OSError:
        print('Looks like there is no CANable board setup to this computer. First estable can0 device first and try again');
        return
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


