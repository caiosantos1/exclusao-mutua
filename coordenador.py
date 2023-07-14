import socket
import os
import time
import threading

ip = 'localhost'
port = 12000

lock = threading.Lock()

REQUEST = '1'
RELEASE = '2'
GRANT = '3'

requests_socket = []
requests_pid = []
clients = {}

# Função para receber conexões de clientes. Cria um socket TCP, faz um bind do ip e da porta e fica em um loop aceitando conexões de clientes.
# Quando é estabelecida uma conexão, é criada uma thread.
def recv_connection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen()
    while True:
        client, addr = server.accept()
        handle_client = threading.Thread(target=process_handler, args=(client,))
        handle_client.start()

"""Função para lidar com as mensagens enviadas pelo cliente. Recebe uma mensagem por socket e divide-a usando |.
    Também é adquirido o lock para garantir a exclusão mútua. Se a mensagem for do tipo REQUEST, verifica se a fila de pedidos está vazia. 
    Se sim, envia uma mensagem de GRANT para o cliente atual. Em seguida, adiciona o socket do cliente e o ID do processo à fila de pedidos. 
    Se a mensagem for do tipo RELEASE, verifica se o ID do processo está presente na fila de pedidos. Se sim, atualiza o número de GRANTS para o processo,
    remove o socket do cliente e o ID do processo da fila de pedidos e, se houver mais clientes na fila, envia uma mensagem de GRANT para o próximo cliente na fila. 
    Por fim, libera o lock."""
def process_handler(client_socket):
    while True:
        txt = client_socket.recv(100).decode()
        msg = txt.split('|')
        lock.acquire()
        if msg[0] == REQUEST:
            if len(requests_socket) == 0:
                send_grant(client_socket)
            requests_socket.append(client_socket)
            requests_pid.append(msg[1])
        elif msg[0] == RELEASE:
            if msg[1] in requests_pid:
                number(msg[1])
                requests_socket.remove(requests_socket[0])
                requests_pid.remove(msg[1])
                if len(requests_socket) > 0:
                    send_grant(requests_socket[0])
        lock.release()

# Essa função envia uma mensagem de GRANT para um cliente específico por meio do socket.
def send_grant(client_socket):
    grant_msg = GRANT + '|'
    grant_msg = padding(grant_msg, 100, '0')
    client_socket.send(grant_msg.encode())


def padding(string, tam, charactere):
    dif = tam - len(string)
    for _ in range(dif):
        string = string + charactere
    return string

def number(pid):
    client = clients.get(pid)
    if client:
        clients[pid] += 1
    else:
        clients[pid] = 1

# Função que mostra o menu com as opções desejadas 
def menu():
    while True:
        os.system(('clclear' if os.name == 'nt' else 'clear'))
        print('Digite uma das opções abaixo.')
        print('1 - Fila de pedidos atual')
        print('2 - Quantas vezes cada processo foi antendido')
        print('3 - Encerrar Execução')
        user_choice = input('Opção: ')
        if user_choice == '1':
            show_current_queue()
        elif user_choice == '2':
            show_requests_pid()
        elif user_choice == '3':
            print('Fim!')
            break
        else:
            print('\nOpção inválida!')
        input('\nDigite qualquer tecla para voltar ao menu')

# Essa função printa a fila de pedidos atual na tela. Ela adquire o lock para garantir que a leitura dos dados seja feita de forma exclusiva. 
def show_current_queue():
    os.system(('clear' if os.name == 'nt' else 'clear'))
    print('Fila de pedidos atual:\n') 
    i = 0
    lock.acquire()
    print('Posição | ID')
    for pid in requests_pid:
        i += 1
        string = padding((str(i) + ' '), 6, ' ')
        string += ('  | ' + str(pid))
        print(string)
    lock.release()

# Essa função printa o número de GRANTS atendidos por cada processo na tela. Também é adquirido o lock para garantir que a leitura dos dados seja feita de forma exclusiva
def show_requests_pid():
    os.system(('clear' if os.name == 'nt' else 'clear'))
    print('Número de requests atendidos de cada processo:\n') 
    lock.acquire()
    print('ID              | Quantidade de GRANTS')
    for pid in clients: 
        print(str(pid) + ' | ' + str(clients[pid]))
    lock.release()

if __name__ == '__main__':
    recv_connections = threading.Thread(target=recv_connection)
    recv_connections.start()
    menu()
