print("Passo 01");

# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Da biblioteca padrao do Python "time" importa apenas a funcao "sleep".
from time import sleep

# Importa a biblioteca do PyPI "requests" (envio de requisicoes HTTP).
# import requests

# Da biblioteca padrao do Python "datetime" importa apenas a classe "datetime" (manipulacao de datas e horarios).
import datetime

# Define o diretorio base para facilitar a referencia aos demais diretorios e arquivos.
path_base = "/home/pi/caixa-magica/"

# Define o caminho do arquivo JSON de parametros do Elasticsearch e armazena na variavel "json_param".
json_param = path_base + "../caixa-magica-vars/param_elastic.json"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_base + "/core")

# Do diretorio local "core" importa o arquivo "funcoes_elastic.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/funcoes_elastic.py
import funcoes_elastic

# Inicialmente, indica que nao e a primeira execucao do script.
primeira_exec = False

# Le a lista de argumentos passada para este script e grava no array "args".
args = sys.argv

# Para cada item do array de argumentos, atribui seu valor a variavel "arg".
for arg in args:
    # Se o valor do argumento que esta sendo verificado for "primeira_exec"...
    if arg == "primeira_exec":
        # Indica que e a primeira execucao do script.
        primeira_exec = True

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Abre o arquivo JSON de parametros do Elasticsearch e atribui seu conteudo a variavel "fil".
    # O parametro "r" indica que o arquivo esta sendo aberto no modo de leitura ("reading").
    with open(json_param, "r") as fil:
        # Converte o JSON de parametros do Elasticsearch em array e atribui a variavel "aux".
        aux = json.load(fil)

        # total_particoes = aux['total_particoes']
        # limite_fotos_conta = aux['limite_fotos_conta']
        
        # Define o limite, em segundos, para execucao do "health check" do Elasticsearch de acordo com o parametrizado no arquivo JSON.
        segundos_limite_start = aux['segundos_limite_start']
# Se ocorrer algum erro na leitura do arquivo JSON de parametros do Elasticsearch...
except Exception as e:
    # Finaliza a execucao da aplicacao.
    quit()

# Declara a variavel "INTERVALO_EXEC" e atribui o valor 10.
INTERVALO_EXEC = 10

# Se for a primeira execucao do script...
if primeira_exec:
    # "Retira" o limite para execucao do "health check" do Elasticsearch.
    segundos_limite_start = 9999

# Declara um laco "while" "infinito" para executar o health check do Elasticsearch periodicamente.
while 1:
    # Inicialmente, indica que o servico do Elasticsearch nao esta ativo.
    servico_ativo = False

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Busca a data e hora UTC atuais e atribui a variavel "atual".
        atual = datetime.datetime.utcnow()

        # Calcula a data e hora limites para a execucao do "health check" do Elasticsearch adicionando a data e hora
        # UTC atuais o numero de segundos definidos como limite.
        limite = atual + datetime.timedelta(seconds=segundos_limite_start)

        # Indica que e a primeira passagem pelo laco "while" do health check do Elasticsearch.
        primeiro_loop = True

        # Se a data e hora UTC atuais sao menores (anteriores) a data e hora limites para execucao do "health check" do Elasticsearch...
        while atual < limite:
            # Atualiza a data e hora UTC atuais.
            atual = datetime.datetime.utcnow()

            # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
            try:
                # Se o servico do Elasticsearch esta ativo...
                if funcoes_elastic.check_elastic_on():
                    # Indica que o servico do Elasticsearch esta ativo. 
                    servico_ativo = True
    
                    # Efetua a criacao dos indices no Elasticsearch.
                    # funcoes_elastic.cria_todos_indices(total_particoes, limite_fotos_conta)
                    funcoes_elastic.cria_todos_indices_lista()

                    # Se chegou aqui, e porque o Elasticsearch esta ativo e com os indices criados. Neste caso,
                    # iguala a data e hora limites para execucao do "health check" com a data e hora atuais para
                    # sair do laco de execucao do "health check".
                    limite = atual
            # Se houver algum erro no "health check" do Elasticsearch...
            except Exception as e:
                # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
                # ser substituido por outra instrucao futuramente.
                pass

            # Se esta for a primeira passagem pelo laco do "health check" do Elasticsearch e o servico do
            # Elasticsearch nao estiver ativo...
            if primeiro_loop and not servico_ativo:
                # Define o comando que executa o script shell, o qual inicializa o servico do Elasticsearch.
                # Caminho do script: /home/pi/caixa-magica/script_inicia_es.sh
                comando = "sudo sh " + path_base + "/script_inicia_es.sh"
                
                # Executa o comando definido acima.
                os.system(comando)

                # Imprime a mensagem "Aguardando inicializacao Elastic Search" na tela do terminal.
                print("Aguardando inicializacao Elastic Search")

                # Interrompe a execucao do script por 10 segundos, para dar tempo de inicializar o Elasticsearch
                # antes da proxima iteracao do loop do "health check".
                sleep(10)

            # Interrompe a execucao do script por 20 segundos, para dar tempo de inicializar o Elasticsearch
            # antes da proxima iteracao do loop do "health check".
            sleep(20)

            # Indica que nao e mais a primeira passagem pelo laco "while" do health check do Elasticsearch.
            primeiro_loop = False

        # Imprime a mensagem "Fim do health check" na tela do terminal.
        print("Fim do health check")
    
    # Se houve algum erro na execucao do "health check" do Elasticsearch...
    except Exception as e:
        # Imprime a mensagem de erro na tela do terminal.
        print("Erro" + str(e))

    # Se for a primeira execucao do script...
    if primeira_exec:
        # Interrompe a execucao do laco "infinito" do "health check" do Elasticsearch.
        break

    # Interrompe a execucao do script pelo numero de segundos definido em INTERVALO_EXEC antes da proxima
    # iteracao do laco "infinito" do Elasticsearch.
    sleep(INTERVALO_EXEC)
