from socket import socket, AF_INET, SOCK_DGRAM
from consts import *


socket = socket(AF_INET, SOCK_DGRAM)
socket.bind(('0.0.0.0', PORT))

while True:
    message, _ = socket.recvfrom(1024)
    message = message.decode(FORMAT)
    print(message)

