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

TEMPO_ATUALIZACAO = 60 * 30
URL_SHELLHUB = ""

local = 'sincronismo_gera_arq_log_unico.py'

funcoes_logs.insere_log("Iniciando sincronismo_gera_arq_log_unico.py", local)

try:
    funcoes_logs.insere_log("Abrindo config.json", local)
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        
        try:
            TEMPO_ATUALIZACAO = conf['intervalo_gera_arqs_logs']
        except:
            pass
except Exception as e:
    funcoes_logs.insere_log("Erro abrir config.json: "+ str(e), local)

funcoes_logs.insere_log("Tempo de atualizacao da rotina gera_arq_log_unico: " + str(TEMPO_ATUALIZACAO), local)

while True:
    time.sleep(TEMPO_ATUALIZACAO)
    funcoes_logs.insere_log("Iniciando geracao arquivo de log unico", local)

    try:
        funcoes_logs.gera_arq_log_unico(local)
    except Exception as e:
        funcoes_logs.insere_log("Erro gera_arq_log_unico: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao gera_arq_log_unico em " + str(TEMPO_ATUALIZACAO) + " segundos",local)

