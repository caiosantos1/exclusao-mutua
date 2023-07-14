import socket
import os
import threading
from datetime import datetime
import time

ip = 'localhost'
port = 12000

REQUEST = '1'
RELEASE = '2'
GRANT = '3'

r = 5
n = 2
k = 1
num_exec = r * n
current_exec = [0]

# criação do arquivo txt
def create_file():
    file = open('resultado.txt', 'w+')
    file.write('PID             | TIME\n')
    file.close()

# escreve no txt as informações do processo em execução. Obtém o ID da thread através da variável pid.
def write_file():
    pid = str(threading.get_ident())
    dif = 6 - len(pid)
    for _ in range(dif):
        pid = pid + " "
    current_time = datetime.now().strftime('%H:%M:%S.%f')
    file = open('resultado.txt', 'a+')
    file.write(pid + ' | ' + current_time + '\n')
    time.sleep(k)
    file.close()
    current_exec[0] += 1

def padding(word, tam, charactere):
    dif = tam - len(word)
    for _ in range(dif):
        word = word + charactere
    return word

# cria um socket do tipo TCP e estabelece uma conexão com um servidor usando o endereço IP e a porta.
def connect_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((ip, port))
    return server_socket

# Função para enviar uma mensagem de solicitação(Request) para o servidor.
def send_request(server_socket):
    request_msg = REQUEST + '|' + str(threading.get_ident()) + '|'
    request_msg = padding(request_msg, 100, '0')
    server_socket.send(request_msg.encode())

# Função para receber uma resposta do servidor. Ela verifica se o primeiro elemento da mensagem é um GRANT.
def recv_grant(server_socket):
    msg = server_socket.recv(100).decode()
    msg = msg.split('|')
    if msg[0] == GRANT:
        write_file()

# Função para enviar um RELEASE para o coordenador
def send_release(server_socket):
    release_msg = RELEASE + '|' + str(threading.get_ident()) + '|'
    release_msg = padding(release_msg, 100, '0')
    server_socket.send(release_msg.encode())

# Função para enviar solicitações, receber concessões e enviar liberações. chama as três ultimas funções acima.
def req_process():
    server_socket = connect_server()
    for _ in range(r):
        send_request(server_socket)
        recv_grant(server_socket)
        send_release(server_socket)
    server_socket.close()

def time_spent(time):
    time = time.split('|')
    time = time[1].split(' ')
    time = time[1]
    time = datetime.strptime(time, '%H:%M:%S.%f ')
    return time

# Função para calcular o tempo de execução do programa, escrevendo no arquivo txt o tempo gasto
def calculate_time():
    file = open('resultado.txt', 'r')
    linhas = file.readlines()
    file.close()
    first_time = linhas[1]
    last_time = linhas[len(linhas) - 1]
    first_time = time_spent(first_time)
    last_time = time_spent(last_time)
    dif = last_time - first_time
    file = open('resultado.txt', 'a')
    file.write('\nTempo de execução: ' + str(dif) + '\n')
    file.write('r: ' + str(r) + '\n')
    file.write('n: ' + str(n) + '\n')
    file.write('k: ' + str(k) + '\n')
    file.close()

if __name__ == '__main__':
    os.system('clear')
    create_file()
    processos = []
    for i in range(n):
        processo = threading.Thread(target=req_process)
        processos.append(processo)
    
    for processo in processos:
        processo.start()

    while (current_exec[0] != num_exec):
        os.system('clear')
        current_percent = round((current_exec[0]/num_exec)*100,2)
        print('Porcentagem da execução: ' + str(current_percent) + '%')
        time.sleep(1)
    os.system('clear')
    print('Completo!')
    calculate_time()