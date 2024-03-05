from datetime import datetime
from datetime import date
import json
import time
import os

import sys
sys.path.insert(1,'/home/pi/caixa-magica/core/')
import db


INTERVALO_EXEC = 60 * 30 # Checa a possibilidade a cada 30 minutos

try:
    with open('/home/pi/caixa-magica-vars/config.json') as json_data:
        aux = json.load(json_data)
        vacuum_full_dias_semana = aux['vacuum_full_dias_semana']
        arrVacuumDias = vacuum_full_dias_semana.split(",")

        vacuum_full_horario_utc_exec = aux['vacuum_full_horario_utc_exec']
except:
    print("Sem parametros para processo de datas de vacuum")
    quit()

# Se nao temos parametros de horario nem data, entao
# abortamos
if str(vacuum_full_horario_utc_exec) == '' or len(arrVacuumDias) <= 0:
    print("Intervalos nao configurados em config.json. Procedimento vacuum nao sera efetuado.")
    quit()

conn = db.Conexao()

while True:
    # Pegamos o dia corrente
    hoje = datetime.today()
    dia_semana = hoje.weekday()

    # Para efeitos de conversao, o Python trabalha com dias considerando:
    # sEGUNDA = 0; Domingo = 6
    # Iremos aqui, para facilitar, entender que DOMINGO = 1 e Sabado =7
    if dia_semana == 6: # Domingo
        dia_semana = 1
    elif dia_semana == 0: # Segunda
        dia_semana = 2
    elif dia_semana == 1: # terca
        dia_semana = 3
    elif dia_semana == 2: #quarta
        dia_semana=4
    elif dia_semana == 3: # quinta
        dia_semana = 5
    elif dia_semana ==  4: # sexta
        dia_semana = 6
    elif dia_semana == 5: # sabado
        dia_semana = 7

    try:
        cnt = 0
        permite_vacuum = False

        while cnt < len(vacuum_full_dias_semana):
            # Se estamos no mesmo dia da semana permitido
            if str(vacuum_full_dias_semana[cnt]) == str(dia_semana):
                # Se estamos no mesmo intervalo horario permitido
                now = datetime.utcnow()
                hora_atual = now.strftime("%H")

                if int(hora_atual) == int(vacuum_full_horario_utc_exec):
                    # Checamose se rotina já rodou na base de dados hoje
                    data_atual = now.strftime("%Y%m%d")
                    sql = "select count(*) from controle_execucoes_diarias where acao = 'VACUUM_FULL' and data_acao=%s"
                    dados=(data_atual,)
                    resultCED = conn.consultarComBind(sql, dados)

                    for rowCED in resultCED:
                        if rowCED[0] <= 0:
                            permite_vacuum = True
                cnt = len(vacuum_full_dias_semana)
            cnt = cnt + 1

        print(permite_vacuum)

        # se permite o vaccum
        if permite_vacuum:
            # Primeiro, matamos os processos python e/ou pyconcrete que estejam agendados
            comando = """sudo ps -aef | grep python3 | grep -v sincronismo_vacuum_full_semana | awk '{print $2}'| while read pid
                         do
                         sudo kill -9 $pid
                         done
                      """
            os.system(comando)

            comando = """sudo ps -aef | grep pyconcrete | grep -v sincronismo_vacuum_full_semana | awk '{print $2}'| while read pid
                         do
                         sudo kill -9 $pid
                         done
                      """
            os.system(comando)

            comando = """sudo ps -aef | grep start_monitor | grep -v sincronismo_vacuum_full_semana | awk '{print $2}'| while read pid
                         do
                         sudo kill -9 $pid
                         done
                      """
            os.system(comando)

            sql = "select pg.tablename from pg_tables pg where schemaname='public' order by 1"
            result = conn.consultar(sql)

            for row in result:
                now = datetime.utcnow()

                print(str(now) + " - Efetuando vacuum da tabela " + str(row[0]))
                sql = "vacuum full " + str(row[0])
                conn.manipular(sql)
    
                # Inserimos na tabela de controle de execuoes diarias
                sql = "insert into controle_execucoes_diarias (acao, data_acao) values ('VACUUM_FULL', %s)"
                dados=(data_atual,)
                conn.manipularComBind(sql, dados)

                now = datetime.utcnow()
                print(str(now) + " - Finalizado vacuum da tabela " + str(row[0]))

            # Por fim, efetuamos o reboot da maquina
            comando = "sudo reboot -f"
            os.system(comando)
    except Exception as e:
        print(str(e))
        pass

    time.sleep(INTERVALO_EXEC)
