import sys

path_atual = "/home/pi/caixa-magica/"
path_botoes = path_atual + "/../caixa-magica-operacao/vars_serial.json"

sys.path.insert(1, path_atual + "/core/")
import funcoes_logs as insere_logs

import socket
import json
from time import sleep
import os


def send(type):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': type,
                'var_sessao': ''
            }
            s.connect((HOST, PORT))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)

            s.shutdown(socket.SHUT_RDWR)
            s.close()
    except Exception as e:
        print("erro send file: " + str(e))

HOST = ''  # The server's hostname or IP address
PORT = 0        # The port used by the server
BUFSIZE = 0

local = 'botoes.py'
insere_logs.insere_log("Iniciando botoes.py", local)

try:
    insere_logs.insere_log("Lendo configuracoes de config.json", local)
    with open(path_atual + '/../caixa-magica-vars/config.json') as json_data:
        config = json.load(json_data)
        HOST = config['core']['host']
        PORT = config['core']['port']
        BUFSIZE = config['core']['bufsize']
except Exception as e:
    insere_logs.insere_log("Erro ao ler de config.json: " + str(e), local)

while 1:
    gratuidade = 0
    dinheiro = 0
    
    try:
        # Abre o arquivo com os sinais dos botoes
        with open(path_botoes) as json_data:
            aux = json.load(json_data)
            gratuidade = aux['gratuidade']
            dinheiro = aux['dinheiro']
    except Exception as e:
        gratuidade = 0
        dinheiro = 0

    try:
        # Se ambos estao pressionados, nao fazemos nada
        if gratuidade == 1 and gratuidade == dinheiro:
            continue
        # Se a gratuidade foi pressionada
        elif gratuidade == 1:
            insere_logs.insere_log("status gratuidade: " +str(gratuidade), local)
            send("gratuidade")
            sleep(0.5)
        # Se o dinheiro foi pressionado
        elif dinheiro == 1:
            insere_logs.insere_log("status dinheiro: " + str(dinheiro), local)
            send("dinheiro")
            sleep(0.5)
    except:
        pass

    sleep(0.15)


