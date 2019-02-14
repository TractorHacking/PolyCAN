import socket
import sys
import time
import packet
if(len(sys.argv)!=2):
    print("Usage: convertCandump2Csv file.log")
    sys.exit()

sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))
#given command argument convert the candump file to csv
for file in sys.argv[1:]:
   inlines = list()
   outlines = list()
   with open(file) as f:
      f.readline()
      inlines = f.readlines()
   for line in inlines:
      p = packet.Packet()
      p.initFromCanUtils(line)
      if(p.valid):
        outlines.append(p.toCSV())
   with open(file.replace('.log','.csv'),"w+") as f:
       f.write("Time,PGN,DA,SA,Priority,Data\n")
       for line in outlines:
           f.write(line)

