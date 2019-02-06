import socket
import sys
import time
StartTime = time.time()
class Packet:
    def __init__(self):
       pass
    def initFromCanUtils(self,line):
        #print(line)
        #This info is not known so put in default
        self.error = 0 
        self.remoteTrRequest = 0 
        self.frameFormat = 1
        self.flags     =  0
        self.padding     = 0
        try:
            spline = line.split()
            self.time = float(spline[0][1:-1])
            pkt = spline[2]
            pkt = pkt.split('#')

            self.can_id  = int(pkt[0],16)
            if(len(pkt[1])>1):
                self.data    = int(pkt[1],16) 
                self.d_len   = int(len(pkt[1])/2) 
            else:
                self.data = 0;
                self.d_len = 0;

            self.priority = (self.can_id & 0x1C000000) >> 26 
            self.pf      = (self.can_id & 0xFF0000)  >> 16  
            if(self.pf <= 239):
                self.pgn     = (self.can_id & 0x3FF0000) >> 8  
                self.da      = (self.can_id & 0xFF00)    >> 8
            else:
                self.pgn     = (self.can_id & 0x3FFFF00) >> 8  
                self.da      = 255
            self.sa      = self.can_id & 0xFF
            self.valid = True
            #print(self)
        except(ValueError):
            print("INVALID")
            print(line)
            self.valid = False

    def initFromCSV(self,line):
        #print(line)
        #This info is not known so put in default
        self.error = 0 
        self.remoteTrRequest = 0 
        self.frameFormat = 1
        self.flags     =  0
        self.padding     = 0
        try:
            spline = line.split(',')
            self.time = float(spline[0])
            self.pgn = int(spline[1])
            self.da  = int(spline[2])
            self.sa  = int(spline[3])
            self.priority = int(spline[4])
            if(len(spline[5])>1):
                d = spline[5].replace(" ","")
                self.d_len = int(len(d)/2);
                self.data = int(d,16);
            else:
                self.d_len = 0
                self.data  = 0
            self.valid = True
            #print(self)
        except(ValueError):
            print("INVALID")
            print(line)
            self.valid = False


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
        self.data = int.from_bytes(self.data,byteorder = 'big')
        self.priority = (self.can_id & 0x1C000000) >> 26 
        self.pf      = (self.can_id & 0xFF0000)  >> 16  
        if(self.pf <= 239):
            self.pgn     = (self.can_id & 0x3FF0000) >> 8  
            self.da      = (self.can_id & 0xFF00)    >> 8
        else:
            self.pgn     = (self.can_id & 0x3FFFF00) >> 8  
            self.da      = 255
        self.sa      = self.can_id & 0xFF
        self.valid = True
        #print(self)
         
    def toPkt(self):
        pkt = bytearray()
        for i in range(16):
            pkt.append(0)
        self.pf = self.pgn>>8
        if((self.pf & 0xFF00 >> 8)<= 239):
            self.can_id  = (self.pgn << 8) | (self.da << 8)
        else:
            self.can_id  = (self.pgn << 8) 
        self.can_id |= self.error << 29
        self.can_id |= self.remoteTrRequest << 30
        self.can_id |= self.frameFormat << 31
        self.can_id |= self.priority << 26
        self.can_id |= self.pf << 16
        self.can_id |= self.sa 


        pkt[0:4] = self.can_id.to_bytes(4,byteorder='little')
        pkt[4] = self.d_len
        pkt[5] = self.flags
        pkt[6:8] = self.padding.to_bytes(2,byteorder='big')
        pkt[8:8+self.d_len] = self.data.to_bytes(self.d_len,byteorder='big')
        
        pkt = bytes(pkt)
        self.valid = True
        return pkt
        #print(self)
 
    def turnHexToStr(hexV,bytesLen):
        tempV = hexV;
        string = ''
        for i in range(bytesLen):
            val = hexV & 0xFF
            hexV >>= 8
            string = (format(val,'02X') + ' ') + string
        return string 


    def toCSV(self):
        string = ""
        string = str(self.time)
        string += ','
        string += str(self.pgn)
        string += ','
        string += str(self.da) 
        string += ','
        string += str(self.sa)
        string += ','
        string += str(self.priority)
        string += ','
        string += Packet.turnHexToStr(self.data,self.d_len)
        string += "\n"
        return string

    def __str__(self):
        string =  "Packet:\n"
        string += "Time:\t\t\t"
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
        string += "\nData(" + str(self.d_len)+"):\t\t"
        string += Packet.turnHexToStr(self.data,self.d_len)
        string += "\n"
        return string 


