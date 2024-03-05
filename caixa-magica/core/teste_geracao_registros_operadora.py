import os
from datetime import datetime
import random

operadora_id = 1 

path = "/home/pi/caixa-magica-bulk/"
os.system("sudo mkdir -p " + path)

prefixo_arquivo = "lista_operadora_" + str(operadora_id) + ".txt"
prefixo_tar = prefixo_arquivo + ".tar.gz"
path_arq = path + prefixo_arquivo
path_arq_tar = path + prefixo_tar

cnt = 1
limite = 200001

print(datetime.utcnow())

# Eliminando arquivo tar gz gerado previamente
print("Eliminando tar.gz")
comando = "sudo rm -f " + path_arq_tar
os.system(comando)

print("Gerando txt")
with open(path_arq, "w") as f:
    # Cria a primeira linha sendo o cabecalho
    registro = 'IDCONTA|NOME|MATRIZ|ATIVO|SALDO|SALDOESTUDANTE|BLOQUEADO|TEMGRATUIDADE|ESTUDANTE|TEMDIREITOACOMPANHANTE|ACOMPANHANTE|REGRABENEFICIOID|LASTUPDATE' + "\n"
    f.write(registro)

    while cnt <= limite:
        nome = "PESSOA_" + str(cnt)

        cnt_matriz = 1
        limite_matriz = 128
        matriz = ""
        while cnt_matriz <= limite_matriz:
            matriz = matriz + str(cnt_matriz) + ","
            cnt_matriz = cnt_matriz+1
        matriz = matriz[0:len(matriz)-1]

        registro = str(cnt) + "|" + nome + "|" + matriz + "|" + "true" + "|" + "10.99" + "|" + "0.78" + "|" + "true" + "|" + "true" + "|" + "true" + "|" + "true" + "|" + "true" + "|" + "1" + "|" + "2023-01-20T15:09:47.000+00:00" + "\n" 
        f.write(registro)
        cnt = cnt +1

print("gerando tar.gz")
comando = "cd " + path + " && sudo tar -czvf " + prefixo_tar + " " + prefixo_arquivo
os.system(comando)

print("eliminando txt")
comando = "sudo rm -f " + path_arq
#os.system(comando)

print(datetime.utcnow())

