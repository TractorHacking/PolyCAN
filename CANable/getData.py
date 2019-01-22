import socket

class Packet:
    def __init__(self,pkt):
        d = int.from_bytes(pkt,byteorder='big')
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
        print("printint!")
        print(pkt)
        print(self)
         
    def __str__(self):
        string = "Packet:"
        #string += "\ncan_id:\t\t"
        #string += format(self.can_id,'08X')
        #string += "\ncan_dlc:\t"
        #string += str(self.d_len)
        #string += "\ncan_data:\t"
        #string += str((self.data))
        #string += "\nWhat We Know:"
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
        #string += str(self.da)
        string += " ".join(["{:02X}".format(count) for count in self.da])
        string += "\n"
        return string 


sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))

while(1):
    p = sock.recv(1024)
    d = int.from_bytes(p,byteorder='big')
    pkt = Packet(p)

data = d & 0x00FFFFFFFFFFFFFFFF
len = d  & 0x0F0000000000000000000000


