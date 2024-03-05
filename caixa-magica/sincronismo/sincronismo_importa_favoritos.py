from time import sleep
import json
import requests
from datetime import datetime

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"

sys.path.insert(1, path_atual + "/../core/")
import db
import funcoes_logs
import funcoes_temperatura
import endpoints

TEMPO_ATUALIZACAO = 1200
INTERVALO_DIAS = 7
TIMEOUT_REQUESTS = 15

local = 'sincronismo_importa_favoritos.py'

# Abre arquivo de configuracao, para checagem do tempo de sincronismo aplicado para esta rotina
with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
    aux = json.load(json_data)
    try:
        TEMPO_ATUALIZACAO = aux['tempo_atualizacao_recebe_favoritos']
    except:
        pass

    try:
        INTERVALO_DIAS = aux['intervalo_dias_check_linhas_favoritos']
    except:
        pass

    try:
        TIMEOUT_REQUESTS = aux['timeout_requests']
    except:
        pass

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    horario_atual = int(datetime.now().strftime("%H"))

    # Buscamos o horario de atualizacao dentro do arquivo de configuracao
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        try:
            HORARIO_ATUALIZACAO_DE = aux['horario_atualizacao_de_recebe_favoritos']
            HORARIO_ATUALIZACAO_ATE = aux['horario_atualizacao_ate_recebe_favoritos']
        except:
            HORARIO_ATUALIZACAO_DE = 2
            HORARIO_ATUALIZACAO_ATE = 4

    prossegue = False
    if horario_atual >= HORARIO_ATUALIZACAO_DE and horario_atual <= HORARIO_ATUALIZACAO_ATE:
        prossegue = True

    if not prossegue:
        print("Fora do horario de execucao")
        sleep(TEMPO_ATUALIZACAO)
        continue
        
    base_url = endpoints.urlbase

    # Abrimos uma conexao com o banco de dados
    connLocal = db.Conexao()

    # Buscamos linhas que tiveram viagens nos ultimos dias neste onibus
    sql = """select l.id 
from linhas l
where exists 
(
	select 1
	from viagem v 
	where v.dateinsert between ((now() at time zone 'utc') - interval '""" + str(INTERVALO_DIAS) + """ days') and (now() at time zone 'utc')
	  and v.linha_id  = l.id
)
  and l.ativa =true"""
    result = connLocal.consultar(sql)
    del connLocal

    # Para cada linha
    for row in result:
        try:
            url = base_url + "LinhaContaFavorito/linhaId?linhaId="+ str(row[0])

            tabela = 'facial_linha_' + str(row[0])

            # Consultamos o web service que retorna a lista de favoritos
            # Parametro de entrada deve ser sempre o id da linha
            r = requests.get(url, timeout=TIMEOUT_REQUESTS)

            if r.ok:
                retorno = r.json()
            else:
                retorno = []

            if len(retorno) > 0:
                for rowretorno in retorno:
                    contaId = str(rowretorno['contaId'])

                    # A partir do ID da conta, inserimos na tabela de favoritos da linha
                    connLocal = db.Conexao()
                    dados=(str(contaId), str(contaId), )
                    sql = """insert into """ + tabela + """ (nome, data, conta, dateinsert)
                            select c.nome, f.data, c.id_web, now() at time zone 'utc'
                            from contas c,
  	                         facial f
                            where c.id_web =%s
                              and f.conta  = c.id_web 
                              and f.data is not null
                         on conflict (conta) do 
                         update set dateupdate=now() at time zone 'utc',
                                    data = (select f1.data from facial f1 where f1.conta=%s)"""
                    connLocal.manipularComBind(sql, dados)
                    del connLocal

        except Exception as e:
            print(str(e))

    sleep(TEMPO_ATUALIZACAO)
