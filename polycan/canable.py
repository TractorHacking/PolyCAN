from polycan.menu import *
import time
import socket
import sys
import select
from polycan.packet import *

##
#Function that given a path for a log file will listen to the device can0 
#saving all command recieved in the log file. 
#hitting enter will exit the function
def get_csv(path):
    try:
        #try establising a connection with the CANable board
        sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind(("can0",))
        sock.settimeout(1)
    except OSError:
        print('Looks like there is no CANable board setup to this computer. First estable can0 device first and try again');
        return

    count = 0;

    with open(path,"w+") as f:
        #CSV header
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        while(1):
            count += 1
            #calls the function that returns a Packet
            pkt = getNewPacket(sock)
            #all packets objects have a valid field, you must check this before doing any operation on it
            if(pkt.valid):
                print(pkt.toCSV());
                f.write(pkt.toCSV());
                print(count);
            #checks if the user hit enter, if so return
            ifdata = select.select([sys.stdin],[],[],0)[0]
            if(len(ifdata) > 0 and ifdata[0] == sys.stdin):
                return
                


##
#function that will listen to the device can0 and store all commands recieved
#in the log file specified by pathW
#Will wait for the user to hit enter then will transmit commands from the 
#log file specified by pathR
#user can then exit by hitting enter again
def sendCSVWhileRead(pathR,pathW):
    try:
        #try establising a connection with the CANable board
        sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind(("can0",))
        sock.settimeout(.005)
    except OSError:
        print('Looks like there is no CANable board setup to this computer. First estable can0 device first and try again');
        return
    recv = 0;
    sent = 0;
    waitToDump = True #varible keeps track of user hitting enter first time
    doneWriting = False
    change = True #if there was any change in recv or send count

    with open(pathW,"w+") as f:
       with open(pathR,'r+') as outF:
        outF.readline()
        #csv header line
        f.write("Time,PGN,DA,SA,Priority,Data\n")
        clear_screen()
        print("Hit Enter when you are ready to transmit!\nOnce done transmiting hit enter again to exit!")
        while(1):
            #checks if user hit enter
            ifdata = select.select([sys.stdin],[],[],0)[0]
            if(len(ifdata) > 0  and ifdata[0] == sys.stdin):
                sys.stdin.readline()
                if(waitToDump == True):
                    waitToDump = False;
                elif(doneWriting):
                    return
            #not waitin to dump log files, so send out the next command
            if(not waitToDump):
               line = outF.readline()
               if(not doneWriting and len(line) ==0):
                   print("Sent the entire CSV!")
                   doneWriting = True
               elif(len(line)>0):
                   #create a new packet object
                   p = Packet()
                   #initlize the packet from a string that coresponds to a line of a csv log file
                   p.initFromCSV(line)
                   #check if valid, this needs to be always done
                   if(p.valid):
                       sendPacket(p,sock)
                       sent +=1
                       #write the packet sent to the log file, desgnate that this is a command 
                       #sent by making the timestamp negive
                       f.write('-'+p.toCSV())
                       change = True
            #get a new packet object from the function getNewPacket
            pkt = getNewPacket(sock)
            #check if valid, this needs to be always done
            if(pkt.valid):
                recv += 1
                #turn packet into a string in csv format and print to user and write to file
                print(pkt.toCSV())
                f.write(pkt.toCSV())
                change = True
            if(change):
                print('Sent: ',sent,'\tRecv: ',recv)
                change = False
 

##
#function that will just send out a log file whitout listening at all
def send_csv(path):
    try:
        sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind(("can0",))
        sock.settimeout(1)
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
                #check if valid, this needs to be always done
                if(p.valid):
                    sendPacket(p,sock)
                    time.sleep(0.05)


