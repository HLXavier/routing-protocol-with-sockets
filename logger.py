from tabulate import tabulate


headers = ['IP de Destino', 'Métrica', 'IP de Saída']

def log_routing_table(routing_table):
    table = []
    for router in routing_table.values():
        router = list(router)
        table.append(router)

    print(tabulate(table, headers=headers, tablefmt='fancy_grid'))