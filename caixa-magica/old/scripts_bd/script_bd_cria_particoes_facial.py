import sys
import pathlib
path_atual = "/home/pi/caixa-magica/scripts_bd"

sys.path.insert(1, path_atual + '/../core/')
import db
import threading
import time
import funcoes_logs

local = 'script_bd_cria_particoes_facial.py'

funcoes_logs.insere_log("Iniciando " + local, local)

funcoes_logs.insere_log("Abrindo conexao BD", local)


# cria tabela de range de contas (para particionamento da tabela de reconhecimento facial)
def cria_facial_range_contas():
    conn1 = db.Conexao()

    funcoes_logs.insere_log("criando tabela facial_range_contas", local)
    st = """CREATE TABLE if not exists public.facial_range_contas (
        id bigserial NOT NULL,
        tabela varchar(200) not null,
        particao varchar(100) NOT NULL,
        contaid_de int8 NOT NULL,
        contaid_ate int8 NOT NULL,
        CONSTRAINT facial_range_contas_pk PRIMARY KEY (id),
        CONSTRAINT facial_range_contas_uk0 UNIQUE (particao)
);"""
    conn1.manipular(st)
    funcoes_logs.insere_log("Tabela facial_range_contas criada",local)

    del conn1

# rotina que cria as tabelas facial por linha (usando threads)
def cria_facial(linhaId = ""):
    conn1 = db.Conexao()

    funcoes_logs.insere_log("Iniciando cria_facial(), para criacao de tabelas de faces por linhas", local)

    # Se nao foi informada uma linha em especifico
    if linhaId == "" or linhaId == None:
        # Cria os ranges de particoes faciais
        cria_facial_range_contas()
    
        # a partir da relacao de linhas, criamos uma tabela facial para cada favoritos
        funcoes_logs.insere_log("identificando as linhas ativas existentes", local)
        st = """select concat('facial_linha_', id) tablename, 2 ordem
	    from linhas where ativa = true
	    union select 'facial' tablename, 1 ordem
            order by 2"""
        c = conn1.consultar(st)
        funcoes_logs.insere_log("Identificada(s) " + str(len(c)) + " linha(s) para criacao de tabelas de faces", local)
    # Mas se a linha foi informada
    else:
        dados=(str(linhaId), )
        st = "select concat('facial_linha_', %s) tablename, 2 ordem"
        c = conn1.consultarComBind(st, dados)
        funcoes_logs.insere_log("Cenario de criacao da tabela de linha especifica, id " + str(linhaId), local)

    i=0
    num_threads = 10
    threads=[]

    while i < len(c):
        tabela = c[i][0]
        t = threading.Thread(target=cria_facial_thread, args=(i, tabela) )
        t.start()
        threads.append(t)

        while threading.activeCount() >= num_threads:
            funcoes_logs.insere_log("Numero de threads permitidas " + str(num_threads) + ". Aguardando para liberacao para nova thread.", local) 
            time.sleep(0.001)

        i = i+1
    for thread in threads:
        thread.join()

    del conn1

# rotina que cria as tabelas e particoes, atraves de uma thread por tabela
def cria_facial_thread(i, tabela):
    conn1 = db.Conexao()
    funcoes_logs.insere_log("Iniciando Thread para criacao da tabela " + tabela, local)
    
    tabela_ja_criada = False

    # Checa se a tabela ja foi criada (dentro do controle existente)
    dados = (str(tabela), )
    sql = "select 1 from tabelas_criadas_facial where tabela = %s"
    result = conn1.consultarComBind(sql, dados)

    for row in result:
        # Checamos se a tabela consta fisicamente na base
        # se constar, pode ser que as particoes nao tenham sido totalmente criadas. Ai manter execucao 
        # deste script
        dados=(str(tabela), )
        sql = "select 1 from pg_tables where tablename=%s"
        result = conn1.consultarComBind(sql, dados)

        for row in result:
            tabela_ja_criada = True

    if tabela_ja_criada:
        print("Tabela " + str(tabela) + " ja consta criada no sistema.")
        #return

    # cria tabela de reconhecimento facial
    funcoes_logs.insere_log("Criando tabela " + tabela, local)
    st = """CREATE TABLE if not exists public.""" + tabela + """ (
        id serial NOT NULL,
        nome varchar(80) NOT NULL,
        """"data"""" cube NOT NULL,
        conta int8 NOT NULL,
        dateinsert timestamp NULL DEFAULT timezone('utc'::text, now()),
        dateupdate timestamp NULL,
        CONSTRAINT """ + tabela + """_pkey PRIMARY KEY (id, conta),
        CONSTRAINT """ + tabela + """_uk unique (conta)
    )
    PARTITION BY RANGE (conta);"""
    conn1.manipular(st)
    #print(st)
    funcoes_logs.insere_log("Tabela " + tabela + " criada", local)

    sql = "alter table " + tabela + " add if not exists backend_lastupdatetime varchar(30)"
    conn1.manipular(sql)

    # Roda procedimento de criacao de particoes
    funcoes_logs.insere_log("Criando particoes para a tabela " + tabela, local)
    sql = """
do
$do$
declare
  v_cnt int8 := 0;
  v_cnt_limite int8 := 60;
  v_valor_inicial int8 := -50000;
  v_multiplo int8 := 50000;
  v_particao varchar(100);
  v_valor_de int8;
  v_valor_ate int8;
  v_statement varchar(200);
begin
	/*delete from facial_range_contas;*/
	
	v_valor_de := v_valor_inicial; 
	v_valor_ate := v_valor_de + v_multiplo;
	
	for i in v_cnt..v_cnt_limite loop
	    v_particao := concat('""" + tabela + """_p_', i);
	   
	    v_valor_de := v_valor_de + v_multiplo; 
	    v_valor_ate := v_valor_ate + v_multiplo;

            insert into facial_range_contas 
                (tabela, particao, contaid_de, contaid_ate)
        values ('""" + tabela + """', v_particao, v_valor_de, v_valor_ate)
              on conflict (particao) do nothing;	

            v_statement := concat('CREATE TABLE if not exists public.', v_particao, ' PARTITION OF public.""" + tabela + """ for values from (', v_valor_de, ') to (', v_valor_ate, ');');
            execute v_statement;

            /* TODO: CRIAR INDICE EM TODAS AS PARTICOES GIST */
            /*v_statement = concat('begin drop index ', v_particao, '_data_idx; exception when others then null; end;');
            execute v_statement;*/

            v_statement := concat('create index ', v_particao, '_data_idx ON ONLY public.', v_particao, ' USING gist (data);');
            begin
               execute v_statement;
            exception when others then null;
            end;

            v_statement := concat('ALTER TABLE ', v_particao, ' SET (parallel_workers = 10);');
            execute v_statement;

	end loop;
end;
$do$"""
    conn1.manipular(sql)
    funcoes_logs.insere_log("Particoes criadas na tabela " + tabela, local)

    # Por fim, inserimos na tabela de controle de favoritos por linhas, indicando que esta tabela ja pode ser usada no processo
    dados=(str(tabela), )
    sql = "insert into tabelas_criadas_facial (tabela) values (%s) on conflict (tabela) do nothing;"
    conn1.manipularComBind(sql, dados)

    del conn1


