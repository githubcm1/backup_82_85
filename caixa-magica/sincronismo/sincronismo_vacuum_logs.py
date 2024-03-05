from datetime import datetime
import time
import os
import sys
sys.path.insert(1,'/home/pi/caixa-magica/core/')

import db
import json

conn = db.Conexao()

try:
    with open("/home/pi/caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        HORARIO_PERMITIDO = aux['horario_utc_vacuum_logs']
except:
    HORARIO_PERMITIDO = 6 # 06 UTC, 3h da manha no horario de Brasilia

INTERVALO_EXEC = 600

while True:
    now = datetime.utcnow()
    horario_atual = int(now.strftime("%H"))
    data_atual = now.strftime("%Y%m%d")

    executa = False

    if horario_atual == HORARIO_PERMITIDO:
        executa = True

        sql = "select 1 from controle_execucoes_diarias where data_acao=%s and acao='VACUUM_LOGS'"
        dados = (data_atual, )
        result = conn.consultarComBind(sql, dados)

        for row in result:
            executa = False
            break

        if not executa:
            time.sleep(INTERVALO_EXEC) # de hora em hora
            continue

        # Primeiro, criamos a tabela logs_vacuum
        sql = "drop table if exists logs_vacuum"
        conn.manipular(sql)

        sql = "create table if not exists logs_vacuum as select * from logs where 1=0"
        conn.manipular(sql)

        # Movemos os registros de logs atuais pra tabela auxiliar
        sql = "insert into logs_vacuum select * from logs"
        conn.manipular(sql)

        # Truncamos a tabela oficial
        sql = "truncate table logs"
        conn.manipular(sql)

        # reinserimos na tabela oficial
        sql = "insert into logs select * from logs_vacuum on conflict (id) do nothing"
        conn.manipular(sql)

        # removemos a tabela
        sql = "drop table if exists logs_vacuum"
        conn.manipular(sql)

        sql = "insert into controle_execucoes_diarias(data_acao, acao) values (%s, %s)"
        dados = (data_atual, 'VACUUM_LOGS')
        conn.manipularComBind(sql, dados)

        print("Finalizado vacuum em " + str(datetime.utcnow()))

    time.sleep(INTERVALO_EXEC)

