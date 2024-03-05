import os
import time

import sys
import pathlib
import json

path_atual = "/home/pi/caixa-magica/sincronismo"
path = path_atual + '/../'

sys.path.insert(1, path + '/core/')
import funcoes_logs
import funcoes_qrcode
import funcoes_temperatura

TEMPO_ATUALIZACAO = 60 * 60 * 12 # A cada 12 horas
URL_SHELLHUB = ""

local = 'sincronismo_expurga_qrcodes_utilizados.py'

funcoes_logs.insere_log("Iniciando " + local, local)

try:
    funcoes_logs.insere_log("Abrindo config.json", local)
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        
        try:
            TEMPO_ATUALIZACAO = conf['intervalo_expurga_qrcodes_utilizados']
        except:
            pass
except Exception as e:
    funcoes_logs.insere_log("Erro abrir config.json: "+ str(e), local)

funcoes_logs.insere_log("Tempo de atualizacao da rotina expurgo qrcodes utilizados: " + str(TEMPO_ATUALIZACAO), local)

while True:
    funcoes_logs.insere_log("Iniciando expurgo de utilizados", local)

    funcoes_temperatura.holdProcessTemperature(local)

    try:
        funcoes_qrcode.expurga_qrcodes_utilizados()
    except Exception as e:
        funcoes_logs.insere_log("Erro expurgo qrcodes: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao expurgo qrcodes em " + str(TEMPO_ATUALIZACAO) + " segundos",local)
    time.sleep(TEMPO_ATUALIZACAO)

