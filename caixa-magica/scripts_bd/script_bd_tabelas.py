# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/scripts_bd"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual + "/../core/")

# Do diretorio local "core" importa o arquivo "db.py".
import db

# Atribui o nome deste script a variavel "local".
# local = 'script_bd_tabelas.py'

# Abre uma conexao com o banco de dados PostgreSQL local.
conn = db.Conexao()

################################################################################################################
# Tabela "logs"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "logs".
statement = """create table if not exists public.logs (
  id bigserial not null,
  string_log varchar(4000) not null,
  local varchar(1000) not null,
  dateinsert timestamptz not null,
  constraint logs_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "arq_log_exportado" da tabela "logs".
statement = "alter table public.logs add if not exists arq_log_exportado varchar(1000);"

# Executa a instrucao SQL de adicao da coluna "arq_log_exportado" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "arq_log_exportado_unico" da tabela "logs".
statement = "alter table public.logs add if not exists arq_log_exportado_unico varchar(1000);"

# Executa a instrucao SQL de adicao da coluna "arq_log_exportado_unico" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "data_envio_servidor" da tabela "logs".
statement = "alter table public.logs add if not exists data_envio_servidor timestamptz;"

# Executa a instrucao SQL de adicao da coluna "data_envio_servidor" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "severidade" da tabela "logs".
statement = "alter table public.logs add if not exists severidade int default 0;"

# Executa a instrucao SQL de adicao da coluna "severidade" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "data_envio_servidor" da tabela "logs" de "timestamptz" para "timestamp".
statement = "alter table public.logs alter column data_envio_servidor type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "data_envio_servidor" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "logs" de "timestamptz" para "timestamp".
statement="alter table public.logs alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "logs".
conn.manipular(statement)

# Define a instrucao SQL que define um valor padrao para a coluna "dateinsert" da tabela "logs".
statement = "alter table only public.logs alter column dateinsert set default (now() at time zone 'utc');"

# Executa a instrucao SQL de definicao do valor padrao da coluna "dateinsert" da tabela "logs".
conn.manipular(statement)

################################################################################################################
# Tabela "caixa_magica"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "caixa_magica".
statement = """create table if not exists public.caixa_magica (
  caixamagica_serial varchar(40) null
);"""

# Executa a instrucao SQL de criacao da tabela "caixa_magica".
conn.manipular(statement)

################################################################################################################
# Tabela "contas_faces_inativas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "contas_faces_inativas".
# statement = """create table if not exists public.contas_faces_inativas (
#   contaid int8 not null,
#   id_foto varchar(20) not null,
#   dateinsert timestamp null default timezone('utc'::text, now()),
#   constraint contas_faces_inativas_key unique(id_foto)
# );"""

# Executa a instrucao SQL de criacao da tabela "contas_faces_inativas".
# conn.manipular(statement)

################################################################################################################
# Tabela "contas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "contas".
statement = """create table if not exists public.contas (
  id bigserial not null,
  id_web int8 not null,
  cpf varchar null,
  nome varchar null,
  dateinsert timestamp null default timezone('utc'::text, now()),
  dateupdate timestamp null,
  bloqueado bool null default false,
  databloqueiostatus timestamptz(0) null,
  constraint contas_guid_key unique (id_web),
  constraint contas_pkey primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "isento" da tabela "contas".
statement = "alter table public.contas add if not exists isento boolean default false;"

# Executa a instrucao SQL de adicao da coluna "isento" da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "pcd" da tabela "contas".
statement = "alter table public.contas add if not exists pcd boolean default false;"

# Executa a instrucao SQL de adicao da coluna "pcd" da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "acompanhante_pcd" da tabela "contas".
statement = "alter table public.contas add if not exists acompanhante_pcd boolean default false;"

# Executa a instrucao SQL de adicao da coluna "acompanhante_pcd" da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "estudante" da tabela "contas".
statement = "alter table public.contas add if not exists estudante boolean default false;"

# Executa a instrucao SQL de adicao da coluna "estudante" da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "contra_check_facial" da tabela "contas".
statement = "alter table public.contas add if not exists contra_check_facial boolean default false;"

# Executa a instrucao SQL de adicao da coluna "contra_check_facial" da tabela "contas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "backend_lastupdatetime" da tabela "contas".
statement = "alter table public.contas add if not exists backend_lastupdatetime varchar(30);"

# Executa a instrucao SQL de adicao da coluna "backend_lastupdatetime" da tabela "contas".
conn.manipular(statement)

################################################################################################################
# Tabela "beneficios"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "beneficios".
statement = """create table if not exists public.beneficios (
  id serial not null,
  id_atribuicao int8 null,
  nomebeneficio varchar null,
  tipodesconto varchar null,
  valordesconto float4 null,
  periodos varchar null,
  conta int8 null,
  dateinsert timestamptz(0) null,
  dateupdate timestamptz(0) null,
  constraint beneficios_pkey primary key (id),
  constraint beneficios_un unique (id_atribuicao)
);"""

# Executa a instrucao SQL de criacao da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que dropa a tabela "beneficios".
statement = "drop table if exists public.beneficios;"

# Executa a instrucao SQL de exclusao da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que recria a tabela "beneficios".
statement = """create table if not exists public.beneficios (
  id bigint not null,
  nome varchar(200),
  ativo boolean default true,
  validode timestamptz not null,
  validoate timestamptz not null,
  percentual float default 100,
  valorfixo float default 0,
  constraint beneficios_pk primary key(id)
);"""

# Executa a instrucao SQL de recriacao da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "marcadoativo" da tabela "beneficios".
statement = "alter table public.beneficios add if not exists marcadoativo boolean default true;"

# Executa a instrucao SQL de adicao da coluna "marcadoativo" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateinsert" da tabela "beneficios".
statement = "alter table public.beneficios add if not exists dateinsert timestamptz default now();"

# Executa a instrucao SQL de adicao da coluna "dateinsert" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateupdate" da tabela "beneficios".
statement = "alter table public.beneficios add if not exists dateupdate timestamptz;"

# Executa a instrucao SQL de adicao da coluna "dateupdate" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "validode" da tabela "beneficios" de "timestamptz" para "timestamp".
statement = "alter table public.beneficios alter column validode type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "validode" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "validoate" da tabela "beneficios" de "timestamptz" para "timestamp".
statement = "alter table public.beneficios alter column validoate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "validoate" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "beneficios" de "timestamptz" para "timestamp".
statement = "alter table public.beneficios alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que define um valor padrao para a coluna "dateinsert" da tabela "beneficios".
statement = "alter table public.beneficios alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "beneficios".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateupdate" da tabela "beneficios" de "timestamptz" para "timestamp".
statement = "alter table public.beneficios alter column dateupdate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateupdate" da tabela "beneficios".
conn.manipular(statement)

################################################################################################################
# Tabela "cartao"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "cartao".
statement = """create table if not exists public.cartao (
  id_web int8 not null,
  numero varchar not null,
  conta int8 not null,
  dateinsert timestamp null default timezone('utc'::text, now()),
  dateupdate timestamp null,
  constraint cartao_un unique (id_web),
  constraint cartao_un2 unique (numero)
);"""

# Executa a instrucao SQL de criacao da tabela "cartao".
conn.manipular(statement)

# Define a instrucao SQL que dropa a tabela "cartao".
statement = "drop table if exists public.cartao;"

# Executa a instrucao SQL de exclusao da tabela "cartao".
conn.manipular(statement)

################################################################################################################
# Tabela "historico_internet"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "historico_internet".
statement = """create table if not exists public.historico_internet (
  id serial not null,
  datahorautc timestamp null,
  status varchar(10) null,
  datahoraenviado timestamp null,
  enviado bool null default false
);"""

# Executa a instrucao SQL de criacao da tabela "historico_internet".
conn.manipular(statement)

################################################################################################################
# Tabela "itinerario_viagem"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "itinerario_viagem".
statement = """create table if not exists public.itinerario_viagem (
  id bigserial not null,
  registroviagemid int8 not null,
  pontoid int8 not null,
  linhaid int8 not null,
  ordem int4 not null,
  sentidovolta bool null,
  geolocalizacao varchar(100) null,
  nome varchar(200) null,
  descricao varchar(200) null,
  bairro varchar(200) null,
  cidade varchar(200) null,
  uf varchar(10) null,
  cep varchar(20) null,
  logradouro varchar(200) null,
  numero varchar(100) null,
  datainsercao timestamptz(0) null default timezone('utc'::text, now()),
  constraint itinerario_viagem_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "itinerario_viagem".
conn.manipular(statement)

################################################################################################################
# Tabela "operadores"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "operadores".
statement = """create table if not exists public.operadores (
  id bigserial not null,
  id_web int8 not null,
  nome varchar(1000) not null,
  """"data"""" varchar null,
  id_qr varchar null,
  matricula varchar(30) null,
  remover boolean default true,
  dateinsert timestamp null default timezone('utc'::text, now()),
  dateupdate timestamp null default timezone('utc'::text, now()),
  constraint operadores_uk unique (id_web),
  constraint operadores_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "fiscal" a tabela "operadores".
statement = "alter table public.operadores add if not exists fiscal boolean default false;"

# Executa a instrucao SQL de adicao da coluna "fiscal" a tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "manutencao" a tabela "operadores".
statement = "alter table public.operadores add if not exists manutencao boolean default false;"

# Executa a instrucao SQL de adicao da coluna "manutencao" a tabela "operadores".
conn.manipular(statement)

# Insere um registro padrao na tabela "operadores".
statement = """insert into public.operadores(id_web, nome, id_qr, matricula, remover, fiscal, manutencao) 
               values(0,'FISCAL', '123456', 'INDEFINIDA', false, false, true)
               on conflict(id_web) do update set fiscal = false, manutencao = true;"""

# Executa a instrucao SQL de insercao de registro padrao na tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "fiscal" a tabela "operadores".
# statement = "alter table public.operadores add if not exists fiscal boolean default false;"

# Executa a instrucao SQL de adicao da coluna "fiscal" a tabela "operadores".
# conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "cpf" a tabela "operadores".
statement = "alter table public.operadores add if not exists cpf varchar(20);"

# Executa a instrucao SQL de adicao da coluna "cpf" a tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "backend_lastupdatetime" a tabela "operadores".
statement = "alter table public.operadores add if not exists backend_lastupdatetime varchar(30);"

# Executa a instrucao SQL de adicao da coluna "backend_lastupdatetime" a tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "operadores".
statement = "alter table public.operadores alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "operadores".
statement = "alter table public.operadores alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateupdate" da tabela "operadores".
statement = "alter table public.operadores alter column dateupdate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateupdate" da tabela "operadores".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateupdate" da tabela "operadores".
statement = "alter table public.operadores alter column dateupdate set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateupdate" da tabela "operadores".
conn.manipular(statement)

################################################################################################################
# Tabela "saldo"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "saldo".
statement = """create table if not exists public.saldo (
  id serial not null,
  id_web int8 not null,
  porvalor bool not null,
  conta int8 not null,
  bloqueado bool not null,
  dateinsert timestamp null default timezone('utc'::text, now()),
  dateupdate timestamp null default timezone('utc'::text, now()),
  constraint saldo_pk primary key (id),
  constraint saldo_un unique (id_web)
);"""

# Executa a instrucao SQL de criacao da tabela "saldo".
conn.manipular(statement)

################################################################################################################
# Tabela "sentido_viagem"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "sentido_viagem".
statement = """create table if not exists public.sentido_viagem (
  id bigserial not null,
  registroviagemid int8 not null,
  dataregistro timestamptz(0) not null default timezone('utc'::text, now()),
  sentido varchar(10) null,
  constraint sentido_viagem_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "sentido_viagem".
conn.manipular(statement)

################################################################################################################
# Tabela "cobrancas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "cobrancas".
statement = """create table if not exists public.cobrancas (
  id bigserial not null,
  valor float4 null,
  datahora varchar not null,
  tipopagamento varchar not null,
  tipoidentificacao int4 not null,
  fotousuario varchar null,
  enviada bool not null,
  saldo int8 null,
  beneficio int8 null,
  viagemid varchar(200) not null,
  geolocalizacao varchar null,
  datahorafalhaintegr timestamptz null,
  status_internet varchar(10) null,
  datahoraenviada timestamp null,
  constraint cobrancas_pkey primary key (id),
  /*constraint cobrancas_fk foreign key (beneficio) references public.beneficios(id_atribuicao),
*/ constraint cobrancas_saldo foreign key (saldo) references public.saldo(id_web)
);"""

# Executa a instrucao SQL de criacao da tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "chavecobranca" a tabela "cobrancas".
statement = "alter table public.cobrancas add column if not exists chavecobranca varchar(100);"

# Executa a instrucao SQL de adicao da coluna "chavecobranca" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "sentido" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists sentido varchar(100) default 'IDA';"

# Executa a instrucao SQL de adicao da coluna "sentido" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "isento" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists isento boolean default false;"

# Executa a instrucao SQL de adicao da coluna "isento" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "chave_qr_code_utilizado" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists chave_qr_code_utilizado varchar(1000);"

# Executa a instrucao SQL de adicao da coluna "chave_qr_code_utilizado" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "contaid" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists contaid int8;"

# Executa a instrucao SQL de adicao da coluna "contaid" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se existir, dropa a coluna "saldo" da tabela "cobrancas".
statement = "alter table public.cobrancas drop if exists saldo;"

# Executa a instrucao SQL de exclusao da coluna "saldo" da tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se existir, dropa a coluna "beneficio" da tabela "cobrancas".
statement = "alter table public.cobrancas drop if exists beneficio;"

# Executa a instrucao SQL de exclusao da coluna "beneficio" da tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se existir, dropa a coluna "matriz_facial" da tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists matriz_facial cube;"

# Executa a instrucao SQL de adicao da coluna "matriz_facial" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "range_analise" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists range_analise float;"

# Executa a instrucao SQL de adicao da coluna "range_analise" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "check_contas_analise" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists check_contas_analise boolean default false;"

# Executa a instrucao SQL de adicao da coluna "check_contas_analise" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "pcd" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists pcd boolean default false;"

# Executa a instrucao SQL de adicao da coluna "pcd" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "acompanhante_pcd" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists acompanhante_pcd boolean default false;"

# Executa a instrucao SQL de adicao da coluna "acompanhante_pcd" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "isento_acompanhante_pcd" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists isento_acompanhante_pcd boolean default false;"

# Executa a instrucao SQL de adicao da coluna "isento_acompanhante_pcd" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "contapcdid" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists contapcdid int8;"

# Executa a instrucao SQL de adicao da coluna "contapcdid" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "saldo_anterior_catraca" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists saldo_anterior_catraca decimal default 0;"

# Executa a instrucao SQL de adicao da coluna "saldo_anterior_catraca" a tabela "cobrancas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "saldo_apos_catraca" a tabela "cobrancas".
statement = "alter table public.cobrancas add if not exists saldo_apos_catraca decimal default 0;"

# Executa a instrucao SQL de adicao da coluna "saldo_apos_catraca" a tabela "cobrancas".
conn.manipular(statement)

################################################################################################################
# Tabela "controle_comprime_logs"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "controle_comprime_logs".
statement = """create table if not exists public.controle_comprime_logs (
  id serial not null,
  data_acao varchar(8) not null,
  path_file varchar(200) not null,
  constraint controle_comprime_logs_pk primary key (id),
  constraint controle_comprime_logs_uk unique (data_acao)
);"""

# Executa a instrucao SQL de criacao da tabela "controle_comprime_logs".
conn.manipular(statement)

################################################################################################################
# Tabela "qrcodes_utilizados"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "qrcodes_utilizados".
statement = """create table if not exists public.qrcodes_utilizados (
  id bigserial not null,
  qrcode varchar(4000) not null,
  dateinsert timestamptz not null,
  constraint qrcodes_utilizados_pk primary key (id),
  constraint qrcodes_utilizados_uk unique (qrcode)
);"""

# Executa a instrucao SQL de criacao da tabela "qrcodes_utilizados".
conn.manipular(statement)

################################################################################################################
# Tabela "linhas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "linhas".
statement = """create table if not exists public.linhas (
  id int8 not null,
  nome varchar(300),
  codigo varchar(10),
  codigopublico varchar(10),
  valor_tarifa float,
  ativa boolean default true,
  constraint linhas_pk primary key(id)
);"""

# Executa a instrucao SQL de criacao da tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateinsert" a tabela "linhas".
statement = "alter table public.linhas add if not exists dateinsert timestamptz default timezone('utc'::text, now());"

# Executa a instrucao SQL de adicao da coluna "dateinsert" a tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateupdate" a tabela "linhas".
statement = "alter table public.linhas add if not exists dateupdate timestamptz;"

# Executa a instrucao SQL de adicao da coluna "dateupdate" a tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "marcardelete" a tabela "linhas".
statement = "alter table public.linhas add if not exists marcardelete boolean default false;"

# Executa a instrucao SQL de adicao da coluna "marcardelete" a tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "linhas".
statement = "alter table public.linhas alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "linhas".
statement = "alter table public.linhas alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateupdate" da tabela "linhas".
statement = "alter table public.linhas alter column dateupdate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateupdate" da tabela "linhas".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateupdate" da tabela "linhas".
statement = "alter table public.linhas alter column dateupdate set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateupdate" da tabela "linhas".
conn.manipular(statement)

################################################################################################################
# Tabela "linhas_horarios"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "linhas_horarios".
statement = """create table if not exists public.linhas_horarios (
  id int8 not null,
  linha_id int8 not null,
  diasemana int,
  horario timestamp,
  ativo boolean default true,
  constraint linhas_horarios_pk primary key(id)
);"""

# Executa a instrucao SQL de criacao da tabela "linhas_horarios".
conn.manipular(statement)

################################################################################################################
# Tabela "viagem_sentido_motorista"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "viagem_sentido_motorista".
statement = """create table if not exists public.viagem_sentido_motorista (
  id bigserial not null,
  id_viagem_cm varchar(100) not null,
  codigolinha varchar(30) not null,
  motoristaid int8 not null,
  dateinsert timestamptz(0) DEFAULT timezone('utc'::text, now()),
  constraint viagem_sentido_motorista_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "viagem_sentido_motorista".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "sentido" a tabela "viagem_sentido_motorista".
statement = "alter table public.viagem_sentido_motorista add if not exists sentido int;"

# Executa a instrucao SQL de adicao da coluna "sentido" a tabela "viagem_sentido_motorista".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateenviadobackend" a tabela "viagem_sentido_motorista".
statement = "alter table public.viagem_sentido_motorista add if not exists dateenviadobackend timestamptz;"

# Executa a instrucao SQL de adicao da coluna "dateenviadobackend" a tabela "viagem_sentido_motorista".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "geolocalizacao" a tabela "viagem_sentido_motorista".
statement = "alter table public.viagem_sentido_motorista add if not exists geolocalizacao varchar(200);"

# Executa a instrucao SQL de adicao da coluna "geolocalizacao" a tabela "viagem_sentido_motorista".
conn.manipular(statement)

################################################################################################################
# Tabela "contas_controle_saldos"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "contas_controle_saldos".
statement = """create table if not exists public.contas_controle_saldos (
  id bigserial not null,
  contaid int8 not null,
  saldo_sumario float8 not null,
  dateinsert timestamptz not null,
  dateupdate timestamptz,
  constraint contas_controle_saldos_pk primary key (id),
  constraint contas_controle_saldos_uk unique (contaid)
);"""

# Executa a instrucao SQL de criacao da tabela "contas_controle_saldos".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "saldo_estudante" a tabela "contas_controle_saldos".
statement = "alter table public.contas_controle_saldos add if not exists saldo_estudante float8 not null default 0;"

# Executa a instrucao SQL de adicao da coluna "saldo_estudante" a tabela "contas_controle_saldos".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "beneficioid" a tabela "contas_controle_saldos".
statement = "alter table public.contas_controle_saldos add if not exists beneficioid int8;"

# Executa a instrucao SQL de adicao da coluna "beneficioid" a tabela "contas_controle_saldos".
conn.manipular(statement)

################################################################################################################
# Tabela "controle_facial_linhas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "controle_facial_linhas".
# statement = """create table if not exists public.controle_facial_linhas
# (
#   id bigserial,
#   datecontrol date,
#   dateinsert timestamptz,
#   constraint controle_facial_linhas_pk primary key (id),
#   constraint controle_facial_linhas_uk unique (datecontrol)
# );"""

# Executa a instrucao SQL de criacao da tabela "controle_facial_linhas".
# conn.manipular(statement)

################################################################################################################
# Tabela "viagem"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "viagem".
statement = """create table if not exists public.viagem (
  id bigserial not null,
  id_viagem_cm varchar(50) not null,
  linha_id int8 not null,
  motorista_id int8 not null,
  dateinsert timestamptz null default now(),
  num_tentativas_integracao_abertura int8 null default 0,
  datelastintegr_abertura timestamptz null,
  num_tentativas_integracao_encerramento int8 null default 0,
  datelastintegr_encerramento timestamptz null,
  viagem_id int8 null,
  horario_viagem_id int8 null,
  encerramento_id varchar(50) null,
  viagem_atual bool null default true,
  dateviagemabertabackend timestamptz,
  dateviagemencerradabackend timestamptz,
  data_viagem_encerrada timestamptz null,
  constraint viagem_pk primary key (id),
  constraint viagem_uk unique (id_viagem_cm)
);"""

# Executa a instrucao SQL de criacao da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "geolocalizacao_abertura" a tabela "viagem".
statement = "alter table public.viagem add if not exists geolocalizacao_abertura varchar(200);"

# Executa a instrucao SQL de adicao da coluna "geolocalizacao_abertura" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "responsavel_encerramento" a tabela "viagem".
statement = "alter table public.viagem add if not exists responsavel_encerramento int8;"

# Executa a instrucao SQL de adicao da coluna "responsavel_encerramento" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "geolocalizacao_encerramento" a tabela "viagem".
statement = "alter table public.viagem add if not exists geolocalizacao_encerramento varchar(200);"

# Executa a instrucao SQL de adicao da coluna "geolocalizacao_encerramento" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "sentido_inicial" a tabela "viagem".
statement = "alter table public.viagem add if not exists sentido_inicial int default 1;"

# Executa a instrucao SQL de adicao da coluna "sentido_inicial" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "status_internet" a tabela "viagem".
statement = "alter table public.viagem add if not exists status_internet varchar(100) default 'ONLINE';"

# Executa a instrucao SQL de adicao da coluna "status_internet" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "manter_integra" a tabela "viagem".
statement = "alter table public.viagem add if not exists manter_integra boolean default true;"

# Executa a instrucao SQL de adicao da coluna "manter_integra" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "manter_integra_encerramento" a tabela "viagem".
statement = "alter table public.viagem add if not exists manter_integra_encerramento boolean default true;"

# Executa a instrucao SQL de adicao da coluna "manter_integra_encerramento" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "data_manter_integra" a tabela "viagem".
statement = "alter table public.viagem add if not exists data_manter_integra timestamptz(0);"

# Executa a instrucao SQL de adicao da coluna "data_manter_integra" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "data_manter_integra_encerramento" a tabela "viagem".
statement = "alter table public.viagem add if not exists data_manter_integra_encerramento timestamptz(0);"

# Executa a instrucao SQL de adicao da coluna "data_manter_integra_encerramento" a tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "viagem".
statement = "alter table public.viagem alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "viagem".
statement = "alter table public.viagem alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "data_viagem_encerrada" da tabela "viagem".
statement = "alter table public.viagem alter column data_viagem_encerrada type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "data_viagem_encerrada" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateviagemabertabackend" da tabela "viagem".
statement = "alter table public.viagem alter column dateviagemabertabackend type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateviagemabertabackend" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateviagemencerradabackend" da tabela "viagem".
statement = "alter table public.viagem alter column dateviagemencerradabackend type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateviagemencerradabackend" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "datelastintegr_abertura" da tabela "viagem".
statement = "alter table public.viagem alter column datelastintegr_abertura type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "datelastintegr_abertura" da tabela "viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "datelastintegr_encerramento" da tabela "viagem".
statement = "alter table public.viagem alter column datelastintegr_encerramento type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "datelastintegr_encerramento" da tabela "viagem".
conn.manipular(statement)

################################################################################################################
# Tabela "lista_tipos_beneficios"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "lista_tipos_beneficios".
statement = """create table if not exists public.lista_tipos_beneficios (
  id int8 not null,
  descricao varchar(100),
  percentual float,
  valor float,
  geral boolean default false,
  constraint lista_tipos_beneficios_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "lista_tipos_beneficios".
conn.manipular(statement)

################################################################################################################
# Tabela "beneficios_pontuais"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "beneficios_pontuais".
statement = """create table if not exists public.beneficios_pontuais (
  id bigint not null,
  nome varchar(200),
  ativo boolean default true,
  validode timestamptz(0) not null,
  validoate timestamptz(0) not null,
  percentual float default 100,
  valorfixo float default 0,
  constraint beneficios_pontuais_pk primary key(id)
);"""

# Executa a instrucao SQL de criacao da tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "marcadoativo" a tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais add if not exists marcadoativo boolean default true;"

# Executa a instrucao SQL de adicao da coluna "marcadoativo" a tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateinsert" a tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais add if not exists dateinsert timestamptz default now();"

# Executa a instrucao SQL de adicao da coluna "dateinsert" a tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateupdate" a tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais add if not exists dateupdate timestamptz;"

# Executa a instrucao SQL de adicao da coluna "dateupdate" a tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "validode" da tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais alter column validode type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "validode" da tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "validoate" da tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais alter column validoate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "validoate" da tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "beneficios_pontuais".
statement = "alter table public.beneficios_pontuais alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "beneficios_pontuais".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateupdate" da tabela "beneficios_pontuais".
statement="alter table public.beneficios_pontuais alter column dateupdate type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateupdate" da tabela "beneficios_pontuais".
conn.manipular(statement)

################################################################################################################
# Tabela "cobrancas_contas_analise"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "cobrancas_contas_analise".
statement = """create table if not exists public.cobrancas_contas_analise (
  id bigserial not null,
  cobrancaid int8 not null,
  dif_permitida float not null,
  ordem int8 not null,
  contaid_analise int8 not null,  
  nome_analise varchar(1000),
  matriz_analise cube not null,
  dif_obtida_analise float not null,
  range_obtido float not null,
  dateinsert timestamptz default now(),
  dateenviadobackend timestamptz,
  constraint cobrancas_contas_analise_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "cobrancas_contas_analise".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "dateinsert" da tabela "cobrancas_contas_analise".
statement = "alter table public.cobrancas_contas_analise alter column dateinsert type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "dateinsert" da tabela "cobrancas_contas_analise".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "cobrancas_contas_analise".
statement = "alter table public.cobrancas_contas_analise alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "cobrancas_contas_analise".
conn.manipular(statement)

# Define a instrucao SQL que drop a constraint "not null" da coluna "matriz_analise" da tabela "cobrancas_contas_analise".
statement="alter table public.cobrancas_contas_analise alter column matriz_analise drop not null;"

# Executa a instrucao SQL de exclusao da constraint "not null" da coluna "matriz_analise" da tabela "cobrancas_contas_analise".
conn.manipular(statement)

################################################################################################################
# Tabela "tabelas_criadas_facial"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "tabelas_criadas_facial".
# statement = """create table if not exists public.tabelas_criadas_facial (
#   tabela varchar(100),
#   constraint tabelas_criadas_facial_pk primary key (tabela)
# );"""

# Executa a instrucao SQL de criacao da tabela "cobrancas_contas_analise".
# conn.manipular(statement)

################################################################################################################
# Tabela "log_integracao_viagem"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "log_integracao_viagem".
statement = """create table if not exists public.log_integracao_viagem (
  id bigserial not null,
  viagemid int8 not null,
  acao varchar(20) default 'ABERTURA',
  datalog timestamptz(0),
  url varchar(1000),
  headers varchar(4000),
  payload text,
  response_status varchar(100),
  response_text varchar(65000),
  constraint log_integracao_viagem_pk primary key(id)
);"""

# Executa a instrucao SQL de criacao da tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "datalog" da tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem alter column datalog type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "datalog" da tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "datalog" da tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem alter column datalog set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "datalog" da tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "url_token" a tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem add if not exists url_token varchar(4000);";

# Executa a instrucao SQL de adicao da coluna "url_token" a tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "headers_token" a tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem add if not exists headers_token varchar(4000);";

# Executa a instrucao SQL de adicao da coluna "headers_token" a tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "payload_token" a tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem add if not exists payload_token varchar(4000);";

# Executa a instrucao SQL de adicao da coluna "payload_token" a tabela "log_integracao_viagem".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "response_token" a tabela "log_integracao_viagem".
statement = "alter table public.log_integracao_viagem add if not exists response_token varchar(4000);";

# Executa a instrucao SQL de adicao da coluna "response_token" a tabela "log_integracao_viagem".
conn.manipular(statement)

################################################################################################################
# Tabela "log_integracao_cobranca"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "log_integracao_cobranca".
statement = """create table if not exists public.log_integracao_cobranca (
  id bigserial not null,
  cobrancaid int8 not null,
  datalog timestamptz(0),
  url varchar(1000),
  headers varchar(4000),
  payload text,
  response_status varchar(100),
  response_text varchar(65000),
  constraint log_integracao_cobranca_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "datalog" da tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca alter column datalog type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "datalog" da tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "datalog" da tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca alter column datalog set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "datalog" da tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "url_token" a tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca add if not exists url_token varchar(4000);"

# Executa a instrucao SQL de adicao da coluna "url_token" a tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "headers_token" a tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca add if not exists headers_token varchar(4000);"

# Executa a instrucao SQL de adicao da coluna "headers_token" a tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "payload_token" a tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca add if not exists payload_token varchar(4000);"

# Executa a instrucao SQL de adicao da coluna "payload_token" a tabela "log_integracao_cobranca".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "response_token" a tabela "log_integracao_cobranca".
statement = "alter table public.log_integracao_cobranca add if not exists response_token varchar(4000);"

# Executa a instrucao SQL de adicao da coluna "response_token" a tabela "log_integracao_cobranca".
conn.manipular(statement)

################################################################################################################
# Tabela "log_integracao_viagem_sentido_motorista"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "log_integracao_viagem_sentido_motorista".
statement = """create table if not exists public.log_integracao_viagem_sentido_motorista (
  id bigserial not null,
  viagem_sentido_motorista_id int8 not null,
  datalog timestamptz(0),
  url varchar(1000),
  headers varchar(4000),
  payload text,
  response_status varchar(100),
  response_text varchar(65000),
  constraint log_integracao_viagem_sentido_motorista_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "log_integracao_viagem_sentido_motorista".
conn.manipular(statement)

# Define a instrucao SQL que altera o tipo da coluna "datalog" da tabela "log_integracao_viagem_sentido_motorista".
statement = "alter table public.log_integracao_viagem_sentido_motorista alter column datalog type timestamp;"

# Executa a instrucao SQL de alteracao do tipo da coluna "datalog" da tabela "log_integracao_viagem_sentido_motorista".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "datalog" da tabela "log_integracao_viagem_sentido_motorista".
statement = "alter table public.log_integracao_viagem_sentido_motorista alter column datalog set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "datalog" da tabela "log_integracao_viagem_sentido_motorista".
conn.manipular(statement)

################################################################################################################
# Tabela "controle_execucoes_diarias"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "controle_execucoes_diarias".
statement = """create table if not exists public.controle_execucoes_diarias (
  data_acao varchar(10),
  acao varchar(100),
  constraint controle_execucoes_diarias_pk primary key (data_acao, acao)
);"""

# Executa a instrucao SQL de criacao da tabela "controle_execucoes_diarias".
conn.manipular(statement)

# Define a instrucao SQL que, se ainda nao existir, adiciona a coluna "dateinsert" a tabela "controle_execucoes_diarias".
statement = "alter table public.controle_execucoes_diarias add if not exists dateinsert timestamp;"

# Executa a instrucao SQL de adicao da coluna "dateinsert" a tabela "controle_execucoes_diarias".
conn.manipular(statement)

# Define a instrucao SQL que altera o valor default da coluna "dateinsert" da tabela "controle_execucoes_diarias".
statement = "alter table public.controle_execucoes_diarias alter column dateinsert set default now() at time zone 'utc';"

# Executa a instrucao SQL de alteracao do valor default da coluna "dateinsert" da tabela "controle_execucoes_diarias".
conn.manipular(statement)

################################################################################################################
# Tabela "facial_fila_linhas"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "facial_fila_linhas".
statement = """create table if not exists public.facial_fila_linhas (
  id bigserial not null,
  contaid int8 not null,
  data cube,
  dateinsert timestamptz(0) default now(),
  constraint facial_fila_linhas_uk unique (contaid)
);"""

# Executa a instrucao SQL de criacao da tabela "facial_fila_linhas".
conn.manipular(statement)

################################################################################################################
# Tabela "fila_atualiza_saldo"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "fila_atualiza_saldo".
statement = """create table if not exists public.fila_atualiza_saldo (
  id bigserial not null,
  contaid int8 not null,
  dateupdate timestamptz(0),
  saldo_sumario float8,
  saldo_estudante float8,
  constraint fila_atualiza_saldo_pk primary key(id),
  constraint fila_atualiza_saldo_uk unique (contaid)
);"""

# Executa a instrucao SQL de criacao da tabela "fila_atualiza_saldo".
conn.manipular(statement)

################################################################################################################
# Tabela "propagandas_em_exec"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "propagandas_em_exec".
statement = """create table if not exists public.propagandas_em_exec (
   id bigserial not null,
   idpropaganda int8,
   vigenciade timestamp,
   vigenciaate timestamp,
   ordenacao int default 1,
   imagem varchar,
   duracao_em_segundos int8 default 10,
   constraint propagandas_ex_exec_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "propagandas_em_exec".
conn.manipular(statement)

# Define a instrucao SQL que exclui todos os registros da tabela "propagandas_em_exec".
statement = "delete from public.propagandas_em_exec;"

# Executa a instrucao SQL de exclusao dos registros da tabela "propagandas_em_exec".
conn.manipular(statement)

# Define e executa as instrucoes SQL de insercao dos registros de logotipos de campanha na tabela "propagandas_em_exec".
statement = """insert into public.propagandas_em_exec(idpropaganda, vigenciade, vigenciaate, ordenacao, imagem)
               values (4, '2022-06-08', '1099-12-31', 1, '/home/pi/caixa-magica/propaganda/buspay_azul.png');"""
conn.manipular(statement)

statement = """insert into public.propagandas_em_exec(idpropaganda, vigenciade, vigenciaate, ordenacao, imagem, duracao_em_segundos)
               values (5, '2022-06-10', '1099-12-31', 2, '/home/pi/caixa-magica/propaganda/campanha_buspay.png', 15);"""
conn.manipular(statement)

statement = """insert into public.propagandas_em_exec(idpropaganda, vigenciade, vigenciaate, ordenacao, imagem, duracao_em_segundos)
               values (5, '2022-06-14', '2099-12-31', 0, '/home/pi/caixa-magica/propaganda/propaganda.png', 10);"""
conn.manipular(statement)

################################################################################################################
# Tabela "historico_geoloc"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "historico_geoloc".
statement = """create table if not exists public.historico_geoloc (
  id bigserial not null,
  latitude float8,
  longitude float8,
  viagemid varchar(50),
  motoristaid numeric,
  dateinsert timestamp,
  distancia_last_id_km numeric,
  constraint historico_geoloc_pk primary key (id)
);"""

# Executa a instrucao SQL de criacao da tabela "historico_geoloc".
conn.manipular(statement)

################################################################################################################
# Tabela "estatistica_total_km"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "estatistica_total_km".
statement = """create table if not exists public.estatistica_total_km (
  dat date,
  total_km numeric,
  dateinsert timestamptz,
  dateupdate timestamptz,
  constraint estatistica_total_km_pk primary key(dat)
);"""

# Executa a instrucao SQL de criacao da tabela "estatistica_total_km".
conn.manipular(statement)

################################################################################################################
# Tabela "estatistica_total_motorista_km"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "estatistica_total_motorista_km".
statement = """create table if not exists public.estatistica_total_motorista_km (
  dat date,
  motoristaid numeric,
  motorista varchar(1000),
  total_km numeric,
  dateinsert timestamptz,
  dateupdate timestamptz,
  constraint estatistica_total_motorista_km_pk primary key(dat, motoristaid)
);"""

# Executa a instrucao SQL de criacao da tabela "estatistica_total_motorista_km".
conn.manipular(statement)

################################################################################################################
# Tabela "estatistica_total_viagem_km"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "estatistica_total_viagem_km".
statement = """create table if not exists public.estatistica_total_viagem_km (
  dat date,
  motoristaid numeric,
  motorista varchar(1000),
  id_viagem_cm varchar(100),
  linha_id numeric,
  codigopublico varchar(20),
  total_km numeric,
  dateinsert timestamptz,
  dateupdate timestamptz,
  constraint estatistica_total_viagem_km_pk primary key(dat, motoristaid, id_viagem_cm)
);"""

# Executa a instrucao SQL de criacao da tabela "estatistica_total_viagem_km".
conn.manipular(statement)

################################################################################################################
# Tabela "estatistica_total_linha_km"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "estatistica_total_linha_km".
statement = """create table if not exists public.estatistica_total_linha_km (
  dat date,
  linha_id numeric,
  codigopublico varchar(20),
  total_km numeric,
  dateinsert timestamptz,
  dateupdate timestamptz,
  constraint estatistica_total_linha_km_pk primary key(dat, linha_id)
);"""

# Executa a instrucao SQL de criacao da tabela "estatistica_total_linha_km".
conn.manipular(statement)

################################################################################################################
# Tabela "estatistica_total_status_viagem_km"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "estatistica_total_status_viagem_km".
statement = """create table if not exists public.estatistica_total_status_viagem_km (
  dat date,
  status_viagem varchar(10),
  total_km numeric,
  dateinsert timestamptz,
  dateupdate timestamptz,
  constraint eestatistica_total_status_viagem_km_pk primary key(dat, status_viagem)
);"""

# Executa a instrucao SQL de criacao da tabela "estatistica_total_status_viagem_km".
conn.manipular(statement)

################################################################################################################
# Tabela "faces_del_elastic"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "faces_del_elastic".
statement = """create table if not exists public.faces_del_elastic (
  chave varchar(1000),
  dateinsert timestamptz,
  constraint faces_del_elastic_pk primary key(chave)
);"""

# Executa a instrucao SQL de criacao da tabela "faces_del_elastic".
conn.manipular(statement)

################################################################################################################
# Tabela "discord_notificacoes"

# Define a instrucao SQL que, se ainda nao existir, cria a tabela "discord_notificacoes".
statement = """create table if not exists public.discord_notificacoes (
  id bigserial not null,
  mensagem varchar(4000) not null,
  tipo varchar(50) not null,
  enviada boolean default false,
  retorno_enviada varchar(4000)
);"""

# Executa a instrucao SQL de criacao da tabela "discord_notificacoes".
conn.manipular(statement)

# statement="alter table facial add if not exists backend_lastupdatetime varchar(30)"
# conn.manipular(statement)
