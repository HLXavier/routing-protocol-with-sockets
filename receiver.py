import socket
from consts import *


socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind((IP, PORT))
    
while True:
    message, address = socket.recvfrom(1024)
    message = message.decode(FORMAT)

    print(f'{address}: {message}')
    