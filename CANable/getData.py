import socket

class Packet:
    def __init__(self,pkt):
        d = int.from_bytes(pkt,byteorder='big')
        self.can_id  = pkt[0:4]
        self.can_dlc = pkt[4]
        self.pgn     = pkt[5:8]
        self.data    = pkt[8:]
        print("printint!")
        print(self)
         
    def __str__(self):
        str = "Packet:"
        str += "\ncan_id:\t"
        str += str(self.can_id.hex)
        str += "\ncan_dlc:\t"
        str += str(hex(self.can_dlc))
        str += "\ncan_pgn:\t"
        str += str(hex(self.pgn))
        str += "\ncan_data:\t"
        str += str(hex(self.data))
        str += "\n"
        return str




sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))

while(1):
    p = sock.recv(1024)
    d = int.from_bytes(p,byteorder='big')
    pkt = Packet(p)

data = d & 0x00FFFFFFFFFFFFFFFF
len = d  & 0x0F0000000000000000000000


