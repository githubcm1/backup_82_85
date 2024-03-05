from datetime import datetime
import time

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"
sys.path.insert(1, path_atual + "/../core/")
import db
import funcoes_logs
import funcoes_temperatura

local ='sincronismo_gera_saldo_base_contas.py' 

funcoes_logs.insere_log("Iniciando " + local, local)

saldo_sumario_base = 0

conn = db.Conexao()

TEMPO_REFRESH = 600
HORARIO_INICIAL = '0030'
HORARIO_FINAL = '0359'

def checaDentroIntervalo():
    time_str = datetime.now().strftime("%H%M")

    if time_str >= HORARIO_INICIAL and time_str <= HORARIO_FINAL:
        funcoes_logs.insere_log("Dentro do horario permitido", local)
        return True

    funcoes_logs.insere_log("Fora do horario permitido", local)
    return False

while True:
    funcoes_logs.insere_log("Executando loop", local)

    funcoes_temperatura.holdProcessTemperature(local)

    # Checa se estamos num intervalo valido
    if checaDentroIntervalo():
        funcoes_logs.insere_log("Obtendo contas sem registro de saldo", local)

        # Pegamos contas que estejam sem um registro de saldo base
        sql = """select c.id from contas c 
where not exists 
	(
	  select 1
	  from contas_controle_saldos ccs 
	  where ccs.contaid =c.id 
	)"""
        result = conn.consultar(sql)
        funcoes_logs.insere_log("Retornado(s) " + str(len(result) ) + " registro(s)", local)

        for row in result:
            try:
                if checaDentroIntervalo():
                    funcoes_logs.insere_log("Inserindo saldo base da conta id " + str(row[0]), local)
                    conn1 = db.Conexao()

                    dados=(str(row[0]), str(saldo_sumario_base), )
                    sqlInsert = """insert into contas_controle_saldos 
                                    (contaid, saldo_sumario, dateinsert) 
                                   values (%s, %s, now() at time zone 'utc') on conflict (contaid) do nothing"""
                    conn1.manipularComBind(sqlInsert, dados)
                    del conn1
                else:
                    funcoes_logs.insere_log("Acao interrompida: fora do intervalo permitido", local)
                    break;
            except Exception as e:
                funcoes_logs.insere_log("Erro encontrado: " + str(e), local)
    else:
        funcoes_logs.insere_log("Fora do intervalo permitido", local)

    funcoes_logs.insere_log("Nova tentativa em " + str(TEMPO_REFRESH) + " segundos", local)
    time.sleep(TEMPO_REFRESH)
