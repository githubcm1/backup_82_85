import threading
import requests

import sys
sys.path.insert(1, '/home/pi/caixa-magica/core/')
import db
import funcoes_logs
import funcoes_viagem
import funcoes_elastic

from datetime import datetime
from time import sleep
import json
import numpy as np
import os
import gc

import threading
import operacoes

conn = db.Conexao()
global GLOBAL_RESULTADOS
GLOBAL_RESULTADOS = []
global GLOBAL_CONTAS
GLOBAL_CONTAS = []
global GLOBAL_NOME
GLOBAL_NOME = []
global GLOBAL_DATA
GLOBAL_DATA = []

global GLOBAL_PARTICOES
global tabela

import pathlib
path_atual = "/home/pi/caixa-magica/core"

local = 'rec_facial.py'

funcoes_logs.insere_log("Iniciando " + local, local,2)

global linhaId
linhaId = funcoes_viagem.get_linha_atual()

# Rotina que obtem as particoes faciais, de acordo com um range especificado
def obtemParticoesFacial(MIN_FACIAL, MAX_FACIAL, tabela):
    try:
        #connlocal = db.Conexao()
        dados=(str(MIN_FACIAL), str(MAX_FACIAL), tabela, str(MAX_FACIAL), tabela,)
        sql = """select particao num
             from facial_range_contas
             where contaid_de >= %s
               and contaid_ate <= %s
               and tabela = %s
             union
             select particao from facial_range_contas
             where %s between contaid_de and contaid_ate
               and tabela = %s"""
        print("query inicia particoes")
        result = conn.consultarComBind(sql,dados)
        print("query final particoes")

        return result
    except:
        return

def obtemParticoes(tabela):
    global GLOBAL_PARTICOES
    GLOBAL_PARTICOES=[]

    funcoes_logs.insere_log("Usando tabela " + tabela + " para reconhecimento facial: ", local, 2)

    MIN_FACIAL = -10000000
    MAX_FACIAL =  10000000
    LASTRO_MIN_MAX_FACIAL = 20000
    saida = ""
    leitura_facial_completa = False

    # Obtem os minimos e maximos para as particoes
    try:
        path_arq = '/home/pi/caixa-magica-operacao/min_max_facial.json'
        path_arq_linha = ""

        if "_linha_" in tabela:
            path_arq_linha = '/home/pi/caixa-magica-operacao/min_max_facial_'+tabela+'.json'

        if path_arq_linha != "":
            try:
                with open(path_arq_linha) as json_data:
                    auxData = json.load(json_data)
                MIN_FACIAL = auxData['minFacial'] - LASTRO_MIN_MAX_FACIAL
                MAX_FACIAL = auxData['maxFacial'] + LASTRO_MIN_MAX_FACIAL
            except:
                leitura_facial_completa = True
        else:
            leitura_facial_completa = True

        if leitura_facial_completa:
            with open(path_arq) as json_data:
                auxData = json.load(json_data)
            MIN_FACIAL = auxData['minFacial'] - LASTRO_MIN_MAX_FACIAL
            MAX_FACIAL = auxData['maxFacial'] + LASTRO_MIN_MAX_FACIAL
    except Exception as e:
        funcoes_logs.insere_log("Erro ao abrir min_max_facial.json: " + str(e), local, 3)

    funcoes_logs.insere_log("Consultando particoes da tabela " + tabela +" no range de contas de " + str(MIN_FACIAL) + " a " + str(MAX_FACIAL), local, 2)
    num = 0
    result = obtemParticoesFacial(MIN_FACIAL, MAX_FACIAL, tabela)

    for row in result:
        GLOBAL_PARTICOES.append(row[0])
        num = num + 1
    funcoes_logs.insere_log("Particoes obtidas tabela " + tabela +": " + str(num), local, 2)

    return num

def execDistanciaEuclidiana(i, var_tabela, metricas, limite_regs = 1):
    # Se chegou aqui, a tabela existe. Assim, realizar a consulta
    data = ([metricas])
    try:
        sql = """select data<->cube(%s) as dist, conta, nome, data
		FROM """ + var_tabela + """ 
		ORDER BY dist
		limit """ + str(limite_regs)
        c = conn.consultarComBind(sql,data)
        #connLocal.fechar()
    
        for row in c:
            GLOBAL_RESULTADOS.append(row[0])
            GLOBAL_CONTAS.append(row[1])
            GLOBAL_NOME.append(row[2])
            GLOBAL_DATA.append("s")
    except Exception as e:
        funcoes_logs.insere_log("Erro Calculo Distancia Euclidiana: " + str(e), local, 3)
    return ""

# Metodo para reconhecimento facial
# Logica: checa na tabela de reconhecimento facial da linha. Se nao encontrar, tenta na tabela facial principal
def get_user(metricas):
    global tabela

    try:
        tabela = determinaTabelaFacialViagem()

        # Se a tabela identificada ja for a principal
        if tabela == 'facial':
            consulta_apenas_principal = True
        else:
            consulta_apenas_principal = False

        # Se a consulta for na tabela de linha
        if not consulta_apenas_principal:
            retorno = get_user_tabela(metricas, tabela)

            # Se o retorno veio vazio, tentamos a tabela facial principal
            if retorno == "" or len(retorno) <= 0:
                tabela = 'facial'
                retorno = get_user_tabela(metricas, tabela)

            # Mas se o retorno ocorreu
            else:
                rate = operacoes.get_rate(retorno[0])
                        
                # Se o resultado nao foi satisfatorio, chamamos a metrica da tabela principal
                if rate != 1:
                    tabela = 'facial'
                    retorno = get_user_tabela(metricas, tabela)

        # Se a consulta nao for na tabela de linha
        else:
            funcoes_logs.insere_log("Consultando direto na tabela " + tabela, local, 2)
            retorno = get_user_tabela(metricas, tabela)
    except Exception as e:
        retorno = ""
        funcoes_logs.insere_log("Erro em get_user() " + str(e), local, 3)

    return retorno

# Efetua o reconheicmento facial usando a tabela principal de faces ou na de linhas
def get_user_tabela(metricas,tabela):
    global GLOBAL_RESULTADOS
    global GLOBAL_NOME
    global GLOBAL_CONTAS
    global GLOBAL_DATA
    GLOBAL_RESULTADOS = []
    GLOBAL_NOME = []
    GLOBAL_CONTAS = []
    GLOBAL_DATA = []
    NUM_THREADS = 300
    TIMEOUT_THREAD = 5

    inicio = str(datetime.now())

    threads=[]

    i = 0
    num_threads = obtemParticoes(tabela)

    while i < num_threads:
        t = threading.Thread(target=execDistanciaEuclidiana, args=(i,GLOBAL_PARTICOES[i], metricas))
        t.start()
        threads.append(t)

        while threading.activeCount() >= NUM_THREADS:
            sleep(0.00001)
        i = i+1

    for thread in threads:
        thread.join(TIMEOUT_THREAD)

    # Obtemos o indice do menor valor encontrado
    try:
        arr = np.array(GLOBAL_RESULTADOS)
        min_indice = arr.argmin()
    
        retorno = [[GLOBAL_NOME[min_indice], GLOBAL_CONTAS[min_indice], float(GLOBAL_RESULTADOS[min_indice]), GLOBAL_DATA[min_indice]]]
    except Exception as e:
        funcoes_logs.insere_log("Erro consulta na tabela " + tabela + ": " + (str(e)), local, 3)
        retorno = []

    gc.collect()
    return retorno

# Rotina que identifica a tabela de consulta para reconhecimento facial, de acordo com a viagem em curso
def determinaTabelaFacialViagem():
    #return 'facial'
    global tabela
    global linhaId
    tabela = ""
    
    #return 'facial'

    while True:
        try:
            if linhaId != "":
                tabela = 'facial_linha_' + str(linhaId)
        except Exception as e:
            funcoes_logs.insere_log("Erro obter linha atual: " + str(e), local, 3)

        # Se houve retorno de uma linha, devemos checar se essa tabela ja consta criada em sistema.
        # Se nao estiver criada, usamos a tabela facial completa
        if tabela != "":
            usa_tabela_linha = False

            conn1 = db.Conexao()
            dados=(str(tabela),)
            sql = "select 1 from tabelas_criadas_facial where tabela = %s"
            result = conn1.consultarComBind(sql,dados)

            for row in result:
                usa_tabela_linha = True

            # Se nao consta a tabela, entao usemos a tabela facial padrao
            if not usa_tabela_linha:
                tabela = ""

        if tabela == "":
            linhaId = ""
            tabela = 'facial'
        
        return tabela

def atualizaFacialLinhas(conta):
    #connLocal =db.Conexao()
    sql = """
/* Rotina para atualizacao do usuario em todas as linhas (quando ocorre uma atualizacao do registro facial) */
do
$do$
declare 
  reg_facial facial%rowtype;
  reg_tabelas pg_catalog.pg_tables%rowtype;
  stmt varchar(1000);
  v_conta int8 := """ + conta +""";
begin
  for reg_facial in
  	(
		select id, nome, data, conta, dateinsert, dateupdate 
		from facial where conta= v_conta  	
  	) loop
  	  /* para cada tabela facial, incluimos o registro*/
  	  for reg_tabelas in
  	  (
		SELECT *
		FROM pg_catalog.pg_tables p
		where p.schemaname = 'public'
		  and p.tablename like 'facial_linha_%'  	  
  	  ) loop 
  	  	/* Inserimos na tabela de linha, ou atualizamos o registro existente */
  	  	begin
  	       stmt := concat('update ', reg_tabelas.tablename, ' set nome = ''', reg_facial.nome, ''', data=''', reg_facial.data, ''', dateupdate=now() where conta = ', reg_facial.conta, ';');
  	       execute stmt;
  	    exception
  	       when others then null;
  	    end;
  	  end loop;
  end loop;
end;
$do$"""
    conn.manipular(sql)

def insereFacialLinha(conta, linha):
    #connLocal = db.Conexao()
    sql  ="""
/* Rotina para adicao do usuario na linha, apos um reconhecimento facial realizado*/
do
$do$
declare 
  reg_facial facial%rowtype;
  reg_tabelas pg_catalog.pg_tables%rowtype;
  stmt varchar(1000);
  v_conta int8 := """ + conta + """;
  v_linha int8:= """ + linha + """;
begin
  for reg_facial in
  	(
		select id, nome, data, conta, dateinsert, dateupdate 
		from facial where conta= v_conta  	
  	) loop
  	  /* para cada tabela facial, incluimos o registro*/
  	  for reg_tabelas in
  	  (
		SELECT *
		FROM pg_catalog.pg_tables p
		where p.schemaname = 'public'
		  and p.tablename = concat('facial_linha_', v_linha)  	  
  	  ) loop 
  	  	/* Inserimos na tabela de linha, ou atualizamos o registro existente */
  	  	begin
  	       stmt := concat('insert into ', reg_tabelas.tablename, ' (nome, data, conta, dateinsert)
  	    		    values (''', reg_facial.nome, ''', ''', reg_facial.data, ''',', reg_facial.conta, ', now())
  	    		 on conflict (conta) do 
  	    		 update set nome = ''', reg_facial.nome, ''', data=''', reg_facial.data, ''', dateupdate=now();');
  	       execute stmt;
  	    exception
  	       when others then null;
  	    end;
  	  end loop;
  end loop;
end;
$do$"""
    conn.manipular(sql)


