from time import sleep
import json
import requests

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"

sys.path.insert(1, path_atual + "/../core/")
import db
import funcoes_logs
import funcoes_temperatura
import endpoints
import funcoes_credenciais_token_rotas as f_cred

sys.path.insert(2, path_atual + '/../discord/')
import functions_discord

local = 'sincronismo_controle_viagens.py'

funcoes_logs.insere_log("Iniciando " + local, local)

INTERVALO_EXEC = 60
TIMEOUT_REQUESTS = 15
INTERVALO_REINTEGRA = 180
QTDE_LIMITE_LOGS = 100

# Checamos se devemos usar autenticação ou nao
usar_auth = f_cred.usar_auth()
detalhes_param_auth = f_cred.obtem_param_auth()

sufixo_rota = ""
if usar_auth:
    sufixo_rota = f_cred.sufixo_rota()

while True:
    funcoes_temperatura.holdProcessTemperature(local)
    executa_chamadas_ws = True
    registro_viagem_id = ""

    funcoes_logs.insere_log("Obtendo URL dos web services da caixa magica", local)
    baseurl = endpoints.urlbase
    funcoes_logs.insere_log("Abrindo conexao com BD", local)
    conn = db.Conexao()

    funcoes_logs.insere_log("Abrindo arquivo de instalacao para obtencao do ID da Caixa", local)
    try:
        with open(path_atual + "/../../caixa-magica-operacao/instalacao.json") as json_data:
            aux = json.load(json_data)
            codigo_acesso = aux['acesso']
            operadora_id = aux['operadora']
            del aux
    except Exception as e:
        funcoes_logs.insere_log("Erro ao abrir instalacao.json: " + str(e), local)
        codigo_acesso = ""
        operadora_id = ""
        funcoes_logs.insere_log("Aberturas viagens nao serao realizadas", local)
        executa_chamadas_ws = False
    try:
        with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            
            try:
                TIMEOUT_REQUESTS = aux['timeout_requests']
            except:
                pass

            try:
                INTERVALO_REINTEGRA = aux['intervalo_reintegra_viagens']
            except:
                pass

            try:
                QTDE_LIMITE_LOGS = aux['num_retentativas_viagem']
            except:
                pass
    except:
        pass

    if executa_chamadas_ws == True:
        # Identificamos casos retidos que possam ser recolocados pra processamento
        sql = """select id
                 from viagem v
                 where v.manter_integra_encerramento = false
                    and v.data_manter_integra_encerramento < now() - interval '""" + str(INTERVALO_REINTEGRA) + """ minutes'"""
        result = conn.consultar(sql)

        for row in result:
            try:
                dados = (str(row[0]), )

                # recoloca para processamento
                sql = """update viagem 
                         set data_manter_integra_encerramento=null,
                             manter_integra_encerramento=true
                         where id = %s"""
                conn.manipularComBind(sql, dados)

                # Elimina os logs de erros anteriores
                sql = """delete from log_integracao_viagem
                         where viagemid = %s
                           and response_status <> '<Response [200]>'
                           and acao='ENCERRAMENTO'"""
                conn.manipularComBind(sql, dados)  
            except Exception as e:
                print(str(e))
                pass

        # Identificamos casos retidos que possam ser recolocados pra processamento
        sql = """select id
                 from viagem v
                 where v.manter_integra = false
                    and v.data_manter_integra < now() - interval '""" + str(INTERVALO_REINTEGRA) + """ minutes'"""
        result = conn.consultar(sql)

        for row in result:
            try:
                dados = (str(row[0]), )

                # recoloca para processamento
                sql = """update viagem 
                         set data_manter_integra=null,
                             manter_integra=true
                         where id = %s"""
                conn.manipularComBind(sql, dados)

                # Elimina os logs de erros anteriores
                sql = """delete from log_integracao_viagem
                         where viagemid = %s
                           and response_status <> '<Response [200]>'
                           and acao='ABERTURA'"""
                conn.manipularComBind(sql, dados)  
            except Exception as e:
                print(str(e))
                pass

        # Parte 1: tentamos efetuar a abertura das viagens que estejam pendentes dentro da caixa magica
        sql = "update viagem set geolocalizacao_abertura ='' where trim(geolocalizacao_abertura) = ','"
        conn.manipular(sql)

        sql = """select v.id, 
                        v.id_viagem_cm, 
                        v.linha_id, 
                        v.motorista_id, 
                        v.horario_viagem_id, 
                        v.viagem_id, 
                        v.dateinsert, 
                        l.codigo codigo_linha,
                        v.geolocalizacao_abertura,
                        v.sentido_inicial,
                        v.status_internet
                from viagem v,
                     linhas l
                where v.dateviagemabertabackend is null
                  and v.linha_id = l.id
                  and v.manter_integra=true
                order by 1"""
        result = conn.consultar(sql)
        num_regs = len(result)
        funcoes_logs.insere_log("Encontrado(s) " + str(num_regs) + " registros de viagens. Iniciando aberturas em backend", local)

        for row in result:
            funcoes_logs.insere_log("Efetuando abertura viagem id interno " + str(row[1]), local)

            url = baseurl + "RegistroViagem" + sufixo_rota
            token_auth = ""
            if not usar_auth:
                h = {'CodigoAcesso': codigo_acesso, 'Content-type': 'application/json'}
            else:
                token_auth = f_cred.obtem_token_atual()
                h = {'codigoAcesso': codigo_acesso, 'Content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

            funcoes_logs.insere_log("Montando header requisicao " + url + ": " + str(h), local)

            responsavelId = row[3]
            viagemId = row[5]
            if viagemId == None or viagemId == 0:
                viagemId = ""

            codigoLinha = row[7]
            if codigoLinha == None:
                codigoLinha = ""

            horarioViagemId = row[4]
            if horarioViagemId == None or horarioViagemId == 0:
                horarioViagemId = ""

            geolocalizacao_abertura = str(row[8])
            sentido_inicial = str(row[9])

            status_internet = str(row[10])
            if status_internet == "ONLINE":
                status_internet = 0
            else:
                status_internet = 3

            if geolocalizacao_abertura == "" or geolocalizacao_abertura == None:
                geolocalizacao_abertura = '0,0'

            payload = {"caixaMagicaGuid": str(row[1]), 
                       "dataInicial": str(row[6]), 
                       "tipo": str(status_internet),
                       "responsavelId": str(responsavelId), 
                       "viagemId": str(viagemId), 
                       "linhaId": str(row[2]), 
                       "codigoLinha": str(codigoLinha), 
                       "horarioViagemId": str(horarioViagemId), 
                       "status": 3, 
                       "sentidoViagem": sentido_inicial, 
                       "geolocalizacao": geolocalizacao_abertura}
            funcoes_logs.insere_log("Efetuando request com payload: " + str(payload), local)
            
            response_status = ""
            response_text = ""
            try:
                r = requests.post(url, data=json.dumps(payload), headers = h, timeout=TIMEOUT_REQUESTS)
                response_status = str(r)
                response_text = str(r.text)

                # Se deu certo
                dados=(str(row[0]), )
                if r.ok:
                    # Gravamos o id na base de dados, indicando que a viagem foi criada
                    funcoes_logs.insere_log("Associando viagem criada no backend com ID local", local)

                    sql = """update viagem 
                             set dateviagemabertabackend=now() at time zone 'utc',
	        	         num_tentativas_integracao_abertura = (num_tentativas_integracao_abertura + 1),
                                 datelastintegr_abertura = now() at time zone 'utc'
                             where id = %s"""

                    funcoes_logs.insere_log("Viagem crida  para id interno " + str(row[1]), local)
                else:
                    funcoes_logs.insere_log("Erro criacao viagem backend para viagem id interno " + str(row[1]) +": " + str(r.text), local)

                    sql = """update viagem 
                             set num_tentativas_integracao_abertura = (num_tentativas_integracao_abertura + 1),
                                 datelastintegr_abertura = now() at time zone 'utc'
                             where id = %s"""
                conn.manipularComBind(sql, dados)

                # Se o status da requisicao foi 401, entao devemos regerar o token
                if "401" in response_status:
                    funcoes_logs.insere_log("Gerando novo token de autenticacao", local,2)
                    f_cred.gera_json_auth()

            except Exception as e:
                response_text = str(e)
                response_status = "Erro Python"
                funcoes_logs.insere_log("Erro chamada para viagem id interno " + str(row[1]) + ": " + str(e), local)

            dados = (str(row[0]), 'ABERTURA', str(url), str(h), str(payload), response_status, response_text, 
                     str(detalhes_param_auth[0]), str(detalhes_param_auth[1]), str(detalhes_param_auth[2]), str(token_auth), 
                    )
            sql = """insert into log_integracao_viagem (viagemid, acao, datalog, url, headers, payload,
                            response_status, response_text,
                            url_token, headers_token, payload_token, response_token)
                            values (%s, %s, now() at time zone 'utc', %s,
                                    %s, %s,
                                    %s, %s,
                                    %s, %s, %s, %s)"""
            conn.manipularComBind(sql, dados)

            # Contabilizamos aqui quantas tentativas ocorreram de integracao sem sucesso
            # Se ultrapassou o limite, suspendemos a integracao temporariamente
            try:
                sql = """select count(*)
                         from log_integracao_viagem v
                         where v.viagemid = %s
                           and v.response_status <> '<Response [200]>'
                           and v.acao = 'ABERTURA'
                         having count(*) >= """ + str(QTDE_LIMITE_LOGS)
                dados = (str(row[0]), )
                resultCheck = conn.consultarComBind(sql, dados)
                    
                for rowCheck in resultCheck:
                    sql = "update viagem set manter_integra=False, data_manter_integra=now() where id = %s"
                    conn.manipularComBind(sql, dados)
            except:
                pass

        funcoes_logs.insere_log("Identificando eventuais registros para encerramento de viagem", local)
    
        # O segundo passo consiste em fechar as viagens no backend que ja tenham sido encerradas dentro da Caixa Magica
        sql = "update viagem set geolocalizacao_encerramento='' where trim(geolocalizacao_encerramento)=',' and dateviagemencerradabackend is null"
        conn.manipular(sql)

        sql = """select id, null registro_viagem_id, id_viagem_cm, 
                    coalesce(data_viagem_encerrada,now() at time zone 'utc') data_viagem_encerrada, 
                    encerramento_id,
                    responsavel_encerramento,
                    geolocalizacao_encerramento
             from viagem 
             where 1=1
               and dateviagemabertabackend is not null 
               and encerramento_id is not null
               and dateviagemencerradabackend is null
               and manter_integra_encerramento = true
             order by 1"""
        result = conn.consultar(sql)
        num_regs = len(result)

        funcoes_logs.insere_log("Identificados " + str(num_regs) + " registros possiveis para encerramento de viagem.", local)

        for row in result:
            funcoes_logs.insere_log("Checando se existem cobrancas pendentes na viagem de ID interno " + str(row[2]), local)
            dados=(str(row[2]), )
            sql = "select count(*) from cobrancas where enviada=false and viagemid=%s"
            result_cob = conn.consultarComBind(sql, dados)

            for row_cob in result_cob:
                if row_cob[0] > 0:
                    funcoes_logs.insere_log("Existem cobrancas ainda nao integradas para a viagem de id interno " + str(row[2]) + ". Encerramento nao sera processado agora.", local)
                else:
                    total_passageiros = 0

                    # pega o total de cobramcas
                    dados=(str(row[2]), )
                    sql = "select count(*) from cobrancas where viagemid=%s"
                    result_cob_total = conn.consultarComBind(sql, dados)
                    for row_total in result_cob_total:
                        total_passageiros = row_total[0]

                    funcoes_logs.insere_log("Cobrancas ja integradas para viagem de id interno " + str(row[2]) + ". Iniciando fechamento via backend", local)

                    url = baseurl + "RegistroViagem"+sufixo_rota+"/Fechar"

                    token_auth = ""
                    if not usar_auth:
                        h = {'CodigoAcesso': codigo_acesso, 'Content-type': 'application/json-patch+json'}
                    else:
                        token_auth = f_cred.obtem_token_atual()
                        h = {'codigoAcesso': codigo_acesso, 'Content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

                    funcoes_logs.insere_log("Montando header requisicao " + url + ": " + str(h), local)

                    geolocalizacao_encerramento = row[6]
                    if geolocalizacao_encerramento == None or geolocalizacao_encerramento == "":
                        geolocalizacao_encerramento = "0,0"

                    payload = { "caixaMagicaGuid": str(row[2]), 
                            "dataTermino": str(row[3]), 
                            "totalPassageiros": total_passageiros, 
                            "idFechamentoViagem": str(row[4]), 
                            "responsavelId": str(row[5]), 
                            "geolocalizacao": str(geolocalizacao_encerramento)
                           }
                    funcoes_logs.insere_log("Efetuando request com payload: " + str(payload), local)
                
                    response_status=""
                    response_text=""
                    try:
                        r = requests.patch(url, data=json.dumps(payload), headers = h, timeout=15)
                        response_status = str(r)
                        response_text = str(r.text)

                        # Se deu certo
                        dados=(str(row[0]), )
                        if r.ok:
                            # Gravamos o id na base de dados, indicando que a viagem foi criada
                            funcoes_logs.insere_log("ID encerramento integrado no backend", local)

                            sql = """update viagem 
                             set dateviagemencerradabackend=now() at time zone 'utc',
                                 datelastintegr_encerramento = now() at time zone 'utc',
                                 num_tentativas_integracao_encerramento = (num_tentativas_integracao_encerramento +1)
                             where id = %s"""

                            funcoes_logs.insere_log("Viagem encerrada integrada com backend para id interno " + str(row[1]), local)
                        else:
                            funcoes_logs.insere_log("Erro encerrar viagem com backend para viagem id interno " + str(row[1]) +": " + str(r.text), local)

                            sql = """update viagem 
                             set datelastintegr_encerramento = now() at time zone 'utc',
                                 num_tentativas_integracao_encerramento = (num_tentativas_integracao_encerramento +1)
                             where id = %s"""
                        conn.manipularComBind(sql, dados)

                        # Se o status da requisicao foi 401, entao devemos regerar o token
                        if "401" in response_status:
                            funcoes_logs.insere_log("Gerando novo token de autenticacao", local,2)
                            f_cred.gera_json_auth()

                    except Exception as e:
                        response_text = str(e)
                        response_status = "Erro Python"
                        funcoes_logs.insere_log("Erro chamada encerrar viagem id interno " + str(row[1]) + ": " + str(e), local)

                    dados = (str(row[0]), 'ENCERRAMENTO', str(url), str(h), str(payload), response_status, response_text, 
                             str(detalhes_param_auth[0]), str(detalhes_param_auth[1]), str(detalhes_param_auth[2]), str(token_auth),
                            )
                    print(dados)
                    sql = """insert into log_integracao_viagem (viagemid, acao, datalog, url, headers, payload,
                            response_status, response_text,url_token, headers_token, payload_token, response_token)
                            values (%s, %s, now() at time zone 'utc', %s,
                                    %s, %s,
                                    %s, %s,
                                    %s, %s, %s, %s)"""
                    conn.manipularComBind(sql, dados)

                    # Contabilizamos aqui quantas tentativas ocorreram de integracao sem sucesso
                    # Se ultrapassou o limite, suspendemos a integracao temporariamente
                    try:
                        sql = """select count(*)
                             from log_integracao_viagem v
                             where v.viagemid = %s
                               and v.response_status <> '<Response [200]>'
                               and v.acao = 'ENCERRAMENTO'
                             having count(*) >= """ + str(QTDE_LIMITE_LOGS)
                        dados = (str(row[0]), )
                        resultCheck = conn.consultarComBind(sql, dados)
                    
                        for rowCheck in resultCheck:
                            sql = "update viagem set manter_integra_encerramento=False, data_manter_integra_encerramento=now() where id = %s"
                            conn.manipularComBind(sql, dados)
                    except:
                        pass

    print("aguardando nova tentativa")
    funcoes_logs.insere_log("Nova tentativa em " + str(INTERVALO_EXEC) + " segundos", local)
    sleep(INTERVALO_EXEC)
