# Importa a biblioteca padrao do Python "time" (funcoes para calculos e conversoes de tempo).
import time

# Do diretorio local "core" importa o arquivo "db.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/db.py
from core import db

# Abre uma conexao com o banco de dados PostgreSQL local e armazena a referencia na variavel "conn".
conn = db.Conexao()

# Cria, caso ainda nao exista, a tabela auxiliar "keep_alive", utilizada para manter a aplicacao ativa.
sql = "create table if not exists keep_alive (chave int not null, tmst timestamptz, constraint keep_alive_pk primary key(chave))"

# Executa a instrucao SQL acima no banco de dados PostgreSQL local.
conn.manipular(sql)

# Inicia um laco "while" infinito, para manter a aplicacao ativa.
while True:

    # Define a instrucao SQL que insere, caso nao exista, um registro na tabela "keep_alive" com a data e hora atuais.
    # Caso o registro ja exista, atualiza esse registro com a data e hora atuais.
    sql = "insert into keep_alive (chave, tmst) values (1, now()) on conflict(chave) do update set tmst=now();"

    # Executa a instrucao SQL acima no banco de dados PostgreSQL local.
    conn.manipular(sql)

    # Interrompe a execucao do script por 4 segundos.
    time.sleep(4)

