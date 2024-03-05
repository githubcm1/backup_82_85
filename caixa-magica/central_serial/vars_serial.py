import time
import json
import os

path_padrao = "/home/pi/caixa-magica/central_serial/"

path = path_padrao + "vars_serial.json"
path_mensagem = path_padrao + "mensagem_serial.json"

def carrega_mensagem():
    try:
        with open(path_mensagem) as json_data:
            conteudo = json.load(json_data)
    except:
        comando = "sudo echo '{\"mensagem\": \"CA000EZ\"}' | sudo tee " + path_mensagem
        os.system(comando)

        conteudo = []
    return conteudo

def carrega_vars():
    try:
        with open(path) as json_data:
            conteudo = json.load(json_data)
    except:
        conteudo = []
    return conteudo

# Carrega conf do sonar
def distancia_sonar():
    try:
        conteudo = carrega_vars()
        return conteudo['sonar']
    except:
        return 999999

# Carrega luz ambiente
def luz_ambiente():
    try:
        conteudo = carrega_vars()
        return conteudo['luz_ambiente']
    except:
        return -1

# Carrega sensor_mao
def sensor_mao():
    try:
        conteudo = carrega_vars()
        return conteudo['sensor_mao']
    except:
        return -1

def gratuidade():
    try:
        conteudo = carrega_vars()
        return conteudo['gratuidade']
    except:
        return -1

def dinheiro():
    try:
        conteudo = carrega_vars()
        return conteudo['dinheiro']
    except:
        return -1

# Carrega tensao de entrada
def tensao_entrada():
    try:
        conteudo = carrega_vars()
        return conteudo['tensor_entrada']
    except:
        return -1

def grava_mensagem(valor):
    time.sleep(0.001)
    conteudo = carrega_mensagem()
    conteudo['mensagem'] = valor

    try:
        with open(path_mensagem, "w") as saida:
            json.dump(conteudo, saida)
    except:
        pass

    time.sleep(0.001)

# Determina mensagem para a placa
def mensagem_padrao():
    grava_mensagem("CA000EZ")

