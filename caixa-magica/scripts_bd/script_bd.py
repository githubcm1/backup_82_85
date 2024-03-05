# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/scripts_bd"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual + "/../core/")

# Do diretorio local "core" importa o arquivo "funcoes_logs.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/funcoes_logs.py
# import funcoes_logs

# Importa a biblioteca padrao do Python "subprocess" (criacao de novos processos conectados ao processo pai para entrada/saida de dados).
# import subprocess

# Da biblioteca padrao do Python "subprocess" importa apenas o valor especial "PIPE".
# from subprocess import PIPE

# Define o nome deste script, para impressao na tela do terminal.
# local = 'script_bd.py'

# Se há um parametro de drop das tabelas, devera ser executado o script de drop cascade das tabelas
# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Se a chamada deste script tiver um argumento de valor "drop" ("python3 script_bd.py drop")
    if sys.argv[1] == "drop":
        # Executa o script Python que dropa as tabelas do banco de dados PostgreSQL local.
        # Caminho do script: /home/pi/caixa-magica/scripts_bd/script_bd_drop.py
        os.system("sudo python3 " + path_atual + "/script_bd_drop.py")
# Se houve algum erro na execucao do script Python que dropa as tabelas do banco de dados PostgreSQL local...
except:
    # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
    # ser substituido por outra instrucao futuramente.
    pass

# Executa o script Python que cria as tabelas do banco de dados PostgreSQL local.
# Caminho do script: /home/pi/caixa-magica/scripts_bd/script_bd_tabelas.py
os.system("sudo python3 " + path_atual + "/script_bd_tabelas.py")

# Executa o script Python que criar os indices e chaves estrangeiras no banco de dados PostgreSQL local.
# Caminho do script: /home/pi/caixa-magica/scripts_bd/script_bd_indices.py
os.system("sudo python3 " + path_atual + "/script_bd_indices.py")
