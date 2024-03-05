import os
from time import sleep
from datetime import datetime

import sys
import pathlib
path_atual = "/home/pi/caixa-magica"

path_atual = path_atual + "/core/"
sys.path.insert(1,path_atual)

import db
import funcoes_logs

DIR_LOGS = "/home/pi/caixa-magica-logs/"

local='comprime_logs.py'

funcoes_logs.insere_log("Iniciando " + local, local, 2)

funcoes_logs.insere_log("Efetuando conexao com BD", local, 2)
conn = db.Conexao()

NOVA_TENTATIVA = 1800

while True:
    try:
        funcoes_logs.insere_log("Efetuando looping checagem compressao logs", local, 2)

        horarioatual = int(datetime.utcnow().strftime("%H"))
        dataatual = str(datetime.utcnow().strftime("%Y%m%d"))
        FILENAME = DIR_LOGS + dataatual + "_logs.tar.gz"

        # Checamos se existe um log da presente data
        sql = "select count(*) existe from controle_comprime_logs where data_acao = %s"
        data = (dataatual,)
        result = conn.consultarComBind(sql, data)
        ja_existe = 0

        for row in result:
            ja_existe = row[0]
        
        funcoes_logs.insere_log("Registros da data atual em controle_comprime_logs: " + str(ja_existe), local, 2)

        # Se nao existe, efetuamos a compressao (desde que esteja num intervalo de horario valido)
        if (ja_existe == 0 and horarioatual >= 5 and horarioatual <= 7):
            funcoes_logs.insere_log("Efetuando compressao dos logs existentes", local, 2)
            os.system("sudo tar -czvf " + FILENAME + " " + DIR_LOGS + "*.log")

            funcoes_logs.insere_log("Removendo arquivos de log existentes", local, 2)
            os.system("sudo rm -rf " + DIR_LOGS + "*.log")

            funcoes_logs.insere_log("Registrando controle da compactacao na data atual", local,2)
            sql = "insert into controle_comprime_logs (data_acao, path_file) values (%s, %s)"
            data = (dataatual, FILENAME,)
            conn.manipularComBind(sql, data)
        else:
            funcoes_logs.insere_log("Fora da janela de compressao. Saindo.", local, 2)

        # Roda o mesmo procedimento dentro de 1h
        funcoes_logs.insere_log("Rodando novamente em " + str(NOVA_TENTATIVA) + " segundos", local, 2)
        sleep(NOVA_TENTATIVA)
    except:
        funcoes_logs.insere_log("Tentando novamente em " + str(NOVA_TENTATIVA) + " minutos", local, 3)
        sleep(NOVA_TENTATIVA)
