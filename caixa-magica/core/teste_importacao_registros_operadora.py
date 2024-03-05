import os
import sys
import threading
from datetime import datetime
import funcoes_elastic

def insere_contas(num_thread, lista_contas):
    print(str(datetime.utcnow()) + " Executando Thread #" + str(num_thread) + ": " + str(len(lista_contas)) )
    #return

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

            doc_elastic = '{"arquivoFoto": "'+ str(contaId) + '", "contaId":"'+str(contaId)+'", "contaIdIndex": "'+contaIdIndex+'", "lastUpdate":"'+ last_update +'", "matrizFacial": ['+ metrica + '], "nome":"'+ valor_nome +'"}'
            print(doc_elastic)
            return

            funcoes_elastic.insere_registro(doc_elastic, contaIdIndex,"",True)
        except:
            pass
    
    print(str(datetime.utcnow()) + "Terminou Thread #" + str(num_thread))

args = sys.argv
arquivo = args[1]

registros_fracionados = []
limite_por_thread = 10000

cnt=1
with open(arquivo,"r") as f:
    lines = [line.strip() for line in f]

arrAux = []
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

#aux = registros_fracionados[0]
#registros_fracionados = []
#registros_fracionados.append(aux)

#print("quebra")
#print(len(registros_fracionados))

#soma_registros = 0
#for row in registros_fracionados:
#    soma_registros = soma_registros + len(row)

#print(soma_registros)

# Para cada bloco de registros, executamos a thread de importacao
threads = []

print("Limpando memoria SWAP")
#os.system("sudo swapoff -a")
print("Limpou memoria SWAP")

print(datetime.utcnow())
num_thread = 1
for row in registros_fracionados:
    try:
        t = threading.Thread(target=insere_contas, args=(num_thread, row,))
        t.start()
    except:
        pass
    num_thread = num_thread+1

# Aguarda o encerramento de todas as threads
for thread in threads:
    thread.join()

print(datetime.utcnow())



