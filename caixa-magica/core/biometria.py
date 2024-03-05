import bio
import json
import socket
from time import sleep

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

import funcoes_logs

HOST = ''  # The server's hostname or IP address
PORT = 0        # The port used by the server
BUFSIZE = 0

with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    HOST = config['core']['host']
    PORT = config['core']['port']
    BUFSIZE = config['core']['bufsize']

def send(usuario):
    funcoes_logs.insere_log("Entrando em send() com usuario " + str(usuario), local, 2)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'qrcode',
                'conta': usuario
            }
            s.connect((HOST, PORT))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)
        funcoes_logs.insere_log("Recebido: " + str(repr(data)), local, 0)
    except:
        funcoes_logs.insere_log("Verifique se o server esta up", local, 3)

def send_type(t):
    funcoes_logs.insere_log("Entrando em send_type()", local, 2)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': t
            }
            s.connect((HOST, PORT))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)
        funcoes_logs.insere_log("Recebido: " + str(repr(data)), local, 2)

    except:
        funcoes_logs.insere_log("Verifique se o server esta up", local, 3)

while True:
    biom = bio.ler_biometria()
    if biom != None and biom != "responsavel":
        funcoes_logs.insere_log("Biometria " + str(biom), local)
        user_id = int(biom)
        if user_id > 0:
            #usuário comum - cobrar
            #send(user_id)
            pass
    elif biom == "responsavel":
        funcoes_logs.insere_log("Responsável - iniciar fechamento", local, 2)
        send_type('fechar')
        exit()
    else:
        funcoes_logs.insere_logo("Biometria não reconhecida", local, 3)
        send_type('erro')
    sleep(1)
