import socket
import sys
import time
StartTime = time.time()
class Packet:
    def __init__(self):
       pass
    def initFromCanUtils(self,line):
        #This info is not known so put in default
        self.error = 0 
        self.remoteTrRequest = 0 
        self.frameFormat = 1
        self.flags     =  0
        self.padding     = 0

        line = line.split()
        self.time = float(line[0][1:-1])
        pkt = line[2]
        pkt.split('#')

        print("can_id:")
        print(pkt[0])
        self.can_id  = hex(pkt[0])
        self.data    = hex(pkt[1]) 
        self.d_len   = len(pkt[1])/2 

        self.priority = (self.can_id & 0x1C000000) >> 26 
        self.pf      = (self.can_id & 0xFF0000)  >> 16  
        if(self.pf <= 239):
            self.pgn     = (self.can_id & 0x3FF0000) >> 8  
            self.da      = (self.can_id & 0xFF00)    >> 8
        else:
            self.pgn     = (self.can_id & 0x3FFFF00) >> 8  
            self.da      = 255
        self.sa      = self.can_id & 0xFF
        print(self)


    def initFromPkt(self,pkt):
        d = int.from_bytes(pkt,byteorder='big')
        self.time = time.time() - StartTime
        self.can_id  = int.from_bytes(pkt[0:4],byteorder='little')
        self.error = (self.can_id & 0x20000000) >> 29
        self.remoteTrRequest = (self.can_id & 0x40000000) >> 30
        self.frameFormat = (self.can_id & 0x80000000) >> 31
        self.d_len = pkt[4]
        self.flags     = pkt[5]
        self.padding     = int.from_bytes(pkt[6:8],byteorder='little')
        self.data    = pkt[8:8+self.d_len]
        self.priority = (self.can_id & 0x1C000000) >> 26 
        self.pf      = (self.can_id & 0xFF0000)  >> 16  
        if(self.pf <= 239):
            self.pgn     = (self.can_id & 0x3FF0000) >> 8  
            self.da      = (self.can_id & 0xFF00)    >> 8
        else:
            self.pgn     = (self.can_id & 0x3FFFF00) >> 8  
            self.da      = 255
        self.sa      = self.can_id & 0xFF
        print(self)
         
    def toCSV(self):
        string = self.time
        string += ' , '
        string = str(self.pgn)
        string += ' , '
        string = self.time
        string += ' , '
        string += str(self.da)
        string += ' , '
        string += str(self.sa)
        string += ' , '
        string += str(self.priority)
        string += ' , '
        string += " ".joint(["{:02X}".format(x) for x in self.da])
        string += "\n"

    def __str__(self):
        string =  "Packet:"
        string += "Time:"
        string += str(self.time)
        string += "\nError:\t\t\t"
        string += str(self.error)
        string += "\nRemote Tr Requ:\t\t"
        string += str(self.remoteTrRequest)
        string += "\nFrame Format:\t\t"
        string += str(self.frameFormat)
        string += "\ncan_pgn:\t\t0x"
        string += format(self.pgn,'05X')
        string += '\t('+str(self.pgn)+')'
        string += "\nDestination Address:\t0x"
        string += format(self.da,'02X')
        string += '\t('+str(self.da)+')'
        string += "\nSource Address:\t\t0x"
        string += format(self.sa,'02X')
        string += '\t('+str(self.sa)+')'
        string += "\npriority:\t\t"
        string += str(self.priority)
        string += "\nData:\t\t\t"
        string += str(self.da)
        string += "\n"
        return string 

def listenForPkts():
   sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
   sock.bind(("can0",))

   while(1):
      p = sock.recv(1024)
      d = int.from_bytes(p,byteorder='big')
      pkt = Packet(p)

   data = d & 0x00FFFFFFFFFFFFFFFF
   len = d  & 0x0F0000000000000000000000


print("starting!\n")
print(len(sys.argv))
if(len(sys.argv)==1):
   #no argumnets so listen for packets
   listenForPkts()

#given command argument convert the candump file to csv
for file in sys.argv[1:]:
   lines = list()
   with open(file) as f:
      lines = f.readlines()
   for line in lines:
      p = Packet()
      p.initFromCanUtils(line)
      print(p.toCSV)


