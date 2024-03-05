# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/scripts_bd"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual + '/../core/')

# Do diretorio local "core" importa o arquivo "db.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/db.py
import db

# Do diretorio local "core" importa o arquivo "funcoes_logs.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/funcoes_logs.py
import funcoes_logs

# Atribui o nome deste script a variavel "local".
local = 'script_bd_indices.py' 

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "Iniciando script_bd_indices" e indicando
# que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data e hora UTC atuais.
funcoes_logs.insere_log("Iniciando script_bd_indices", local)

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "Abrindo conexao com BD" e indicando
# que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data e hora UTC atuais.
funcoes_logs.insere_log("Abrindo conexao com BD", local)

# Abre uma conexao com o banco de dados PostgreSQL local.
conn = db.Conexao()

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "criando unique index em contas, campo id_web" e indicando
# que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data e hora UTC atuais.
funcoes_logs.insere_log("criando unique index em contas, campo id_web", local)

# Declara o bloco anonimo SQL para criacao do indice do tipo "b-tree" na tabela "contas" do banco de dados PostgreSQL local.
# Se o indice ja estiver criado (exception) nao e realizada nenhuma acao.
st = """DO $BLOCK$
BEGIN
    BEGIN
        CREATE UNIQUE INDEX contas_id_web_idx ON public.contas USING btree (id_web);
    EXCEPTION
        WHEN duplicate_table
        THEN null;
    END;
END;
$BLOCK$;"""

# Executa o bloco anonimo SQL declarado acima.
conn.manipular(st)

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "Criando indice tipo GIST na tabela facial 
# (para matrizes CUBE)" e indicando que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data 
# e hora UTC atuais.
# funcoes_logs.insere_log("Criando indice tipo GIST na tabela facial (para matrizes CUBE)", local)

# Declara o bloco anonimo SQL para criacao do indice do tipo "GIST" na tabela "facial" do banco de dados PostgreSQL local.
# Se o indice ja estiver criado (exception) nao e realizada nenhuma acao.
# st = """DO $BLOCK$
# BEGIN
#     BEGIN
#         CREATE INDEX facial_data_idx ON ONLY public.facial USING gist (data);
#     EXCEPTION
#         WHEN others then null;
#     END;
# END;
# $BLOCK$;"""

# Executa o bloco anonimo SQL declarado acima.
# conn.manipular(st)

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "Criando FK tabela saldo, referenciando tabela 
# contas" e indicando que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data e hora UTC atuais. 
funcoes_logs.insere_log("Criando FK tabela saldo, referenciando tabela contas", local)

# Declara o bloco anonimo SQL para criacao da chave estrangeira da tabela "saldo" que referencia o registro correspondente
# da tabela "contas" do banco de dados PostgreSQL local. Se a chave ja estiver criada (exception) nao e realizada nenhuma acao. 
st = """DO $BLOCK$
BEGIN
    BEGIN
        ALTER TABLE public.saldo ADD CONSTRAINT saldo_fk FOREIGN KEY (conta) REFERENCES public.contas(id_web);
    EXCEPTION
        WHEN others then null;
    END;
END;
$BLOCK$;"""

# Executa o bloco anonimo SQL declarado acima.
conn.manipular(st)

# Declara o bloco anonimo SQL para criacao do indice na tabela "contas" do banco de dados PostgreSQL local.
# Se o indice ja estiver criado (exception) nao e realizada nenhuma acao.
st = """DO $BLOCK$
BEGIN
    BEGIN
        CREATE INDEX contas_cpf_idx ON public.contas (cpf);
    EXCEPTION
        WHEN duplicate_table
        THEN null;
    END;
END;
$BLOCK$;"""

# Executa o bloco anonimo SQL declarado acima.
conn.manipular(st)

# Declara o bloco anonimo SQL para criacao do indice na tabela "operadores" do banco de dados PostgreSQL local.
# Se o indice ja estiver criado (exception) nao e realizada nenhuma acao.
st = """DO $BLOCK$
BEGIN
    BEGIN
        CREATE INDEX operadores_cpf_idx ON public.operadores (cpf);
    EXCEPTION
        WHEN duplicate_table
        THEN null;
    END;
END;
$BLOCK$;"""

# Executa o bloco anonimo SQL declarado acima.
conn.manipular(st)

# Insere um registro na tabela "logs" do banco de dados PostgreSQL local com o texto "Finalizando script_bd_indices.py" e indicando 
# que a acao ocorreu no script "script_bd_indices.py". Considera como data de insercao a data e hora UTC atuais.
funcoes_logs.insere_log("Finalizando script_bd_indices.py", local)
