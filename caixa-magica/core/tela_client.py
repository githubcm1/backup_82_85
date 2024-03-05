import socket
import json
from time import sleep

import funcoes_logs

HOST = 'localhost'  # The server's hostname or IP address
PORT = 30020        # The port used by the server

local = "tela_client.py"

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conectado = False
while not conectado:
    try:
        #s.connect((HOST, PORT))
        sc.connect((HOST, 30110))
        conectado = True
        print("Socket da tela conectado")
    except Exception as e:
        print("Erro de conexão do socket da tela", e)
    sleep(1)


def enviar_tela(tela, nome=''):
    funcoes_logs.insere_log("Entrei enviar_tela", local)
    i = 0
    limite = 10

    while i < limite:
        try:
            data = {
            'tela': tela,
            'nome': nome
            }
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            funcoes_logs.insere_log("Enviei enviar_tela", local)
            return
        except Exception as e:
            funcoes_logs.insere_log("Erro enviar_tela: " + str(e), local)

        i = i + 1
        sleep(0.1)

def enviar_catraca(timeout_catraca,passou_catraca):
    try:
        data = {
            'timeout': timeout_catraca,
            'catraca': passou_catraca
        }

        js = json.dumps(data)
        sc.sendall(js.encode('utf-8'))
        print('Received', repr(data))
    except:
        print("Verifique se o server está up - Catraca")
