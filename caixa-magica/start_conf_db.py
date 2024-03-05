# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Importa a biblioteca padrao do Python "subprocess" (criacao de novos processos conectados ao processo pai para entrada/saida de dados).
# import subprocess

# Da biblioteca padrao do Python "subprocess" importa apenas o valor especial "PIPE".
# from subprocess import PIPE

# Importa a biblioteca padrao do Python "time" (funcoes para calculos e conversoes de tempo).
import time

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
# import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual + "/core")

# local = 'start_conf_postgresql.py'

# Define o nome deste script, para impressao na tela do terminal.
local = 'start_conf_db.py';

# Imprime na tela do terminal a mensagem de que esta iniciando a execucao deste script.
print("Iniciando " + local)

# Imprime a mensagem "Parando servico do PostgreSQL" na tela do terminal.
print("Parando servico do PostgreSQL")

# Com o usuario "postgres", executa o comando para parar o servidor do PostgreSQL que esta rodando no "data directory"
# especificado no parametro "-D". O parametro "-m" indica que o servidor sera desligado imediatamente, abortando
# todos os seus processos ativos.
os.system("sudo su postgres -c \'/usr/local/pgsql/bin/pg_ctl stop -D /usr/local/pgsql/data -m immediate\'")

# Interrompe a execucao do script por 2 segundos.
time.sleep(2)

# Imprime a mensagem "Iniciando postgre" na tela do terminal.
print("Iniciando postgre")

# Exclui o arquivo de configuracao do PostgreSQL criado no "data directory".
os.system("sudo rm -f /usr/local/pgsql/data/postgresql.conf")

# Define o comando que copia o arquivo de configuracao do PostgreSQL, do diretorio "/home/pi/caixa-magica/postgresql/"
# para o "data directory" do PostgreSQL.
comando = "sudo cp -f " + path_atual + "/postgresql/postgresql.conf /usr/local/pgsql/data/"

# Executa o comando definido acima.
os.system(comando)

# Altera o usuario e o grupo "owner" do arquivo de configuracao do PostgreSQL para "postgres". 
os.system("sudo chown postgres:postgres /usr/local/pgsql/data/postgresql.conf")

# Iniciando banco de dados
# string_postgre = "sudo su postgres -c \'/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data/ -l /home/postgres/logfile start\'"

# Define o comando que, com o usuario "postgres", executara a inicializacao do servidor do PostgreSQL para rodar no "data directory"
# especificado no parametro "-D".
string_postgre = "sudo su postgres -c \'/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data/ start\'"

# Imprime na tela do terminal a mensagem de que esta rodando o comando de inicializacao do PostgreSQL.
print("Rodando subprocesso com comando: " + string_postgre)

# Executa o comando de inicializacao do PostgreSQL.
os.system(string_postgre)

# Imprime a mensagem "Iniciado postgres" na tela do terminal.
print("Iniciado postgres")
