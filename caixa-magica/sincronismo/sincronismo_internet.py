import sys

import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"
sys.path.insert(1, path_atual + "/../core/")
import funcoes_temperatura
import funcoes_internet

import db
import datetime
from datetime import datetime
import time
import os

import subprocess as sp

TEMPO_ATUALIZACAO = 15

conn1=db.Conexao()
local = 'sincronismo_internet.py'

# Looping ao iniciar a aplicacao
while True:
    funcoes_temperatura.holdProcessTemperature(local)

    status_online = "OFFLINE"
    now = datetime.utcnow().isoformat()

    #cria tabela de historico 
    try:
        conn1.manipular("create table if not exists historico_internet (id serial not null, datahorautc timestamp, status varchar(10))")
    except:
        print("Tabela historico_internet ja existe")

    # Expurga informacoes da tabela historico internet apos 5 dias
    try:
        conn1.manipular("delete from historico_internet where datahorautc < ((now() - interval '5 days') at time zone 'utc')")
    except:
        print("Erro ao deletar da tabela historico_internet")

    try:
        # Obtemos o resultado do ping
        resultado_ping = sp.getoutput("ping -c 1 www.google.com")

        # Se o resultado do ping apresentou 0% de perda de pacote, entao esta ONLINE
        if (resultado_ping.find("0% packet loss") > -1
            or
            resultado_ping.find("0% perda") > -1):
            status_online = "ONLINE"
    except:
        status_online = "OFFLINE"

    funcoes_internet.atualiza_status_internet(status_online)

    # Efetua a insercao do registro
    try:
        dados=(now, str(status_online), )
        conn1.manipularComBind("insert into historico_internet (datahorautc, status) values(%s, %s)", dados)
    except:
        print("Erro ao inserir na tabela historico_internet")

    # Executa novamente o looping apos alguns segundos
    time.sleep(TEMPO_ATUALIZACAO)
