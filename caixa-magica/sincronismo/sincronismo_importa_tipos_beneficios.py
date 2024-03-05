import os
import time

import sys
import pathlib
import json
from datetime import datetime

path_atual = "/home/pi/caixa-magica/sincronismo"
path = path_atual + '/../'

sys.path.insert(1, path + '/core/')
import funcoes_logs
import funcoes_temperatura

TEMPO_ATUALIZACAO = 60
HORARIO_INICIO = 2
HORARIO_TERMINO = 4
URL_SHELLHUB = ""

local = 'sincronismo_importa_tipos_beneficios.py'

funcoes_logs.insere_log("Iniciando " + local, local)

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    hora = int(datetime.now().strftime("%H"))

    try:
        funcoes_logs.expurga_logs_enviados(local)
    except Exception as e:
        funcoes_logs.insere_log("Erro expurgo logs: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao expurgo logs em " + str(TEMPO_ATUALIZACAO) + " segundos",local)
    time.sleep(TEMPO_ATUALIZACAO)

