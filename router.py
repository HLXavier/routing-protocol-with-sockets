from socket import socket, timeout, AF_INET, SOCK_DGRAM
from threading import Thread, Lock
from time import sleep
from os import system
from consts import *
from logger import *

# When the receiver thread times out the stop_flag is set to False
# This stops the sender thread from sending messages
stop_flag = {}
routing_table = {}

# Solves concurrency issues
lock = Lock()

def neighbours():
    with open('IPVizinhos.txt', 'r') as file:
        return file.read().splitlines()


def format_routing_table():
    return ''.join(f'*{destination_ip};{metric}' for destination_ip, metric, _ in routing_table.values())
        

def send_routing_table(ip, socket):
    message = format_routing_table()
    message = message.encode(FORMAT)
    socket.sendto(message, (ip, PORT))
    
# TODO: "Uma atualização deverá ser feita sempre que for recebido um IP de Destino não 
# presente na tabela local. Neste caso a rota deve ser adicionada, a Métrica deve ser 
# incrementada em 1 e o IP de Saída deve ser o endereço do roteador que ensinou esta informação."

# TODO: "Uma atualização deverá ser feita sempre que for recebida uma Métrica menor para um 
# IP Destino presente na tabela local. Neste caso, a Métrica e o IP de Saída devem ser atualizadas."

# TODO: "Uma atualização deverá ser feita sempre que for um IP Destino deixar de ser divulgado. 
# Neste caso, a rota deve ser retirada da tabela de roteamento."
def receiver(ip, socket):
    while not stop_flag[ip]:
        try:
            # TODO: 
            message, _ = socket.recvfrom(1024)
            message = message.decode(FORMAT)
        except timeout:
            with lock:
                stop_flag[ip] = True
                socket.close()

# TODO: "O protocolo não prevê confirmação de recebimento de mensagens, pois a tabela será
# reenviada a cada 10 segundos. Contudo, caso o recebimento de uma mensagem de anúncio de
# rotas cause a alteração da tabela de roteamento, o roteador deve enviar sua tabela imediatamente
# para seus vizinhos."

# TODO: "Esta mensagem será enviada aos vizinhos a cada 10 segundos somente se a tabela de
# roteamento estiver vazia. Assim, logo que um roteador entrar na rede e não tiver nenhuma rota
# pré-configurada, deverá anunciar-se para os vizinhos."
def sender(ip, socket):
    while not stop_flag[ip]:
        sleep(MSG_EXG_INTERVAL)
        send_routing_table(ip, socket)
    socket.close()


for neighbour in neighbours():
    with lock:
        stop_flag[neighbour] = False
        routing_table[neighbour] = (neighbour, 1, neighbour)
    
    # Two sockets are created to avoid concurrency issues
    sender_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
    receiver_socket.bind((neighbour, PORT))
    receiver_socket.settimeout(TIMEOUT)

    Thread(target=sender, args=(neighbour, sender_socket)).start()
    Thread(target=receiver, args=(neighbour, receiver_socket)).start()


while True:
    system('clear')
    log_routing_table(routing_table)
    sleep(1)
