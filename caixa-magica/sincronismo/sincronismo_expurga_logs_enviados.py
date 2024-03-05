import os
import time

import sys
import pathlib
import json

path_atual = "/home/pi/caixa-magica/sincronismo"
path = path_atual + '/../'

sys.path.insert(1, path + '/core/')
import funcoes_logs

TEMPO_ATUALIZACAO = 60 * 24
URL_SHELLHUB = ""

local = 'sincronismo_expurga_logs_enviados.py'

funcoes_logs.insere_log("Iniciando " + local, local)

try:
    funcoes_logs.insere_log("Abrindo config.json", local)
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        
        try:
            TEMPO_ATUALIZACAO = conf['intervalo_expurga_logs_enviados']
        except:
            pass
except Exception as e:
    funcoes_logs.insere_log("Erro abrir config.json: "+ str(e), local)

funcoes_logs.insere_log("Tempo de atualizacao da rotina expurgo logs: " + str(TEMPO_ATUALIZACAO), local)

while True:
    funcoes_logs.insere_log("Iniciando expurgo de logs", local)

    try:
        funcoes_logs.expurga_logs_enviados(local)
        funcoes_logs.expurga_logs_legados(local)
    except Exception as e:
        funcoes_logs.insere_log("Erro expurgo logs: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao expurgo logs em " + str(TEMPO_ATUALIZACAO) + " segundos",local)
    time.sleep(TEMPO_ATUALIZACAO)

