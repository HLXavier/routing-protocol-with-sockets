import socket
from consts import *


socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(message):
    message = message.encode(FORMAT)
    socket.sendto(message, (IP, PORT))

while True:
    message = input('--> ')
    send(message)
