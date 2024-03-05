import os
import time
import sys
import json

path_atual = "/home/pi/caixa-magica/sincronismo"
path = path_atual + '/../'

sys.path.insert(1, path + '/core/')
import funcoes_logs
import funcoes_temperatura

TEMPO_ATUALIZACAO = 600
URL_SHELLHUB = ""

local = 'sincronismo_adiciona_shellhub.py'

funcoes_logs.insere_log("Iniciando sincronismo_adiciona_shellhub.py", local)

try:
    funcoes_temperatura.holdProcessTemperature(local)

    funcoes_logs.insere_log("Abrindo config.json", local)
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        
        try:
            TEMPO_ATUALIZACAO = conf['intervalo_check_shellhub']
        except:
            pass
    
        try:
            URL_SHELLHUB = conf['url_shellhub']
        except:
            pass
except Exception as e:
    funcoes_logs.insere_log("Erro abrir config.json: "+ str(e), local)

funcoes_logs.insere_log("Tempo de atualizacao da rotina adicao shellhub: " + str(TEMPO_ATUALIZACAO), local)
funcoes_logs.insere_log("URL Shellhub: " + URL_SHELLHUB, local)

while True:
    funcoes_logs.insere_log("Iniciando check periodico ShellHub", local)

    if URL_SHELLHUB == "":
        funcoes_logs.insere_log("URL ShellHub nao parametrizada em config.json.", local)
    else:
        funcoes_logs.insere_log("URL ShellHub existente em config.json: " + URL_SHELLHUB, local)

    try:
        funcoes_logs.insere_log("Removendo arquivo de check shellhub", local)
        os.system("sudo rm -rf " + path + "/check_docker_shellhub.txt")

        funcoes_logs.insere_log("Recriando arquivo de check shellhub", local)
        os.system("sudo touch " + path + "/check_docker_shellhub.txt")
    
        funcoes_logs.insere_log("Checando existencia docker Shellhub", local)
        os.system("sudo docker container ls | sudo tee -a " + path + "/check_docker_shellhub.txt > /dev/null")
    
        funcoes_logs.insere_log("Abrindo arquivo para analise", local)
        f = open(path+ "/check_docker_shellhub.txt")
        aux = f.read()
        pos_pct = aux.find("shellhub")

        if pos_pct < 0:
            funcoes_logs.insere_log("Docker nao encontrado. Iniciando instalacao.", local)
        
            comando_curl = "sudo curl -sSf " + URL_SHELLHUB + " | sudo sh"

            funcoes_logs.insere_log("Instalando docker shellhub a partir do comando " + comando_curl, local)

            os.system("sudo docker stop shellhub")
            os.system("sudo docker rm shellhub")
            os.system(comando_curl)
        else:
            funcoes_logs.insere_log("Ja existe um docker de shellhub. Nao necessaria a instalacao", local)
    except Exception as e:
        funcoes_logs.insere_log("Erro: " + str(e), local)

    funcoes_logs.insere_log("Nova atualizacao adicao shellhub em " + str(TEMPO_ATUALIZACAO) + " segundos",local)
    time.sleep(TEMPO_ATUALIZACAO)

