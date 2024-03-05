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

# Buscamos as linhas
conn = db.Conexao()

sql = "select id from linhas where ativa=true"
result = conn.consultar(sql)

for row in result:
    print("Criando tabeça facial da Linha: " + str(id))
    funcoes_logs.insere_log("Criando tabela para linha ID: " + str(row[0]), local)
    cria_facial(row[0])
    funcoes_logs.insere_log("Encerrado processo de criacao tabela para linha ID " + str(row[0]), local)

