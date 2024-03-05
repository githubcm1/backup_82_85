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
        HORARIO_PERMITIDO = aux['horario_truncate_historico_geoloc']
except:
    HORARIO_PERMITIDO = 6 # 06 UTC, 3h da manha no horario de Brasilia

INTERVALO_EXEC = 600

while True:
    now = datetime.utcnow()
    horario_atual = int(now.strftime("%H"))
    data_atual = now.strftime("%Y%m%d")
    print(horario_atual)

    executa = False

    if horario_atual == HORARIO_PERMITIDO:
        executa = True

        sql = "select 1 from controle_execucoes_diarias where data_acao=%s and acao='VACUUM_GEOLOC'"
        dados = (data_atual, )
        result = conn.consultarComBind(sql, dados)

        for row in result:
            executa = False
            break

        if not executa:
            time.sleep(INTERVALO_EXEC) # de hora em hora
            continue

        # truncamos a tabela
        sql = "delete from historico_geoloc"
        conn.manipular(sql)

        sql = "vacuum historico_geoloc"
        conn.manipular(sql)

        sql = "insert into controle_execucoes_diarias(data_acao, acao) values (%s, %s)"
        dados = (data_atual, 'VACUUM_GEOLOC')
        conn.manipularComBind(sql, dados)

        print("Finalizado vacuum em " + str(datetime.utcnow()))

    time.sleep(INTERVALO_EXEC)

