import os
import logging
import time

import sys
import pathlib
import json

path_atual = "/home/pi/caixa-magica/sincronismo"
path = path_atual + '/../'

sys.path.insert(1, path + '/core/')
import funcoes_logs
import funcoes_temperatura

TEMPO_ATUALIZACAO = 60 * 30
URL_SHELLHUB = ""

local = 'sincronismo_gera_arqs_logs.py'

funcoes_logs.insere_log("Iniciando sincronismo_gera_arqs_logs.py", local)

try:
    funcoes_logs.insere_log("Abrindo config.json", local)

    funcoes_temperatura.holdProcessTemperature(local)

    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        
        try:
            TEMPO_ATUALIZACAO = conf['intervalo_gera_arqs_logs']
        except:
            pass
except Exception as e:
    funcoes_logs.insere_log("Erro abrir config.json: "+ str(e), local)

funcoes_logs.insere_log("Tempo de atualizacao da rotina gera_arqs_logs: " + str(TEMPO_ATUALIZACAO), local)

while True:
    time.sleep(TEMPO_ATUALIZACAO)
    funcoes_logs.insere_log("Iniciando geracao arquivos de logs", local)

    try:
        funcoes_logs.gera_arqs_logs(local)
    except Exception as e:
        funcoes_logs.insere_log("Erro gera_arqs_logs: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao gera_arqs_logs em " + str(TEMPO_ATUALIZACAO) + " segundos",local)

