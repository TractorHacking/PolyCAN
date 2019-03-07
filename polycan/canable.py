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
        sock.settimeout(3)
    except OSError:
        print('Looks like there is no CANable board setup to this computer. First estable can0 device first and try again');
        return

    count = 0;

    with open(path,"w+") as f:
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        while(1):
            count += 1
            pkt = getNewPacket(sock)
            if(pkt.valid):
                print(pkt.toCSV());
                f.write(pkt.toCSV());
                print(count);
            ifdata = select.select([sys.stdin],[],[],0)[0]
            if(len(ifdata) > 0 and ifdata[0] == sys.stdin):
                return
                


def sendCSVWhileRead(pathR,pathW):
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    sock.bind(("can0",))
    sock.settimeout(.005)
    recv = 0;
    sent = 0;
    waitToDump = True
    doneWriting = False
    change = True

    with open(pathW,"w+") as f:
       with open(pathR,'r+') as outF:
        outF.readline()
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        print("Hit Enter when you are ready to transmit!\nOnce done transmiting hit enter again to exit!")
        while(1):
            ifdata = select.select([sys.stdin],[],[],0)[0]
            if(len(ifdata) > 0  and ifdata[0] == sys.stdin):
                sys.stdin.readline()
                if(waitToDump == True):
                    waitToDump = False;
                elif(doneWriting):
                    return
            if(not waitToDump):
               line = outF.readline()
               if(not doneWriting and len(line) ==0):
                   print("Sent the entire CSV!")
                   doneWriting = True
               elif(len(line)>0):
                   p = Packet()
                   p.initFromCSV(line)
                   if(p.valid):
                       p.sendPacket(sock)
                       sent +=1
                       f.write('-'+p.toCSV())
                   change = True
            pkt = getNewPacket(sock)
            if(pkt.valid):
                recv += 1
                print(pkt.toCSV())
                f.write(pkt.toCSV())
                change = True
            if(change):
                print('Sent: ',sent,'\tRecv: ',recv)
                change = False
 

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
                p = Packet()
                p.initFromCSV(line)
                if(p.valid):
                    p.sendPacket(sock)
                    time.sleep(0.05)


