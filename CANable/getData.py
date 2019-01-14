import socket

sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
sock.bind(("can0",))

p = sock.recv(16)
d = int.from_bytes(p,byteorder='big')

data = d & 0x00FFFFFFFFFFFFFFFF
len = d  & 0x0F0000000000000000000000

