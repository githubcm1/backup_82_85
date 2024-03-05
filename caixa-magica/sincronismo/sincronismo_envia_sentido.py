import json
from time import sleep
import sys
import pathlib

path_atual = '/home/pi/caixa-magica/sincronismo/'
path_atual = path_atual + "/../core/"
sys.path.insert(1, path_atual)

import funcoes_temperatura
import funcoes_viagem
import funcoes_logs

local = 'sincronismo_envia_sentido.py'

# Obtemos a configuracao de atualizacao
TEMPO_ATUALIZACAO = 30
try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        TEMPO_ATUALIZACAO = aux['tempo_atualizacao_envio_sentido_backend']
except:
    pass

funcoes_logs.insere_log("Iniciando " + local, local)

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    try:
        funcoes_logs.insere_log("Enviando registros de sentido", local)
        funcoes_viagem.enviaSentidoViagemSemIntegr()
    except Exception as e:
        funcoes_logs.insere_log("Erro envio registros de sentido: " + str(e), local)

    funcoes_logs.insere_log("Enviando novamente registros de sentido em " + str(TEMPO_ATUALIZACAO), local)
    sleep(TEMPO_ATUALIZACAO)

