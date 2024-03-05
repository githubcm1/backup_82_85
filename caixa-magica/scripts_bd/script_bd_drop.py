# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/scripts_bd"

# Insere nos paths do sistema o path do diretorio "core" local.
sys.path.insert(1, path_atual + "/../core/")

# Do diretorio local "core" importa o arquivo "db.py".
import db

# Atribui o nome deste script a variavel "local".
local = 'script_bd_drop.py'

# Abre uma conexao com o banco de dados PostgreSQL local e atribui uma referencia a ela a variavel "conn".
conn = db.Conexao()

# Para cada argumento passado para o script na chamada do mesmo...
for row in sys.argv:
    # Inicialmente, indica que nao deve manter as tabelas de contas no banco de dados.
    MANTEM_CONTAS = False

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Se o argumento passado for "--mantem_contas=S" ("python3 script_bd_drop.py --mantem_contas=S")
        if row == "--mantem_contas=S":
            # Indica que deve manter as tabelas de contas no banco de dados.
            MANTEM_CONTAS = True
    # Se houve algum erro na leiura do argumento passado para o script...
    except:
        # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
        # ser substituido por outra instrucao futuramente.
        pass

# Se indicou que deve manter as tabelas de contas no banco de dados...
if MANTEM_CONTAS:
    # Define a "extensao" da query "drop table" para nao considerar as tabelas "contas", "saldo", "contas_controle_saldo",
    # "facial" nem nenhuma tabela com nome iniciado em "facial_linha_".
    sql_ext = """ and p.tablename not in('contas', 'saldo', 'contas_controle_saldo', 'facial')
                  and p.tablename not like 'facial_linha_%' """
# Se indicou que nao deve manter as tabelas de contas no banco de dados...
else:
    # Define a "extensao" da query "drop table" com valor vazio.
    sql_ext = ""

# Define a query que retorna o nome das tabelas e correspondente instrucao SQL de "drop table" do banco de dados
# PostgreSQL local, do schema "public" e que nao seja a tabela "logs" e, caso assim informado,
# nao seja uma tabela de contas.
sql = """SELECT p.tablename, concat('drop table ', p.schemaname, '."', p.tablename, '" cascade;') comando
FROM pg_catalog.pg_tables p 
where p.schemaname = 'public'
  and p.tablename not in('logs') """ + sql_ext + """
order by 1 desc"""

# Executa a query acima e armazena o resultset na variavel "c".
c = conn.consultar(sql)

# Se o resultset retornado acima tiver algum registro...
if len(c) > 0:
    # Para cada registro retornado...
    for row in c:
        # Abre uma nova conexao com o banco de dados PostgreSQL local.
        conn1 = db.Conexao()

        # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
        try:
            # Atribui a instrucao SQL "drop table" a variavel "sqldrop".
            sqldrop = row[1]

            # Executa a instrucao SQL "drop table" no banco de dados.
            conn1.manipular(row[1])
        
        # Se houve algum erro na execucao da instrucao SQL "drop table"...
        except Exception as e:
            # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
            # ser substituido por outra instrucao futuramente.
            pass

        # Exclui a variavel de conexao com o banco de dados PostegreSQL local. 
        del conn1

