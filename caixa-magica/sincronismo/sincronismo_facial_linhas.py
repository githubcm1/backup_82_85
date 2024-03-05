import sys
import threading
import time
import json

sys.path.insert(1, '/home/pi/caixa-magica/core')
import db
import funcoes_elastic

try:
    with open('/home/pi/caixa-magica-vars/config.json') as fil:
        aux = json.load(fil)
        PROXIMA_INTERACAO = aux['intervalo_merge_facial_linhas']
except Exception as e:
    PROXIMA_INTERACAO = 300

conn = db.Conexao()
#PROXIMA_INTERACAO = 5

while True:
    try:
        # Lista todos os registros de contas que estao na fila de atualizacao nas filas
        sql = "select id, contaid from facial_fila_linhas order by 1 limit 500"
        result = conn.consultar(sql)

        for row in result:
            contaId = row[1]
            funcoes_elastic.copia_matriz_facial_linhas(contaId)

            # Remove da fila
            sql = "delete from facial_fila_linhas where id = %s"
            dados = (row[0],)
            conn.manipularComBind(sql, dados)
    except:
        pass

    time.sleep(PROXIMA_INTERACAO)
