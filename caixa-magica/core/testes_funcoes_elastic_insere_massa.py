import funcoes_elastic
import sys

args = sys.argv

arrAux=[]
arrElasticInsert=[]
metrica = []
valor_nome = "CARGA_TESTE"

cnt = 0
limite = 128

while cnt < limite:
    metrica.append('1')
    cnt = cnt+1

metrica = ','.join(metrica)

try:
    ini = int(args[1])
except:
    ini = 1
fim = ini + 1000000

while ini < fim:
    contaid = ini
    contaIdIndex = str(contaid) + "_1"
    doc_elastic = '{"arquivoFoto": "'+ str(contaid) + '", "contaId":"'+str(contaid)+'", "contaIdIndex": "'+contaIdIndex+'", "lastUpdate":"1900-01-01", "matrizFacial": ['+ metrica + '], "nome":"'+ valor_nome +'"}'
    arrAux=[]
    arrAux.append(doc_elastic)
    arrAux.append(contaIdIndex)
    arrAux.append(str(contaid))
    arrElasticInsert.append(arrAux)
    ini = ini+1

for reg_es in arrElasticInsert:
    chave_id = reg_es[1]
    print(chave_id)
    funcoes_elastic.insere_registro(reg_es[0], chave_id)
