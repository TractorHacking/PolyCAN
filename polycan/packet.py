import socket
import sys
import time
import math
StartTime = time.time()
class Packet:
    def __init__(self):
       pass

    def initFromCanUtils(self,line):
        self.initFromCanUtils(line)
        self.checkForSeg()

    def checkForSeg(self):
        self.pktNum   = 1
        self.actualPGN = self.pgn
        self.numPkt   = 1
        self.numBytes = 0
        self.actualData = []; 
        if(self.pgn == 60416):#start of long packet
            self.allDone = False
            self.numBytes =   (self.data &   (0x0000FF0000000000)) >> 5*8 
            self.numBytes <<= 8
            self.numBytes |=  (self.data &   (0x00FF000000000000)) >> 6*8 
            
            self.numPkt =     (self.data &   (0x000000FF00000000)) >> 4*8
            
            self.actualPGN =  (self.data &   (0x00000000000000FF)) 
            self.actualPGN <<= 8
            self.actualPGN |= (self.data &   (0x000000000000FF00)) >> 1*8
            self.actualPGN <<= 8
            self.actualPGN |= (self.data &   (0x0000000000FF0000)) >> 2*8
            
            self.pktNum = 1
            self.actualData = [];
    def combinePacket(self,pkt):
        if(pkt.pgn != 60160 or self.pgn != 60416):#the pgn for a new segment of data
            print("notValid pkt pgn","pkt.pgn",pkt.pgn,"   self.pgn",self.pgn)
            pkt.valid = False
            return
        curPktNum =  (pkt.data &      (0xFF00000000000000) ) >> 7*8
        if(curPktNum!=self.pktNum):
            pkt.valid = False
            print("notValid pkt num, Expected:",self.pktNum,",got:",curPktNum)
            return
        self.pktNum += 1
        for i in range(7):
            mask = (0x00FF000000000000)
            mask >>=i*8
            b = pkt.data & mask
            b >>= (6-i)*8
            self.actualData.append(b)
            self.numBytes -=1
            if(self.numBytes <= 0):
                break

       
        if(self.numBytes <= 0):
            self.allDone = True
            self.valid   = True
            self.data = 0
            for i in range(len(self.actualData)):
                self.data <<= 8
                self.data |= self.actualData[i]
            self.d_len = len(self.actualData);
            self.pgn = self.actualPGN


    def initFromCanUtilsHelper(self,line):
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
            self.allDone = True
            #print(self)
        except(ValueError):
            print("INVALID")
            print(line)
            self.valid = False
            self.allDone = True

    def initFromCSV(self,line):
        self.initFromCSVHelper(line)
        self.checkForSeg()

    def initFromCSVHelper(self,line):
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
            self.allDone = True
            #print(self)
        except(ValueError):
            print("INVALID")
            print(line)
            self.valid = False
            self.allDone = True


    def initFromPkt(self,pkt):
        self.initFromPktHelper(pkt)
        self.checkForSeg()

    def initFromPktHelper(self,pkt):
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
        self.allDone = True
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
        self.allDone = True
        return pkt
        #print(self)
    def sendPacket(self,sock):
        if(self.d_len <=8):
            sock.send(self.toPkt())
            return
        #need to break up into multiple packets
        head = Packet()
        head.error = 0
        head.remoteTrRequest = 0
        head.frameFormat = 1
        head.flags     =  0
        head.padding     = 0
        head.priority = self.priority
        head.pgn = 60416
        head.d_len = 8
        head.da = self.da
        head.sa = self.sa

        head.data   = 32
        head.data <<= 8 
        head.data  |= self.d_len & 0xFF
        head.data <<= 8 
        head.data  |= (self.d_len & 0xFF00) >> 8
        head.data <<= 8
        head.data  |= math.ceil(self.d_len/7)
        head.data <<= 8
        head.data  |= 0xFF 
        head.data <<= 8
        head.data  |= (self.pgn & 0x0000FF)
        head.data <<= 8
        head.data  |= ((self.pgn & 0x00FF00) >> 8)
        head.data <<= 8
        head.data  |= ((self.pgn & 0xFF0000) >> 16)
        sock.send(head.toPkt())
        bytesLeft = self.d_len
        pktNum = 1
        while(bytesLeft > 0):
            #time.sleep(0.05)
            mid = Packet()
            mid.error = 0
            mid.remoteTrRequest = 0
            mid.frameFormat = 1
            mid.flags     =  0
            mid.padding     = 0
            mid.priority = self.priority
            mid.pgn = 60160
            mid.d_len = 8
            mid.data = pktNum
            mid.da = self.da
            mid.sa = self.sa
            for i in range(7):
                if(bytesLeft<=0):
                    b = 0xFF
                else:
                    b = self.getByte(bytesLeft-1,self.data)
                mid.data <<= 8
                mid.data |= b
                bytesLeft -= 1

            sock.send(mid.toPkt())
            pktNum += 1
            if(bytesLeft<=0):
                break

    def getByte(self,index,s):
       mask = 0xFF << index*8 
       b = s & mask
       b >>= index*8
       return b
 
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


def getNewPacket(sock):
    try:
        p = sock.recv(1024)
    except socket.timeout:
        pkt = Packet()
        pkt.valid = False
        return pkt
    pkt = Packet()
    pkt.initFromPkt(p)
    if(not(pkt.valid) | pkt.allDone):
        print("not valid!")
        return pkt
    while(not pkt.allDone):
        p = sock.recv(1024)
        pktNew = Packet()
        pktNew.initFromPkt(p)
        pkt.combinePacket(pktNew)
    return pkt


