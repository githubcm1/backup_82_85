import sys
path = "/home/pi/caixa-magica/core/"

sys.path.insert(1, path)
import db
import json
from time import sleep
from datetime import datetime

INTERVALO = 60 * 6
ACAO = 'EXPURGA_LOGS_INTEGRACAO'
INTERVALO_EXPURGO = 7

try:
    with open(path + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        INTERVALO = aux['intervalo_expurga_logs_integracao']
        INTERVALO_EXPURGO = aux['intervalo_dias_expurga_logs_integracao']
except Exception as e:
    print(str(e))
    pass

conn = db.Conexao()

while 1:
    EXECUTA = True
    now = datetime.utcnow()
    data = now.strftime("%Y%m%d")
    
    sql = "select 1 from controle_execucoes_diarias where acao = %s and data_acao = %s"
    dados = (ACAO, data, )
    result = conn.consultarComBind(sql, dados)

    for row in result:
        EXECUTA = False

    if EXECUTA:
        try:
            sql = "delete from log_integracao_viagem where datalog < now() - interval '" + str(INTERVALO_EXPURGO) + " days';"
            conn.manipular(sql)
        except Exception as e:
            print(str(e))
            pass

        try:
            sql = "delete from log_integracao_cobranca where datalog < now() - interval '" + str(INTERVALO_EXPURGO) + " days';"
            conn.manipular(sql)
        except Exception as e:
            print(str(e))
            pass

        try:
            sql = "delete from log_integracao_viagem_sentido_motorista where datalog < now() - interval '" + str(INTERVALO_EXPURGO) + " days';"
            conn.manipular(sql)
        except Exception as e:
            print(str(e))
            pass

        try:
            sql = "insert into controle_execucoes_diarias (acao, data_acao) values (%s, %s)"
            conn.manipularComBind(sql, dados)
        except:
            pass
    sleep(INTERVALO)
