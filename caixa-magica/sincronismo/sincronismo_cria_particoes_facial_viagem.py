import os
import time
import json

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"

path_atual = path_atual+ '/../scripts_bd/'

sys.path.insert(1, path_atual)
from script_bd_cria_particoes_facial import cria_facial

sys.path.insert(2, path_atual + "/../core")
import funcoes_logs
import db
import funcoes_viagem
import funcoes_temperatura

from datetime import datetime

local = 'sincronismo_cria_particoes_facial_viagem.py'

funcoes_logs.insere_log("Iniciando " + local, local)

TEMPO_ATUALIZACAO = 600

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    hora = int(datetime.now().strftime("%H%M"))
    viagem_aberta = False

    # Nesta janela de processamento, executa a criacao das particoes de TODAS as LINHAS
    if hora >= 2330 and hora <= 2340:
        os.system("sudo python3 " + path_atual + "/../sincronismo/sincronismo_cria_particoes_todas_linhas.py")
        time.sleep(TEMPO_ATUALIZACAO)
        continue

    print("Passando proceso checagem normal")

    # Trecho modificado por Fernando Andre de Almeida
    # Consideramos a linha ativa que estiver na tabela local "viagem"
    linhaId = funcoes_viagem.get_linha_atual()
   
    # Buscamos as linhas
    conn = db.Conexao()

    sql = "select id from linhas where ativa=true"

    # Se existe uma viagem aberta, fazemos a acao apenas na linha em questao
    if linhaId != "" and linhaId != None:
        sql = sql + " and id = " + str(linhaId)
        result = conn.consultar(sql)
        del conn
    else:
        del conn
        continue

    cria_controle_facial = False
    for row in result:
        print("Criando tabeça facial da Linha: " + str(id))
        funcoes_logs.insere_log("Criando tabela para linha ID: " + str(row[0]), local)
        cria_facial(row[0])
        funcoes_logs.insere_log("Encerrado processo de criacao tabela para linha ID " + str(row[0]), local)
        cria_controle_facial = True

    funcoes_logs.insere_log("Nova checagem em " + str(TEMPO_ATUALIZACAO), local)
    time.sleep(TEMPO_ATUALIZACAO)

