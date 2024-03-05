# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/core"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual)

# Do diretorio local "core" importa o arquivo "funcoes_serial.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_serial.py
import funcoes_serial

# Do diretorio local "core" importa o arquivo "funcoes_logs.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_logs.py
import funcoes_logs

# Da biblioteca padrao do Python "time" importa apenas a funcao "sleep" (manipulacao de datas e horarios).
from time import sleep

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# ADICIONADO EM 08/08/2023
import os

ARQ_SAIDA_TEMPERATURA = '/home/pi/caixa-magica-operacao/temperatura_cpu.txt'
ARQ_FINAL_TEMPERATURA = '/home/pi/caixa-magica-operacao/temperatura_cpu.json'

# Verifica se esta maquina e uma Raspberry PI e atribui o valor booleano retornado pela funcao
# a variavel "isRasp".
isRasp = funcoes_serial.getRaspPI()

# Se a maquina for uma Raspberry PI...
if isRasp:
    # Da biblioteca do PyPI "gpiozero" importa apenas a classe "CPUTemperature" (inteface com dispositivos GPIO - General Purpose Input/Output).
    from gpiozero import CPUTemperature

# Funcao que retorna a temperatura da CPU da maquina em graus Celsius.
def getTemperature():
    # Se a maquina for uma Raspberry PI...
    if isRasp:
        # Cria uma instancia da classe "CPUTemperature" e atribui a variavel "cpu".
        cpu = CPUTemperature()

        # Verifica a temperatura da CPU em graus Celsius e atribui o valor a variavel "temperatura".
        temperatura = cpu.temperature
    # Se a maquina nao for uma Raspberry PI...
    else:
        # ADICIONADO EM 08/08/2023
        comando = 'sudo sensors | sudo tee ' + ARQ_SAIDA_TEMPERATURA
        os.system(comando)

        # Le o conteudo do arquivo
        with open(ARQ_SAIDA_TEMPERATURA) as f:
            aux = str(f.readlines())
        f.close()
        
        # Encontramos o trecho que contem a temperatura
        pos_ini= aux.find("Package id 0:")
        aux = aux[pos_ini:len(aux)]
        pos_fim = aux.find("°C")+2
        aux = aux[0:pos_fim]
        aux = aux.replace("Package id 0:","").strip()
        
        temperatura = float(aux.replace("°C",""))
        
        saida_json = '{"temperatura_cpu": "' + aux + '"}'
        with open(ARQ_FINAL_TEMPERATURA,"w") as f:
            f.write(saida_json)
        f.close()
    
    # Retorna a temperatura da CPU definida acima.
    return (temperatura)

# Retorna a temperatura do arquivo JSON
def getTemperatureJSON():
    try:
        with open(ARQ_FINAL_TEMPERATURA,"r") as f:
            aux = json.load(f)
            return aux['temperatura_cpu'].replace("°","")
    except:
        return ""

#print(getTemperatureJSON())

# Funcao que verifica a temperatura da CPU e, caso esteja acima do limite permitido, interrompe a execucao do sistema por um
# numero determinado de segundos.
def holdProcessTemperature(local):
    # Declara um laco while para executar as proximas instrucoes em loop infinito.
    while True:
        # Verifica a temperatura da CPU e atribui o valor a variavel "temperatura".
        temperatura = getTemperature()

        # Abre o arquivo JSON de configuracoes gerais do validador e cria uma referencia chamada "json_data" a ele.
        with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
            # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
            try:
                # Le o conteudo do arquivo JSON de configuracoes gerais do validador e atribui a variavel "aux".
                aux = json.load(json_data)

                # Atribui a variavel "limite" o valor limite de temperatura da CPU lido do arquivo JSON de configuracoes
                # gerais do validador.
                limite = aux['limite_temperatura_cpu_jobs']
            # Se ocorrer algum erro na abertura e leitura do arquivo JSON de configuracoes gerais do validador...
            except Exception as e:
                # Atribui um valor maximo "999" ao limite de temperatura da CPU.
                limite = 999

        # Se a temperatura da CPU estiver acima do limite permitido...
        if temperatura > limite:
            # Insere um registro na tabela de log do banco de dados PostgreSQL local informando que a execucao do programa esta
            # sendo interrompida por aquecimento e informa a temperatura da CPU e a temperatura limite.
            funcoes_logs.insere_log("Interrompendo " + str(local) + " por aquecimento (limite: " + str(limite) + "ºC, temp: " + str(temperatura) + "ºC", local)
            
            # Interrompe a execucao do programa por 10 segundos.
            sleep(10)

            # Insere um registro na tabela de log do banco de dados PostgreSQL local informando que a execucao do programa esta
            # sendo retomada apos aquecimento e informa a temperatura da CPU e a temperatura limite.
            funcoes_logs.insere_log("Retomando " + str(local) + " apos aquecimento (limite: " + str(limite) + "ºC, temp: " + str(temperatura) + "ºC", local)
        # Se a temperatura da CPU nao estiver acima do limite permitido...
        else:
            # Finaliza a execucao da funcao para que a verificacao da temperatura da CPU nao seja mais executada.
            return


