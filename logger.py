from tabulate import tabulate
from consts import *


def log_routing_table(routing_table):
    table = []

    for destination, value in routing_table.items():
        metric, next_hop = value
        table.append([destination, metric, next_hop])
    
    print(tabulate(table, headers=HEADERS, tablefmt='fancy_grid'))


def log_timeout(neighbours):
    print(f'[{neighbours}] TIMEOUT')


def log_message(message, origin):
    print(f'[{origin}] {message}')

    
