import json
import os
import sys
import threading
from datetime import datetime
import funcoes_elastic
from time import sleep

# Iniciando postgres
#comando = 'sudo python3 /home/pi/caixa-magica/start_conf_db.py'
#os.system(comando)

import db

db = db.Conexao()

def insere_contas_db(num_thread, lista_contas):
    filename = path_bulk_files + "json_thread_" + str(num_thread) + ".json"
    print(str(datetime.utcnow()) + " Executando Thread DB #" + str(num_thread) + ": " + str(len(lista_contas)) )    

    contador = 1
    lista_body = ""
    lista_body_saldos = ""
    # para cada registro
    for row in lista_contas:
        try:
            now = datetime.utcnow()
            colunas = row.split("|")
            contaIdIndex = str(colunas[0]) + "_1"
            metrica = str(colunas[2])
            contaId = colunas[0]
            valor_nome = colunas[1]
            last_update = str(now)
            ativo = str(colunas[3])
            saldo = str(colunas[4])
            saldo_estudante = str(colunas[5])
            bloqueado = str(colunas[6])
            tem_gratuidade = str(colunas[7])
            estudante = str(colunas[8])
            direitoacomp = str(colunas[9])
            acomp = str(colunas[10])
            regrabeneficioid = str(colunas[11])
            lastupdate = str(colunas[12])
            cpf = '11111111111'

            body = "(" + str(contaId) + ", '" + str(valor_nome) + "', now() at time zone 'utc', '" + bloqueado + "', '" + lastupdate + "','" +estudante  +"', '" + tem_gratuidade + "', '" + direitoacomp + "', '" + acomp + "','"+cpf+"' ),"
            lista_body = lista_body + body

            body_saldos = "(" + str(contaId) + ", " + str(saldo) + ", now() at time zone 'utc', " + str(saldo_estudante) + ", " + regrabeneficioid + "),"
            lista_body_saldos = lista_body_saldos + body_saldos

            contador = contador+1
        except:
            pass

    lista_body = lista_body[0:len(lista_body)-1]
    lista_body_saldos = lista_body_saldos[0:len(lista_body_saldos)-1]
    
    # Insere no bd na tabela de contas
    sql = "insert into contas (id_web, nome, dateinsert, bloqueado, backend_lastupdatetime, estudante, isento, pcd, acompanhante_pcd, cpf) values " + lista_body
    db.manipular(sql)

    # Insere na tabela de saldos
    sql = "insert into contas_controle_saldos (contaid, saldo_sumario, dateinsert, saldo_estudante, beneficioid) values " + lista_body_saldos
    db.manipular(sql)

    print(str(datetime.utcnow()) + "Terminou Thread DB #" + str(num_thread))

def insere_contas_facial(num_thread, lista_contas):
    filename = path_bulk_files + "json_thread_" + str(num_thread) + ".json" 
    print(str(datetime.utcnow()) + " Executando Thread #" + str(num_thread) + ": " + str(len(lista_contas)) )
    doc_elastic = ""

    contador = 1
    # para cada registro
    for row in lista_contas:
        try:
            now = datetime.utcnow()
            colunas = row.split("|")
            contaIdIndex = str(colunas[0]) + "_1"
            metrica = str(colunas[2])
            contaId = colunas[0]
            valor_nome = colunas[1]
            last_update = str(now)
            
            # Definimos o indice
            indice = funcoes_elastic.define_indice_insercao(contaIdIndex, False)

            header = '{"index": {"_index": "'+ indice +'"}}' + "\n"

            body = '{"arquivoFoto": "'+ str(contaId) + '", "contaId":"'+str(contaId)+'", "contaIdIndex": "'+contaIdIndex+'", "lastUpdate":"'+ last_update +'", "matrizFacial": ['+ metrica + '], "nome":"'+ valor_nome +'"}' + "\n"
            documento = header + body
            doc_elastic = doc_elastic + documento
            contador = contador+1
        except:
            pass
    
    with open(filename,"w") as f:
        f.write(doc_elastic)
    f.close()

    # Agora, chamamos a insercao BULK
    comando = 'sudo curl -X POST http://localhost:9200/_bulk?pretty -H "Content-Type: application/json" --data-binary "@'+filename+'"'
    os.system(comando)
    os.system("sudo rm -rf " + filename)
    print(str(datetime.utcnow()) + "Terminou Thread #" + str(num_thread))

def executa_bloco_facial(lines):
    registros_fracionados = []
    arrAux = []
    cnt = 1

    for row in lines:
        arrAux.append(row)
    
        if cnt == limite_por_thread:
            registros_fracionados.append(arrAux)
            arrAux=[]
            cnt = 1
        else:
            cnt = cnt+1

    # Se sobrou algo no array aux
    if len(arrAux) > 0:
        registros_fracionados.append(arrAux)

    # Para cada bloco de registros, executamos a thread de importacao
    threads = []

    print(datetime.utcnow())
    num_thread = 1
    limitador_threads = 5
    conta_threads = 1
    for row in registros_fracionados:
        try:
            t = threading.Thread(target=insere_contas_facial, args=(num_thread, row,))
            t.start()
            threads.append(t)

            conta_threads = conta_threads +1

            if conta_threads > limitador_threads:
                conta_threads = 1
                print("aguardando para exec da thread " + str(num_thread))

                for thread in threads:
                    thread.join()
            
                threads=[]
        except:
            pass
        num_thread = num_thread+1

    # Aguarda o encerramento de todas as threads
    for thread in threads:
        thread.join()


def executa_bloco_db(lines):
    print("Efetuando trecho BD")
    registros_fracionados = []
    arrAux = []
    cnt = 1

    for row in lines:
        arrAux.append(row)

        if cnt == limite_por_thread:
            registros_fracionados.append(arrAux)
            arrAux=[]
            cnt = 1
        else:
            cnt = cnt+1

    # Se sobrou algo no array aux
    if len(arrAux) > 0:
        registros_fracionados.append(arrAux)

    # Para cada bloco de registros, executamos a thread de importacao
    threads = []

    print(datetime.utcnow())
    num_thread = 1
    limitador_threads = 20
    conta_threads = 1
    for row in registros_fracionados:
        try:
            t = threading.Thread(target=insere_contas_db, args=(num_thread, row,))
            t.start()
            threads.append(t)

            conta_threads = conta_threads +1
            if conta_threads > limitador_threads:
                conta_threads = 1
                print("aguardando para exec da thread " + str(num_thread))

                for thread in threads:
                    thread.join()

                threads=[]
        except:
            pass
        num_thread = num_thread+1

    # Aguarda o encerramento de todas as threads
    for thread in threads:
        thread.join()

path_base = "/home/pi/caixa-magica/"
json_param = path_base + "../caixa-magica-vars/param_elastic.json"

try:
    with open(json_param,"r") as fil:
        aux = json.load(fil)
        total_particoes = aux['total_particoes']
        limite_fotos_conta = aux['limite_fotos_conta']

except Exception as e:
    print(str(e))
    quit()

data_atual = str(datetime.utcnow())
data_atual = data_atual[0:10].strip("") + "T00:00:00.000"

args = sys.argv
try:
    arquivo = args[1]
except:
    print("Arquivo nao informado.")
    quit()

# Descompacta o arquivo
path_bulk_files = "/home/pi/caixa-magica-bulk/"
comando = "sudo tar -xzvf " + arquivo + " -C " + path_bulk_files
os.system(comando)

arquivo = arquivo[0:len(arquivo)-7]


limite_por_thread = 20000

os.system("clear")

inicio = datetime.utcnow()

# Cria diretorio com lotes
path_bulk_files = "/home/pi/caixa-magica-bulk/json_temp/"
os.system("sudo mkdir -p " + path_bulk_files)
os.system("sudo rm -rf " + path_bulk_files + "*")

# Removemos os indices existentes
funcoes_elastic.remove_indices_faciais(True, True)

# efetua a criacao dos indices
funcoes_elastic.cria_todos_indices(total_particoes, limite_fotos_conta)

# Zera fila de atualizacao dos saldos
sql = "truncate table fila_atualiza_saldo cascade"
db.manipular(sql)

# Zera tabela de saldos
sql = "truncate table contas_controle_saldos cascade"
db.manipular(sql)

# Zera tabela de contas
sql = "truncate table contas cascade"
db.manipular(sql)

# Trecho facial (elastic search)
print("Iniciando carga de faces")
lines = []
cnt_linhas = 1
primeira_linha = True
limite_linhas = 1000000
with open(arquivo,"r") as f:
    for line in f:
        if primeira_linha:
            primeira_linha= False
            continue
        lines.append(line.strip())
        cnt_linhas = cnt_linhas+1

        if cnt_linhas > limite_linhas:
            executa_bloco_facial(lines)

            cnt_linhas = 1
            del lines
            lines= []

print(len(lines))
if len(lines) > 0:
    executa_bloco_facial(lines)

# Trecho do banco de dados
print("Iniciando carga de contas")
lines = []
cnt_linhas = 1
primeira_linha = True
limite_linhas = 1000000
with open(arquivo,"r") as f:
    for line in f:
        if primeira_linha:
            primeira_linha= False
            continue

        lines.append(line.strip())
        cnt_linhas = cnt_linhas+1

        if cnt_linhas > limite_linhas:
            executa_bloco_db(lines)

            cnt_linhas = 1
            del lines
            lines= []

print(len(lines))
if len(lines) > 0:
    executa_bloco_db(lines)

# Atualiza arquivo de sincronismo de contas
comando = '{\"lastSyncAtualizacao\": \"'+data_atual+'\", \"lastSyncBloq\": \"1900-01-01T00:00:00.000000\", \"lastSyncDesbloq\": \"1900-01-01T00:00:00.000000\"}'
comando = "sudo echo '" + comando + "' | tee /home/pi/caixa-magica-operacao/sincronismo.json"
os.system(comando)

# Atualiza arquivo de sincronismo facial
comando = '{\"lastUpdateTime\": \"'+data_atual+'\"}'
comando = "sudo echo '" + comando + "' | tee /home/pi/caixa-magica-operacao/sincronismo_facial.json"
os.system(comando)

termino = datetime.utcnow()
print("Iniciado: " + str(inicio))
print("Termino: " + str(termino))

