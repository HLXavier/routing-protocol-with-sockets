from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread, Lock
from time import time, sleep
from os import system
from consts import *
from logger import *


def read_neighbours():
    with open('IPVizinhos.txt', 'r') as file:
        return file.read().splitlines()


def format_routing_table():
    formated = ''

    for key, value in routing_table.items():
        formated += f'*{key};{value[0]}'
    
    return formated

# TODO: Não pode enviar as rotas para o vizinho que enviou a mensagem
def update_routing_table(message, origin):
    if not routing_table or origin not in routing_table:
        routing_table[origin] = [1, origin]
        return True

    routes = message.split('*')[1:]
    modified = False

    for route in routes:
        ip, metric = route.split(';')

        if ip not in routing_table or int(metric) + 1 < routing_table[ip][0]:
            routing_table[ip] = [int(metric) + 1, origin]
            modified = True

    return modified


def send(ip, message):
    message = message.encode(FORMAT)
    socket.sendto(message, (ip, PORT))


def send_routing_table():
    for neighbour in neighbours:
        if not routing_table:
            send(MSG_JOIN)
        else:
            send(neighbour, format_routing_table())

    
def receiver():
    while True:
        message, origin = socket.recvfrom(1024)
        message = message.decode(FORMAT)

        last_seen[origin] = time()
        with lock:
            modified = update_routing_table(message, origin[0])

        if modified:
            send_routing_table()


def sender():
    while True:
        send_routing_table()
        sleep(MSG_EXG_INTERVAL)


def pinger():
    while True:
        for neighbour in neighbours:
            if neighbour not in last_seen or time() - last_seen[neighbour] > TIMEOUT:
                with lock:
                    del routing_table[neighbour]
                send_routing_table()
        sleep(MSG_PING_INTERVAL)


# Main
neighbours = read_neighbours()
routing_table = {}
last_seen = {}

# Socket    
socket = socket(AF_INET, SOCK_DGRAM)
socket.bind((NETWORK, PORT))

# Threading
lock = Lock()

Thread(target=sender).start()
Thread(target=receiver).start()


while True:
    system('clear')
    log_routing_table(routing_table)
    sleep(1)
