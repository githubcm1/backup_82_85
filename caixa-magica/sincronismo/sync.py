import threading
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"
sys.path.insert(1, path_atual)

import req
import json
import db
import datetime
import time
import os
import math
import threading

sys.path.insert(1, path_atual + "/../core/")
import funcoes_logs
import funcoes_string
import funcoes_viagem
import funcoes_elastic

local='sync.py'
funcoes_logs.insere_log("Iniciando " + local, local)

# # global valor_original
global onibus_id
global caixa_magica_id
global bilhetadoraId

GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS = 100

json_param = path_atual + "/../../caixa-magica-vars/param_elastic.json"

### Abrindo jsons
try:
    with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
        vars_conf = json.load(json_data)
        GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS = vars_conf['tamanho_pagina_novas_contas']
        funcoes_logs.insere_log("Assumindo valor config.json para GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS: " + str(GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS), local) 
except Exception as e:
    funcoes_logs.insere_log("Assumindo valor padrao para GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS: " + str(GLOBAL_TAMANHO_PAGINA_NOVAS_CONTAS), local) 

try:
    with open(path_atual + '/../../caixa-magica-operacao/sincronismo.json') as json_data:
        global config
        config = json.load(json_data)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir arquivo - " + str(e), local)

# instalacao.json
try:
    with open(path_atual +'/../../caixa-magica-operacao/instalacao.json') as json_data:
        instalacao = json.load(json_data)

        onibus_id = instalacao['veiculo']
        caixa_magica_id = instalacao['caixa_id']
        bilhetadoraId = instalacao['bilhetadoraId']
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir 'instalacao.json' em 'sync.py': "+ str(e), local)


# Funcao utilizada para determinar o ID do PCD, caso o sujeito seja um PCD
# Rotina necessaria para que o backend receba a informacao para cobranca
def determinaContaPcdIdCobranca(cobrancaid):
    conn1 = db.Conexao()

    # Checa se trata-se de um caso de cobranca de acompanhante
    sql = """select id, viagemid
             from cobrancas
             where isento_acompanhante_pcd = true
               and contapcdid is null
               and id = %s"""
    dados = (cobrancaid,)
    result = conn1.consultarComBind(sql, dados)

    # sendo uma cobranca de acompanhante pcd, determinamos agora quem seria esse PCD
    for row in result:
        sql = """select contaid
                 from cobrancas c
                 where id in
                    (
                        select max(c1.id)
                        from cobrancas c1
                        where c1.id < %s
                          and c1.viagemid = %s
                          and c1.pcd = true
                    )"""
        dados = (row[0], row[1], )
        result = conn1.consultarComBind(sql, dados)

        # Atraves do ID obtido, atualizamos o campo na base
        for row in result:
            sql = "update cobrancas set contapcdid=%s where id=%s"
            dados=(row[0], cobrancaid,)
            conn1.manipularComBind(sql, dados)

    del conn1
    return

# retorna o ID do PCD
def retornaContaPcdIdCobranca(cobrancaid):
    conn1 = db.Conexao()
    try:
        sql = "select contapcdid from cobrancas where id=%s and contapcdid is not null"
        dados=(cobrancaid,)
        result = conn1.consultarComBind(sql, dados)
        del conn1

        for row in result:
            return row[0]
    except:
        pass

    return ""

#função retorna um int, indicando o estado
#0 - erro no envio
#1 - sucesso
#2 - nenhuma cobrança foi encontrada no banco
#
def enviar_cobrancas():
    try:
        with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            LIMITE_QUERY = aux['limite_envio_cobrancas']
    except:
        LIMITE_QUERY = 1

    funcoes_logs.insere_log("Iniciando envio de cobranças", local)
    conn = db.Conexao()
    c = conn.consultar("""select c.id, c.valor, c.datahora, c.tipopagamento, c.tipoidentificacao , c.fotousuario, c.enviada, 
	   c.contaid, v.linha_id, c.viagemid, c.geolocalizacao,
	   c.datahorafalhaintegr , c.status_internet ,c.datahoraenviada, c.chavecobranca, c.isento_acompanhante_pcd, c.pcd
from cobrancas c,
	 viagem v 
where v.id_viagem_cm  = c.viagemid 	 
  and v.dateviagemabertabackend  is not null
  and c.enviada = false
  and c.datahorafalhaintegr is null
  and c.check_contas_analise = true
order by 1 limit """ + str(LIMITE_QUERY))
    cobrancas = []
    lista_ids = []
    print("Retorno:" + str(len(c)) )
    if len(c) == 0:
        funcoes_logs.insere_log("Não existem mais cobranças a serem enviadas", local)

        # recoloca para processamento eventuais registros que ficaram retidos
        query = conn.manipular("update cobrancas set datahorafalhaintegr=null where datahorafalhaintegr is not null")

        return 2
    for row in c:
        # Determina o ID do PCD
        determinaContaPcdIdCobranca(row[0])
        contapcdid = retornaContaPcdIdCobranca(row[0])
        funcoes_logs.insere_log("procurando no banco para enviar", local)
        contaId = 0 if row[7] == None else row[7]
        
        geolocalizacao = row[10]

        if geolocalizacao == "" or geolocalizacao == None:
            geolocalizacao = '0,0'

        acompanhante = False
        if row[15] == True:
            acompanhante = True

        # Para cada registro de cobranca, devemos buscar os registros
        # de casos ditos "parecidos".
        # Isso sera enviado para o backend de forma a fazer uma contra-checagem
        #sql = "select id, ordem from cobrancas_contas_analise where cobrancaid=%s"
        sql = """select x.contaid, x.ordem, x.similaridadePercentual
                 from
                 (
	            select 1 ordem, c.contaid, round(((c.range_analise) * 100)::numeric,2) similaridadePercentual 
	            from cobrancas c where id=%s
	            union
	            select ordem+1 ordem, cca.contaid_analise , round(((cca.range_obtido) * 100)::numeric,2) pct
	            from cobrancas_contas_analise cca 
	            where cca.cobrancaid =%s
	            order by 1
                ) x"""
        dadosCA = (row[0],row[0],)
        resultCA = conn.consultarComBind(sql, dadosCA)

        # Formamos um json com os dados
        jsonCA = ""

        for rowCA in resultCA:
            jsonCA = jsonCA + '{"contaId": ' + str(rowCA[0]) + ', "posicao": ' + str(rowCA[1]) + ', "similaridadePercentual": ' + str(rowCA[2]) +'},'

        if jsonCA != "":
            jsonCA = '[' + jsonCA[0:len(jsonCA)-1] + ']'
            
            try:
                jsonCA = json.loads(jsonCA)
            except:
                jsonCA = []

        cobranca = {
                'data': row[2],
                'tipoIdentificacao': row[4],
                'tipo':row[3],
                'contaId':contaId,
                'foto': row[5] if row[5] != '' else "", #todo
                'extensaoArquivoFoto': '',
                'linhaId': row[8], ##### Nao tem que pegar de fora, tem que pegar do banco
                'veiculoId': onibus_id,
                'caixaMagicaId': caixa_magica_id,
                'caixaMagicaGuid': row[9],
                'geolocalizacao': geolocalizacao,
                'chavecobranca': row[14],
                'acompanhante': acompanhante,
                'candidatos': jsonCA,
                'ContaPcdId': contapcdid
                #,'status_internet': row[12] # ATIVAR QUANDO O METODO FOR HABILITADO PARA ISTO
            }
        '''
        disc: Dinheiro, PassagemUnica, CartaoBandeira, ValeTransporte, Passagem, Beneficio

        1 - vt
        2 - passagem (facial/mifare/digital)
        3 - benefício
        4 - dinheiro
        5 - gratuidade (beneficio)
        '''
        discriminator = ""
        if row[3] == '1':
            discriminator = "ValeTransporte"
        if row[3] == '2':
            discriminator = "Passagem"
        if row[3] == '3':
            discriminator = "Beneficio"
        if row[3] == '5':
            discriminator = "Dinheiro"
        if row[3] == '8':
            discriminator = "Gratuidade"
        ##cobranca['discriminator'] = discriminator
        
        # Se for botao de dinheiro
        if row[3] == '5':
            tipoPassagem = 2 # Dinheiro
        # Mas se for caso de acompanhante pcd ou um pcd, entendemos que trata-se de uma gratuidade
        elif row[15] == True or row[16] == True:
            tipoPassagem = 3
        else:
            tipoPassagem = 1 # Outros

        if row[3] == '8':
            tipoPassagem = 3
        cobranca['tipoPassagem'] = tipoPassagem

        cobrancas.append(cobranca)
        lista_ids.append(row[0])

    funcoes_logs.insere_log("Enviando cobrancas", local)
    send = req.enviar_cobrancas(cobrancas)
    print(send)
    if not send:
        funcoes_logs.insere_log("Erro no envio das cobranças - possível erro de conexão", local)

        # Marcamos o registro na base, para que ele fique separado na integracao
        query = conn.manipular("update cobrancas set datahorafalhaintegr=now(), enviada =false where id in ({})".format(",".join(map(str, lista_ids))))
        return 0
    query = conn.manipular("UPDATE cobrancas SET enviada = true, datahoraenviada=(now() at time zone 'utc') WHERE id IN ({})".format(",".join(map(str, lista_ids))))
    return 1

'''
função retorna um int, indicando o estado
0 - erro (provável erro de conexão)
1 - sucesso
2 - não existem mais contas
'''
def receber_operadores():
    funcoes_logs.insere_log("Iniciando receber_operadores()", local)

    # Primeiro, marca os operadores para exclusao logica
    conn_interna = db.Conexao()

    # Efetuamos a chamada para obtermos TODOS OS OPERADORES da empresa
    # Uma vez recebidos (PELO VOLUME NÃO SER ELEVADO), insercoes atuam como UPSERT na tabela de operadores
    r = req.receber_operadores()

    try:
        with open(path_atual + "/../../caixa-magica-operacao/sincronismo_operadores.json") as json_data:
            syncoper = json.load(json_data)

        for row in r:
            funcoes_logs.insere_log("Inserindo operador " + row[2], local)
            
            if row[9] == False:
                dados(str(row[0]),)
                sql = "delete from operadores where id = %s"
            else:
                valor_cpf = '22222222222'
                dados = (str(row[2]), str(row[0]), str(row[1]), str(row[4]), str(row[5]),str(valor_cpf), str(row[10]), str(row[2]), str(row[0]), str(row[1]), str(row[4]), str(row[5]), str(valor_cpf), str(row[10]), ) 
                sql = "INSERT INTO operadores(nome, id_web, id_qr, matricula, remover, fiscal, cpf, backend_lastupdatetime) VALUES(%s, %s,%s, %s, false, %s, %s,%s) ON CONFLICT (id_web) DO UPDATE SET NOME= %s, id_web= %s, id_qr=%s, matricula = %s, dateupdate = (now() at time zone 'utc'), remover = false, fiscal=%s, cpf=%s, backend_lastupdatetime=%s;"
            conn_interna.manipularComBind(sql, dados)
            syncoper['lastUpdateTime'] = row[10]
            funcoes_logs.insere_log("Operador " + row[2] + " inserido", local)

            last_sync = syncoper['lastUpdateTime']
            pos_timezone = last_sync.find("+")

            with open(path_atual +"/../../caixa-magica-operacao/sincronismo_operadores.json", "w") as f:
                f.write(json.dumps(syncoper))

        # Forca a checagem da contingencia
        os.system("sudo python3 " + path_atual + "/sincronismo_contingencia_operadores.py")

        return 1
    except Exception as e:
        # Forca a checagem da contingencia
        os.system("sudo python3 " + path_atual + "/sincronismo_contingencia_operadores.py")

        return 2

def atualiza_facial_linhas(conta, result, deleteFacial):
    funcoes_logs.insere_log("Iniciando atualiza_facial_linhas para a conta id " + str(conta), local)
    conn1 = db.Conexao()

    # Para cada tabela encontrada
    for row in result:
        try:
            tabela = str(row[0])

            if deleteFacial:
                sql = "delete from " + tabela + " where conta=" + str(conta)
            else:
                sql = """update """ + tabela + """
                 set data = (select data from facial where conta=""" + str(conta) +"""), 
	             dateupdate=now()
                 where conta=""" + str(conta)
            conn1.manipular(sql)
            funcoes_logs.insere_log("Atualizada conta id " + str(conta) + " na tabela " + tabela, local)
        except Exception as e:
            print(str(e))
            funcoes_logs.insere_log("Erro atualiza_facial_linhas: " + str(e), local)
    del conn1

# Rotina para atualizacao de saldos
def atualizar_saldos_fila():
    conn_interna = db.Conexao()
    string_valores = ""
    string_del = ""

    try:
        with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
            vars_aux = json.load(json_data)
            intervalo = vars_aux['intervalo_delay_saldos_segundos']
    except Exception as e:
        intervalo = 300

    # Otemos a lista de registros a serem atualizados
    sql = """select id, contaid, saldo_sumario, saldo_estudante,
	          dateupdate, now(),
	          case when dateupdate + interval '""" + str(intervalo) + """ seconds' < now() then
	            'S'
	          else 
	   	    'N'
	          end atualiza
            from fila_atualiza_saldo s 
            where s.dateupdate + interval '""" + str(intervalo) + """ seconds' < now() 
              and not exists
                (
                   select 1
                   from cobrancas c
                   where c.enviada=False
                     and c.contaid = s.contaid
                )
            order by id limit 2000"""
    result = conn_interna.consultar(sql)

    # Para cada registri
    for row in result:
        try:
            string_valores = string_valores + "(" + str(row[0]) + "," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "),"
            string_del = string_del + str(row[0]) + ","
        except Exception as e:
            print(str(e))
            pass

    if string_valores != "":
        string_del = string_del[0:len(string_del)-1]
        string_valores = string_valores[0:len(string_valores)-1]

        sql = """update contas_controle_saldos 
                 set saldo_sumario = v.saldo_sumario,
                     saldo_estudante = v.saldo_estudante,
                     dateupdate=now()
                 from (
                        values """ + string_valores + """
                      ) as v (id, contaid, saldo_sumario, saldo_estudante)
                 where contas_controle_saldos.contaid = v.contaid"""
        conn_interna.manipular(sql)

        sql = "delete from fila_atualiza_saldo where id in(" + string_del + ")"
        conn_interna.manipular(sql)

    del conn_interna

# Rotina utilizada para remocao de faces que tenham sido deletadas no sistema
# processo ocorre apartado, para nao acarretar em problemas de performance na insercao de novas faces
def remove_facial_fila():
    conn_interna = db.Conexao()

    try:
        sql = "select chave from faces_del_elastic limit 100"
        ret = conn_interna.consultar(sql)

        for row in ret:
            chave_id = row[0]
            print("removendo " + chave_id)
            funcoes_elastic.remove_registro(chave_id)

            sql = "delete from faces_del_elastic where chave = %s"
            params = (chave_id,)
            conn_interna.manipularComBind(sql, params)
    except Exception as e:
        print(str(e))
        pass

    del conn_interna

# Rotina utilizada para atualização de matrizes faciais
# As matrizes serao atualizadas apenas quando ocorrer uma atualizacao de fotos no sistema principal (backend),
# Ex: atualizacao via loja, atualizacao via APP
def atualizar_facial_bulk():
    cnt = 0
    cnt_limite = 30
    arrRegistrosInsert = []
    arrRegistrosDel = []
    cnt_registros = 0
    prossegue_proxima_data = True

    # Abrimos o arquivo de sincronismo, para obtermos a data de atualizacao
    try:
        with open(path_atual + "/../../caixa-magica-operacao/sincronismo_facial.json") as json_data_aux:
            config_sinc = json.load(json_data_aux)
            last_sync = config_sinc['lastUpdateTime']
    except:
        last_sync = '0001-01-01T00:00:00.000'

    # Abrimos o arquivo de parametros do elastic search
    try:
        with open(json_param, "r") as fil:
            aux = json.load(fil)
            habilita_es = aux['habilitado']
            indice_facial = aux['indice_facial']
    except Exception as e:
        habilita_es = False
        indice_facial = ""

    pos_timezone = last_sync.find("+")

    if pos_timezone >= 0:
        last_sync = str(last_sync[0:pos_timezone])
    try:
        last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S")

    last_sync = str(last_sync + datetime.timedelta(seconds=0.000)).replace(" ", "T")

    url_inicial = 'Conta/MatrizFacialPaginated'
    print("Iniciando request faces com " + url_inicial)
    r = req.atualizar_facial(url_inicial, last_sync)

    ret = r.json()
    retorno = ret['contas']

    if len(retorno) <= 0:
        return   

    # Abre conexao com o BD
    conn_interna = db.Conexao()

    string_facial = ""
    string_del_facial = ""
    arrElasticInsert = []

    # Para cada registro retornado
    for s in retorno:
        cnt_registros = cnt_registros+1
        dimensao_matriz = 0
        
        arrNome = str(s['nome']).split(" ")
        if len(arrNome) > 0:
            valor_nome = arrNome[0].strip().upper()
        else:
            valor_nome = str(s['nome']).upper()

        metrica = (s['matrizFacial'].replace(';', ','))
        metricaArr = metrica.split(",")
        dimensao_matriz = len(metricaArr)

        doc_elastic_del = '{"contaId": "' + str(s['contaId']) + '"}'

        contaIdIndex = str(s['contaId']) + "_1"
        doc_elastic = '{"arquivoFoto": "'+ str(s['contaId']) + '", "contaId":"'+str(s['contaId'])+'", "contaIdIndex": "'+contaIdIndex+'", "lastUpdate":"'+s['lastUpdateMatrizFacialTime'] +'", "matrizFacial": ['+ metrica + '], "nome":"'+ valor_nome +'"}'
        arrAux=[]
        arrAux.append(doc_elastic)
        arrAux.append(doc_elastic_del)
        arrAux.append(contaIdIndex)
        arrAux.append(str(s['contaId']))
        arrAux.append(dimensao_matriz)

        arrElasticInsert.append(arrAux)

        # atualizamos a data de ultima atualizacao
        config_sinc['lastUpdateTime'] = s['lastUpdateMatrizFacialTime']
        cnt = cnt+1

        # Se atingiu o limite de registros, paramos o looping e efetuamos a acao na base
        if cnt >= cnt_limite or cnt_registros == len(retorno):
            cnt = 0
            arrRegistrosInsert.append(string_facial)
            arrRegistrosDel.append(string_del_facial)
            string_facial = ""
            string_del_facial=""

    # Inserimos conteudo no Elastic Search
    for reg_es in arrElasticInsert:
        chave_id = reg_es[2]
        dimensao_matriz = reg_es[4]
    
        #print(chave_id + " " + str(dimensao_matriz))

        # Se a dimensao existe, temos foto e devemos atualiza-la no BD
        if dimensao_matriz > 1:
            #print("Inserindo " + str(chave_id))
            ret_elastic = funcoes_elastic.insere_registro(reg_es[0], chave_id, "", False, dimensao_matriz)
            
            # se ocorreu algum erro aqui, nao devemos prosseguir com a busca por novos registros
            if ret_elastic != "":
                prossegue_proxima_data = False

                # Se o erro foi de conexao com o Elastic, abortamos a execucao
                if "Connection error" in ret_elastic:
                    #print("Erro conexao Elastic")
                    return

                #print("Ret elastic: " + ret_elastic)
        else:
            # Inserimos na fila de registros a serem deletados
            sql = "insert into faces_del_elastic (chave, dateinsert) values (%s, now() at time zone 'utc') on conflict (chave) do nothing"
            paramsDel = (chave_id,)
            conn_interna.manipularComBind(sql, paramsDel)

        # Inserimos na tabela de atualizacao para as linhas
        sql = "insert into facial_fila_linhas (contaid, dateinsert) values (%s, now() at time zone 'utc')"
        paramsInsert = (reg_es[3],)
        conn_interna.manipularComBind(sql, paramsInsert)

    if prossegue_proxima_data:
        last_sync = config_sinc['lastUpdateTime']
        pos_timezone = last_sync.find("+")

        if pos_timezone >= 0:
            last_sync = str(last_sync[0:pos_timezone])
        try:
            last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S")

        last_sync = str(last_sync + datetime.timedelta(seconds=0.001)).replace(" ", "T")

        config_sinc['lastUpdateTime'] = last_sync
        with open(path_atual +'/../../caixa-magica-operacao/sincronismo_facial.json', 'w') as f: 
            f.write(json.dumps(config_sinc))
        f.close()

    # Forca a checagem da contingencia
    os.system("sudo python3 " + path_atual + "/sincronismo_contingencia_contas.py")

    del conn_interna

# Rotina utlizada para atualizacao de matrizes de uma linha especifica
def atualiza_facial_linha_especifica(tabela, string_facial, string_del_facial):
    conn_thread = db.Conexao()
    try:
        sql = """update """ + tabela + """ set dateupdate=now(), nome=v.nome, data=v.data, backend_lastupdatetime=v.backend_lastupdatetime
                     from (values
                           """ + string_facial + """
                          ) as v (nome, conta, data, backend_lastupdatetime)
                     where """+tabela+""".conta = v.conta"""
        conn_thread.manipular(sql)
    except:
        pass
    
    try:
        if string_del_facial != "":
            string_del_facial = string_del_facial[0:len(string_del_facial)-1]
            sql = "delete from " + tabela + " where conta in (" + string_del_facial + ")"
            conn_thread.manipular(sql)
    except:
        pass
    
    del conn_thread

# Rotina de atualizacao de contas, utilizando a tecnica de BULK INSERT/UPDATE
def atualizar_contas_bulk():
    # Abrimos o arquivo de sincronismo, para obtermos a data de atualizacao
    try:
        with open(path_atual + "/../../caixa-magica-operacao/sincronismo.json") as json_data_aux:
            config_sinc = json.load(json_data_aux)
            last_sync = config_sinc['lastSyncAtualizacao']
    except:
        last_sync = '0001-01-01T00:00:00.000'
    pos_timezone = last_sync.find("+")

    #last_sync = '1900-01-01T00:00:00.000'

    if pos_timezone >= 0:
        last_sync = str(last_sync[0:pos_timezone])
    try:
        last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S.%f")
    except:
        last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S")

    last_sync = str(last_sync + datetime.timedelta(seconds=0.000)).replace(" ", "T")

    url_inicial = 'Conta/Paginated'

    r = req.sincronismo_principal(url_inicial, last_sync)
    ret = r.json()
    retorno = ret['contas']

    if len(retorno) <= 0:
        return
    else:
        # Obtemos a linhda da viagem que esta aberta
        arrViagemAberta = funcoes_viagem.get_linha_detalhes_viagem_aberta()

        try:
            linha_id_aberta = arrViagemAberta[0]
        except:
            linha_id_aberta = None

        conn_interna = db.Conexao()

        efetua_bulk = False
        string_contas = ""
        string_saldos = ""
        string_update_saldos = ""
        string_fila_saldos = ""

        for s in retorno:
            efetua_bulk = True

            s['nome'] = funcoes_string.ucase(s['nome'])

            try:
                saldo_estudante = s['saldoEstudante']
            except:
                saldo_estudante = 0

            try:
                beneficioid = s['regraBeneficioId']
            except:
                beneficioid = 0

            try:
                estudante = s['estudante']
            except:
                estudante = False

            try:
                pcd = s['temDireitoAcompanhante']
            except:
                pcd = False

            try:
                acompanhante_pcd = s['acompanhante']
            except:
                acompanhante_pcd = False

            # Nao utilizamos o CPF dentro do validador, por questoes de LGPD
            valor_cpf = '11111111111'
            arrNome = str(s['nome']).split(" ")
            if len(arrNome) > 0:
                valor_nome = arrNome[0].strip().upper()
            else:
                valor_nome = str(s['nome']).upper()

            string_contas = string_contas + "(" + str(s['contaId']) + ",'" + valor_cpf + "','" + str(valor_nome) + "', " + str(s['bloqueado']) + ", " + str(s['temGratuidade']) + "," + str(estudante) + ",'" + str(s['lastUpdateTime']) +"', " + str(pcd) + ", " + str(acompanhante_pcd) + "),"
            string_saldos = string_saldos + "(" + str(s['contaId']) + "," + str(s['saldo']) +",now()," + str(saldo_estudante) + "," + str(beneficioid) + "),"
            string_fila_saldos = string_fila_saldos + "(" + str(s['contaId']) + ",now()," + str(s['saldo']) + "," + str(saldo_estudante) + "),"
            string_update_saldos = string_update_saldos + "(" + str(s['contaId']) + "," + str(beneficioid) + "),"
            config_sinc['lastSyncAtualizacao'] = s['lastUpdateTime']
        
        if efetua_bulk:
            # Primeiro, realizamos o comando para inserir quem ainda nao existe
            string_contas = string_contas[0: len(string_contas)-1]
            sql = """INSERT INTO contas (id_web, cpf, nome, bloqueado, isento, estudante,backend_lastupdatetime, pcd, acompanhante_pcd) values """ + string_contas + """
                     ON CONFLICT (id_web) DO nothing"""
            conn_interna.manipular(sql)

            # Agora, rodamos o comando para atualizar quem ja existe
            sql = """update contas set dateupdate=now(), cpf=v.cpf, nome=v.nome, bloqueado=v.bloqueado, 
                                       isento=v.isento, estudante=v.estudante, backend_lastupdatetime=v.backend_lastupdatetime, pcd = v.pcd, acompanhante_pcd=v.acompanhante_pcd
                     from (values
                           """ + string_contas + """
                          ) as v (id_web, cpf, nome, bloqueado, isento, estudante, backend_lastupdatetime, pcd, acompanhante_pcd)
                     where contas.id_web = v.id_web"""
            conn_interna.manipular(sql)

            # Agora, inserimos os saldos de quem nao possui registros na base
            string_saldos = string_saldos[0: len(string_saldos)-1]
            sql = """INSERT INTO contas_controle_saldos 
                           (contaid, saldo_sumario, dateinsert, saldo_estudante, beneficioid) 
                         values """ + string_saldos + """
                            on conflict (contaid) do nothing"""
            conn_interna.manipular(sql)

            string_update_saldos = string_update_saldos[0:len(string_update_saldos)-1]
            sql = """update contas_controle_saldos
                     set dateupdate=now(),
                         beneficioid=v.beneficioid
                     from (values """ + string_update_saldos + """) as v (contaid, beneficioid)
                     where contas_controle_saldos.contaid = v.contaid
                  """
            conn_interna.manipular(sql)

            # Agora, atualizamos a fila de controle de saldos
            string_fila_saldos = string_fila_saldos[0:len(string_fila_saldos)-1]
            sql = "insert into fila_atualiza_saldo (contaid, dateupdate, saldo_sumario, saldo_estudante) values " + string_fila_saldos + " on conflict (contaid) do nothing"
            conn_interna.manipular(sql)

            sql = """update fila_atualiza_saldo set dateupdate=now(), saldo_sumario=v.saldo_sumario, saldo_estudante=v.saldo_estudante
                     from (values
                           """ + string_fila_saldos + """
                          ) as v (contaid, dateupdate, saldo_sumario, saldo_estudante)
                     where fila_atualiza_saldo.contaid = v.contaid"""
            conn_interna.manipular(sql)

        last_sync = config_sinc['lastSyncAtualizacao']
        pos_timezone = last_sync.find("+")

        if pos_timezone >= 0:
            last_sync = str(last_sync[0:pos_timezone])
        try:
            last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S.%f")
        except:
            last_sync = datetime.datetime.strptime(last_sync, "%Y-%m-%dT%H:%M:%S")

        last_sync = str(last_sync + datetime.timedelta(seconds=0.001)).replace(" ", "T")

        config_sinc['lastSyncAtualizacao'] = last_sync
        with open(path_atual +'/../../caixa-magica-operacao/sincronismo.json', 'w') as f:       
            f.write(json.dumps(config_sinc))

    # Forca a checagem da contingencia
    os.system("sudo python3 " + path_atual + "/sincronismo_contingencia_contas.py")

    del conn_interna
    return

def save_config():
    global config
    with open(path_atual +'/../../caixa-magica-operacao/sincronismo.json', 'w') as f:       
        f.write(json.dumps(config))
        funcoes_logs.insere_log("Salvando sincronismo.json com dados: " + str(config), local)

