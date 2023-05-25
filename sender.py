from socket import socket, AF_INET, SOCK_DGRAM
from time import sleep


HOST_IP = '192.168.1.229'
PORT = 5000
FORMAT = 'utf-8'

def send(message):
    message = message.encode(FORMAT)
    socket.sendto(message, (HOST_IP, PORT))


socket = socket(AF_INET, SOCK_DGRAM)

while True:
    message = 'SENDER'
    send(message)
    sleep(3)