import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo/"
sys.path.insert(1, path_atual + '/../core/')
import funcoes_viagem
import funcoes_temperatura

import db
import os
import time
import json

conn = db.Conexao()

DIR_FILE = path_atual + "/../../caixa-magica-operacao/"
FILE_TEMP = DIR_FILE + "min_max_facial_tmp.json"
FILE = DIR_FILE + "min_max_facial.json"

local = 'sincronismo_min_max_facial.py'

# Primeiro, removemos todos os conteudos de ranges
os.system("sudo rm -rf " + DIR_FILE + "min_max_facial*")

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    try:
        # Obtem o minimo e maximo dos ids de reconhecimento facial
        sql = "select coalesce(min(id_web),0) min_id, coalesce(max(id_web),0) max_id from contas"

        MIN_ID = 0
        MAX_ID = 0
        result = conn.consultar(sql)

        for row in result:
            MIN_ID = row[0]
            MAX_ID = row[1]

            os.system("sudo touch " + FILE_TEMP)
            with open(FILE_TEMP, "w") as json_data:
                json_data.write('{"minFacial":' + str(MIN_ID) + ', "maxFacial":' + str(MAX_ID) + '}')
    
            # trocamos o arquivo oficial (usado pelas rotinas de reconhecimento facial)
            os.system("sudo mv "+ FILE_TEMP + " " + FILE)
            os.system("sudo rm -rf " + FILE_TEMP)
    except:
        pass

    # Faz o mapeio dos minimos e maximos da tabela de linha da viagem corrente
    linhaId = funcoes_viagem.get_linha_atual()

    # Obtemos as linhas que existem dentro desta Caixa Magica
    sql = "select id from linhas where 1=1 and ativa = true "

    if linhaId == "" or linhaId == None:
        sql = sql
    else:
        sql = sql + " and id = " +str( linhaId )
    resultLinha = conn.consultar(sql)

    # para cada linha
    for rowLinha in resultLinha:
        linhaId = rowLinha[0]

        FILE_TEMP_LINHA = DIR_FILE + "min_max_facial_tmp_facial_linha_"+str(linhaId)+".json"
        FILE_LINHA = DIR_FILE + "min_max_facial_facial_linha_"+str(linhaId)+".json"

        connLocal = db.Conexao()
        try:
            sql = "select coalesce(min(conta),0) min_id, coalesce(max(conta),0) max_id from facial_linha_" + str(linhaId)
            result = connLocal.consultar(sql)

            for row in result:
                MIN_ID_LINHA = row[0]
                MAX_ID_LINHA = row[1]

                os.system("sudo touch " + FILE_TEMP_LINHA)
                with open(FILE_TEMP_LINHA, "w") as json_data:
                    json_data.write('{"minFacial":' + str(MIN_ID_LINHA) + ', "maxFacial":' + str(MAX_ID_LINHA) + '}')

                # trocamos o arquivo oficial (usado pelas rotinas de reconhecimento facial)
                os.system("sudo mv "+ FILE_TEMP_LINHA + " " + FILE_LINHA)
                os.system("sudo rm -rf " + FILE_TEMP_LINHA)
        # Neste caso, geramos o arquivo de linhas com os mesmos ranges do arquivo principal
        except:
            MIN_ID_LINHA = MIN_ID
            MAX_ID_LINHA = MAX_ID

            os.system("sudo touch " + FILE_TEMP_LINHA)
            with open(FILE_TEMP_LINHA, "w") as json_data:
                json_data.write('{"minFacial":' + str(MIN_ID_LINHA) + ', "maxFacial":' + str(MAX_ID_LINHA) + '}')

                # trocamos o arquivo oficial (usado pelas rotinas de reconhecimento facial)
            os.system("sudo mv "+ FILE_TEMP_LINHA + " " + FILE_LINHA)
            os.system("sudo rm -rf " + FILE_TEMP_LINHA)
            

        del connLocal

    time.sleep(300) # sincroniza a cada 5 minutos (evitando sobrecarga pelo tamanho da tabela)
