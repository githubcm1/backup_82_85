from time import sleep
import json
import requests

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"

sys.path.insert(1, path_atual + "/../core/")
import db
import funcoes_logs
import threading
import rec_facial
import funcoes_temperatura
import funcoes_elastic

local= "sincronismo_cobranca_similaridade_facial.py"

funcoes_logs.insere_log("Iniciando " + local, local)

DIF_PERMITIDA = 0.18
LIMITE_REGS = 5

# abre arquivo de configuracao
try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        DIF_PERMITIDA = aux['dif_permitida_similaridade_facial']
        LIMITE_REGS = aux['limite_regs_similaridade_facial']
except:
    pass

INTERVALO = 60

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    conn = db.Conexao()

    # Para os registros que nao sao de reconhecimento facial, devemos marca-los para nao ocorrer a analise
    sql = """update cobrancas 
             set check_contas_analise = true 
             where check_contas_analise = false
               and matriz_facial is null"""
    conn.manipular(sql)
    
    # Buscamos os registros de cobranca que ainda nao tiveram checagem de reconhecimento facial similares
    sql = """select c.id, c.contaid, c.range_analise
	     from cobrancas c
	     where c.check_contas_analise = false 
  	       and c.enviada =false 
  	       and c.matriz_facial is not null limit 100"""
    result = conn.consultar(sql)

    # Para cada registro
    for row in result:
        try:
            cobrancaid = row[0]
            contaid = row[1]
            range_analise = row[2]

            dados=(str(cobrancaid),)
            sql = "delete from cobrancas_contas_analise where cobrancaid=%s"
            conn.manipularComBind(sql, dados)

            # Obtemos a matriz facial do registro de cobranca
            sql = "select matriz_facial from cobrancas where id = %s"
            dadosC = (str(cobrancaid),)
            resultM = conn.consultarComBind(sql, dadosC)
            matriz_facial = str(resultM[0]).strip()
            matriz_facial = matriz_facial[0:len(matriz_facial)-2]
            matriz_facial = str(matriz_facial).replace("(","").replace(")","").replace("'","").split(",")

            matriz_original = matriz_facial
            matriz_facial = []

            for row in matriz_original:
                matriz_facial.append(float(row))

            # Em posse da matriz, agora consultamos no Elastic Search
            resultados = funcoes_elastic.consulta_matriz_facial_thread(matriz_facial,"")
            suspeitos = []

            # Se temos resultados, entao consideramos apenas os registros cujo id nao seja da propria conta em 
            # que a cobranca ocorreu
            if len(resultados) > 0:
                for registro in resultados:
                    range_comparar = float(registro[3])
                    diferenca = (range_analise - range_comparar)
                    
                    if int(registro[0]) != contaid and (diferenca <= DIF_PERMITIDA):
                        aux =[]
                        aux.append(int(registro[0]))
                        aux.append(registro[3])
                        suspeitos.append(aux)

                        if len(suspeitos) == LIMITE_REGS:
                            break
            
            # Se existem registros proximos, inserimos na base
            ordem = 1
            for row in suspeitos:
                # Busca o nome da pessoa na propria base
                sql = "select nome from contas where id_web = %s"
                dadosN = (row[0],)
                resultN = conn.consultarComBind(sql, dadosN)

                try:
                    nome_analise = resultN[0]
                except:
                    nome_analise = ""

                sql = """insert into cobrancas_contas_analise 
                               (cobrancaid, dif_permitida, ordem, contaid_analise,
                                nome_analise, dif_obtida_analise, 
                                range_obtido, dateinsert)
                        values (%s, %s, %s, %s,
                                %s, %s, 
                                %s, now() at time zone 'utc')"""
                dados = (cobrancaid, DIF_PERMITIDA, ordem, row[0],
                         nome_analise, diferenca, 
                         row[1],)
                conn.manipularComBind(sql, dados)
                ordem = ordem + 1
        except Exception as e:
            print("Erro atualizacao cobranca id " + str(row[0]) + ": " + str(e))
            continue

        dados=(cobrancaid,)
        sql = "update cobrancas set check_contas_analise=true where id = %s"
        conn.manipularComBind(sql, dados)

    del conn
    sleep(INTERVALO)
