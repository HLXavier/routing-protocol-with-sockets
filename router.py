from socket import socket, gethostname, gethostbyname, AF_INET, SOCK_DGRAM
from threading import Thread, Lock
from time import time, sleep
from consts import *
from logger import *
import sys


def read_neighbours():
    path = None
    if len(sys.argv) >= 3:
        path = sys.argv[2]
    else:
        path = 'IPVizinhos.txt'

    with open(path, 'r') as file:
        return file.read().splitlines()


# { 'destination': [metric, next_hop] }
def format_routing_table():
    formated = ''

    for destination, value in routing_table.items():
        metric, _ = value
        formated += f'*{destination};{metric}'
    
    return formated


def update_routing_table(message, origin):
    modified = False
    routes = [f'{origin};0'] + message.split('*')[1:]

    for route in routes:
        destination, metric = route.split(';')
        metric = int(metric)

        is_new_path = destination not in routing_table
        is_better_path = False

        if not is_new_path:
            current_metric, _ = routing_table[destination]
            is_better_path = metric + 1 < current_metric

        if destination != ip and (is_new_path or is_better_path):
            routing_table[destination] = [metric + 1, origin]
            modified = True

    return modified


def receive():
    message, origin = socket.recvfrom(1024)
    origin_ip, _ = origin
    return message.decode(FORMAT), origin_ip


def send(ip, message):
    message = message.encode(FORMAT)
    socket.sendto(message, (ip, PORT))


def propagate_routing_table():
    message = MSG_JOIN

    if routing_table:
        message = format_routing_table()

    for neighbour in neighbours:
        send(neighbour, message)
        log_message(message, ip)
        

def timeout(neighbour):
    if neighbour not in last_seen: return

    if time() - last_seen[neighbour] > TIMEOUT:
        with lock:
            del routing_table[neighbour]
            del last_seen[neighbour]

            unreachable_targets = [target for target, path in routing_table.items() if path[1] == neighbour]
            for target in unreachable_targets:
                del routing_table[target]

        log_timeout(neighbour)
        propagate_routing_table()

    
def receiver():
    while True:        
        message, origin = receive()
        log_message(message, origin)

        last_seen[origin] = time()

        with lock:
            modified = update_routing_table(message, origin)

        if modified:
            propagate_routing_table()


def sender():
    while True:
        propagate_routing_table()
        sleep(MSG_EXG_INTERVAL)


def pinger():
    while True:
        for neighbour in neighbours:
            timeout(neighbour)
        sleep(MSG_PING_INTERVAL)

def logger():
    while True:
        log_routing_table(routing_table)
        sleep(10)

# Main
neighbours = read_neighbours()
routing_table = {}
last_seen = {}
ip = sys.argv[1]


# Socket    
socket = socket(AF_INET, SOCK_DGRAM)
socket.bind((NETWORK, PORT))

# Threading
lock = Lock()


# # 1 - 2 - 3
# message, origin = '*1;1*3;1', '2'
# update_routing_table(message, origin)
# log_routing_table(routing_table)

# # 1 - 2
# # \  /
# #   3
# message, origin = '*1;1*2;1', '3'
# update_routing_table(message, origin)
# log_routing_table(routing_table)

# # 1 - 2 
# # \  /      
# #   3 - 4 - 5 - 6
# message, origin = '*1;1*2;1*4;1*5;2', '3'
# update_routing_table(message, origin)
# log_routing_table(routing_table)

# # 1 - 2 - - -
# # \  /      |
# #   3 - 4 - 5 
# message, origin = '*1;1*3;1*5;1', '2'
# update_routing_table(message, origin)
# log_routing_table(routing_table)

Thread(target=sender).start()
Thread(target=receiver).start()
Thread(target=pinger).start()
Thread(target=logger).start()
