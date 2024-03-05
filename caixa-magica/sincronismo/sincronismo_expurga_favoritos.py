import os
import time
import json

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"

sys.path.insert(2, path_atual + "/../core")
import funcoes_logs
import db
import funcoes_viagem
import funcoes_temperatura

from datetime import datetime

local = 'sincronismo_expurga_favoritos.py'

funcoes_logs.insere_log("Iniciando " + local, local)

TEMPO_ATUALIZACAO = 600

INTERVALO_DIAS_CHECK = 7

ACAO = "EXPURGA_FAVORITOS"
HORA_DE = 1
HORA_ATE = 2

with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
    aux = json.load(json_data)

    try:
        INTERVALO_DIAS_CHECK = aux['intervalo_dias_expurgo_favoritos']
    except:
        pass

    try:
        HORA_DE = aux['hora_de_expurgo_favoritos']
        HORA_ATE = aux['hora_ate_expurgo_favoritos']
    except:
        pass

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    prossegue = False
    hora = int(datetime.now().strftime("%H"))

    if hora >= HORA_DE and hora <= HORA_ATE:
        prossegue = True

    if not prossegue:
        time.sleep(TEMPO_ATUALIZACAO)
        continue

    # Checamos se a acao ja foi feita na presente data
    dataatual = str(datetime.now().strftime("%Y%m%d"))
    conn = db.Conexao()
    sql  ="select 1 from controle_execucoes_diarias where data_acao=%s and acao=%s"
    data = (dataatual, ACAO, )
    result = conn.consultarComBind(sql, data)
    del conn

    # Se chegou aqui, a acao ja foi feita. Entao, abortar
    for row in result:
        prossegue = False

    if not prossegue:
        time.sleep(TEMPO_ATUALIZACAO)
        continue
    
    conn = db.Conexao()

    # Busca as linhas existentes
    sql="""select x.tablename, 
	   trim(substring(x.linha, strpos(x.linha, '_')+1, length(x.linha) )) linha
from
(
	select pt.*, 
		   substring(pt.tablename,8,length(pt.tablename)) linha
	from pg_catalog.pg_tables pt 
	where pt.tablename like 'facial_linha_%'
	  and pt.tablename not like '%_p_%'
) x"""
    result = conn.consultar(sql)

    for row in result:
        # Checamos se existe alguma viagem criada nesta linha nos ultimos dias
        sql = """select count(*)
                 from viagem 
                 where linha_id = %s
                   and dateinsert >= now() - interval '""" + str(INTERVALO_DIAS_CHECK) + """ days'"""
        data=(row[1],)
        result_viagem = conn.consultarComBind(sql,data)

        for row_viagem in result_viagem:
            # Se o resultado foi zero, entao nao teve viagens. Neste caso, efetuar drop da tabela
            if row_viagem[0] <= 0:
                try:
                    #sql = "drop table " + row[0]
                    #conn.manipular(sql)
                
                    sql = "delete from tabelas_criadas_facial where tabela = %s"
                    data = (row[0],)
                    conn.manipularComBind(sql, data)
                except:
                    pass
            # Caso ocorreram viagens no periodo, entao devemos deletar registros que nao foram atualizados nas ultimas semanas
            # e tambem os que foram apenas inseridos a mais de x dias
            else:
                try:
                    sql = "delete from " + row[0] + " where dateupdate is not null and dateupdate < now() - Interval '" + str(INTERVALO_DIAS_CHECK) + " days'"
                    conn.manipular(sql)
                    sql = "delete from " + row[0] + " where dateupdate is null and dateinsert < now() - Interval '" + str(INTERVALO_DIAS_CHECK) + " days'"
                    conn.manipular(sql)
                except:
                    pass

    sql = "insert into controle_execucoes_diarias (data_acao, acao) values (%s, %s) on conflict (data_acao, acao) do nothing"
    data = (dataatual, ACAO, )
    conn.manipularComBind(sql, data)

    time.sleep(TEMPO_ATUALIZACAO)

