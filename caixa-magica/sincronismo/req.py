'''
req.py
Responsável por realizar as requisições entre a Caixa Mágica e o web service.
Editar o sincronismo.json para mudar o servidor. 
'''
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo/"
sys.path.insert(1, path_atual + '/../core/')

import funcoes_credenciais_token_rotas as f_cred
import endpoints
import gera_uuid
import requests
import json
import datetime
from datetime import timezone
import time
import os
import db
import funcoes_logs
import funcoes_viagem
import funcoes_geo

sys.path.insert(2, path_atual + "/../discord/")
import functions_discord

local = 'req.py' 

funcoes_logs.insere_log("Iniciando " + local, local)

funcoes_logs.insere_log("Abrindo conexao com o BD", local)
conn = db.Conexao()

baseurladm = endpoints.urladm
baseurl = endpoints.urlbase

usar_auth = f_cred.usar_auth()
detalhes_param_auth = f_cred.obtem_param_auth()

sufixo_rota=""
if usar_auth:
    sufixo_rota = f_cred.sufixo_rota()

# Abrindo jsons

# instalacao.json
try:
    with open(path_atual + '/../../caixa-magica-operacao/instalacao.json') as json_data:
        instalacao = json.load(json_data)

        codigo_acesso = instalacao['acesso']
        operadora_id = instalacao['operadora']
        bilhetadora_id = instalacao['bilhetadoraId']

        funcoes_logs.insere_log("Codigo acesso Caixa Magica:" + str(codigo_acesso), local)
        funcoes_logs.insere_log("Operadora da Caixa magica: " + str(operadora_id), local)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir 'instalacao.json' em 'req.py': " + str(e), local)

# config.json
TIMEOUT_HEALTH_CHECK=15
TIMEOUT_REQUESTS = 15
try:
    funcoes_logs.insere_log("Abrindo arquivo config.json", local)
    with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
        configArr = json.load(json_data)
        try:
            TIMEOUT_HEALTH_CHECK = configArr['timeout_health_check']
            TIMEOUT_REQUESTS = configArr['timeout_requests']
            funcoes_logs.insere_log("Assumindo timeout para health_check com valor " + str(TIMEOUT_HEALTH_CHECK) + " de config.json", local)
        except:
            funcoes_logs.insere_log("Variavel timeout_health_check nao definida em config.json. Usando valor padrao " + str(TIMEOUT_HEALTH_CHECK), local )
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir config.json: "+ str(e), local)


def verificacao(onibus_id):
    url = baseurladm + "CaixaMagica/VerificaInstalacao/" + str(onibus_id)
    funcoes_logs.insere_log("*** INICIANDO REQUEST DE VERIFICAÇÃO DE INSTALACAO ***", local)
    timeout = time.time() + 60
    while True:
        try:
            funcoes_logs.insere_log("Verificando instalacao com url " + url, local)
            r = requests.get(url, timeout=TIMEOUT_REQUESTS)
            funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
            return r
        except Exception as e:
            if time.time() > timeout:
                funcoes_logs.insere_log("Excedido número de tentativas com backend, voltando para tela de instalação.", local)
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - VERIFICAÇÃO INSTALAÇÃO. Esperando 5 segundos", local)
            time.sleep(1)

def instalacao(numero_serie, instalacao):
    h = {'content-type': 'application/json'}
    payload = {
        'numeroSerie': numero_serie,
        'onibusId': int(instalacao),
    }
    url = baseurladm + "bilhetagem/administracao/api/CaixaMagica/Instalacao"
    
    funcoes_logs.insere_log("*** INICIANDO REQUEST DE INSTALACAO ***", local)
    timeout = time.time() + 60 
    while True:
        try:
            funcoes_logs.insere_log("Efetuando request instalacao com url " + url, local)
            funcoes_logs.insere_log("Efetuando request instalacao com payload " + str(payload) + ", header=" + str(h), local)
            
            r = requests.put(url, data=json.dumps(payload), headers=h)
            if not r.ok:
                funcoes_logs.insere_log("Erro instalacao: " + str(r.text), local)
                return r
                #return False
            else:
                funcoes_logs.insere_log("Sucesso instalacao: " + str(r.text), local)
                return r
        except Exception as e:
            if time.time() > timeout:
                funcoes_logs.insere_log("Excedido número de tentativas com backend, voltando para tela de instalação.", local)
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - INSTALAÇÃO. Esperando 5 segundos", local)
            time.sleep(1)

# Rotina criada para definicao da chave de encerramento da viagem
# Padrao: matricula_motorista.numero_onibus.dataYYMMDD.horaHHmm.idoperadora
def set_idFechamentoViagem(p_matricula_motorista, p_numero_onibus, p_id_operadora, p_id_web_responsavel):
    idFechamentoViagem = ''
    #idFechamentoViagem = str(p_matricula_motorista) + "." + str(p_numero_onibus) + "." + datetime.datetime.utcnow().strftime('%y%m%d.%H%M') + "." + p_id_operadora
    idFechamentoViagem = str(p_id_operadora) + "." + str(p_matricula_motorista) + "." +datetime.datetime.now().strftime('%y%m%d.%H%M') + "." + str(p_numero_onibus)

    # Associamos o id de encerramento da viagem com a viagem que esta ativa
    funcoes_viagem.set_id_encerramento_viagem(idFechamentoViagem, p_id_web_responsavel)

    with open(path_atual +'/../../caixa-magica-operacao/idFechamentoViagem.json', 'w') as json_data:
        json_data.write('{"idFechamentoViagem":"' + idFechamentoViagem + '"}')

    return idFechamentoViagem

# Atraves dos arquivos de configuracao do sistema, geramos a chave de encerramento
def get_idFechamentoViagem(p_id_operador_fechamento):
    with open(path_atual + '/../../caixa-magica-operacao/instalacao.json', 'r') as json_data:
        r = json.load(json_data)
        p_numero_onibus = r['numeroVeiculo']
        p_id_operadora = r['operadora']

    
    try:
        with open(path_atual+'/../../caixa-magica-operacao/motorista.json', 'r') as json_data:
            r = json.load(json_data)

            try:
                p_matricula_motorista = r['matricula']
                p_motorista_id = r['id_web']
            except:
                p_matricula_motorista = "00000"
                p_motorista_id = r['id_web']
    except:
        p_matricula_motorista = ""
        p_motorista_id = -1

    return set_idFechamentoViagem(p_matricula_motorista, p_numero_onibus, p_id_operadora, p_id_operador_fechamento)

# Funcao que formata o ID de encerramento na tela de encerramento (para facilitar para o motorista)
def getIdFechamentoViagemTela(idFechamento):
    # <data>.<hora>.<ONIBUS>
    idExibicao = ""

    posicao = int(idFechamento.find("."))+1
    idExibicao = idFechamento[posicao: 1000]
    posicao = int(idExibicao.find("."))+1
    idExibicao = idExibicao[posicao: 1000]

    return idExibicao


def get_viagem_responsavel(id_web_motorista):
    retorno = []
    url = baseurladm + "bilhetagem/administracao/api/Viagem/MatchViagem?ResponsavelId="+str(id_web_motorista)
    h = {"codigoAcesso" : codigo_acesso}

    # Abrimos o arquivo de configuracao, e identificamos o timeout definido
    try:
        with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            try:
                timeout_definido = aux['timeout_viagem_por_responsavel']
            except:
                timeout_definido = 15

            try:
                match_viagens = aux['match_viagens']
            except:
                match_viagens = False
    except Exception as e:
        pass

    # Se o recurso de matching estiver desligado
    if not match_viagens:
        return retorno

    # testamos se o web service responde (health check)
    # se responde, mantemos o timeout definido no passo anterior
    # Caso contrario, timeout curto para forçar a viagem sendo aberta offline
    if not operacao_on():
        timeout_definido = 0.1

    funcoes_logs.insere_log("*** INICIANDO REQUEST DE VIAGEM POR RESPONSAVEL ID ***", local)
    funcoes_logs.insere_log('RESPONSÁVEL ID: ' + str(id_web_motorista), local)
    timeout = time.time() + timeout_definido
    while True:
        try:
            funcoes_logs.insere_log("Obtendo retorno request com url: " + str(url), local)
            funcoes_logs.insere_log("Obtendo retorno request com header: " + str(h), local)
            r = requests.get(url, headers=h, timeout=timeout_definido)
            retorno_ok = r.ok
     
            mock = False
            
            if mock:
                retorno_ok = True

            if not retorno_ok:
                funcoes_logs.insere_log("Retorno erro request viagem por responsavel id: " + str(r.text), local)
                funcoes_logs.insere_log("Não existem viagens para esse operador.", local)
                return retorno
            else:
                funcoes_logs.insere_log("Formando chave de encerramento da viagem", local)
                
                if mock:
                    print("MOCK")
                    retorno = []
                    retorno.append("51")
                    retorno.append("1")
                    retorno.append("901")
                    retorno.append(20188)
                    retorno.append("691")
                    retorno.append("1")
                    return retorno
                
                json_aux = json.loads(r.text)

                # Retornamos o id da linha, turno, Linha, viagemid, horarioviagemid, sentidoviagemid
                retorno = []
                retorno.append(str(json_aux['data']['linhaId']))
                retorno.append(str(json_aux['data']['turno']))
                retorno.append(str(json_aux['data']['codigoLinha']))
                retorno.append(str(json_aux['data']['viagemId']))
                retorno.append(str(json_aux['data']['horarioViagemId']))
                retorno.append(str(json_aux['data']['sentidoViagem']))

                return retorno
        except Exception as e:
            if time.time() > timeout:
                funcoes_logs.insere_log("Excedido número de tentativas com backend, voltando para tela inicial.", local)
                retorno = []
                return retorno
            funcoes_logs.insere_log("Erro ao se comunicar com backend - GET RESPONSÁVEL ID. Esperando 5 segundos", local)
            time.sleep(1)

def get_linha_id(codigo_linha):
    # Este metodo busca a linha DENTRO da Caixa Magica, e nao no servidor
    # Isso se justifica pelo fato de que as viagens podem ser abertas sem a necessidade de uma
    # conexao com a internet no momento
    conn1 = db.Conexao()

    funcoes_logs.insere_log("Iniciando get_linha_id", local)
    
    # Checamos o id da linha pelo código digitado
    dados = (str(codigo_linha),)
    sql = "select id, nome from linhas where codigo = %s and ativa=true limit 1"
    result = conn1.consultarComBind(sql, dados)
    for row in result:
        funcoes_logs.insere_log("Linha ID " + str(row[0]) + " encontrada para a linha informada " + str(codigo_linha), local)
        row_saida = ['', '', '', '', '']
        row_saida[0] = row[0]
        row_saida[1] = row[1]
        row_saida[2] = ""
        row_saida[3] = ""
        row_saida[4] = ""

        # A partir deste trecho, tentamos obter a escala por linha
        #url = baseurladm + "Viagem/PorCodigoLinha/" + str(codigo_linha)
        #h = {"CodigoAcesso" : codigo_acesso}
        
        #try:
        #    r = requests.get(url, headers=h, timeout=2)#TIMEOUT_REQUESTS)
        #    if not r.ok:
        #        funcoes_logs.insere_log("Resposta chamada " + url + ":" + r.text, local)
        #        funcoes_logs.insere_log("Não existem viagens para essa linha", local)
        #    else:
        #        response = r.json()
        #        funcoes_logs.insere_log("Resposta chamada " + url + ":" + r.text, local)
        #        funcoes_logs.insere_log("Existem viagens para essa linha id.", local)
        #        try:
        #            row_saida[2] = response['id']
        #        except:
        #            pass
        #        try:
        #            row_saida[3] = response['programacaoViagem']['horarioViagens'][0]['id']
        #        except:
        #            pass

        #        try:
        #            row_saida[4] = response['programacaoViagem']['horarioViagens'][0]['horario']
        #        except:
        #            pass
        #except Exception as e:
        #    pass
        return row_saida

    funcoes_logs.insere_log("Linha informada " + str(codigo_linha) + " nao encontrada no BD Local", local)
    return


    #url = baseurl + "Viagem/PorCodigoLinha/" + str(codigo_linha)
    #h = {"CodigoAcesso" : codigo_acesso}

    #funcoes_logs.insere_log("*** INICIANDO REQUEST DE VIAGEM POR LINHA ID ***", local)
    #funcoes_logs.insere_log("VIAGEM ID: " + str(codigo_linha), local)
    #timeout = time.time() + 60
    #while True:
    #    try:
    #        r = requests.get(url, headers=h)
    #        if not r.ok:
    #            funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
    #            funcoes_logs.insere_log("Não existem viagens para essa linha id.", local)
    #            return False
    #        else:
    #            funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
    #            funcoes_logs.insere_log("Existem viagens para essa linha id. Iniciando viagem", local)
    #            return r
    #    except Exception as e:
    #        if time.time() > timeout:
    #            funcoes_logs.insere_log("Excedido número de tentativas com backend, voltando para tela inicial.", local)
    #            return False
    #        funcoes_logs.insere_log("Erro ao se comunicar com backend - GET LINHA ID. Esperando 5 segundos", local)
    #        time.sleep(1)

# Iniciar viagem por código de linha
def iniciar_viagem(tipo, id_web_motorista, status, codigo_linha = None):
    funcoes_logs.insere_log("Entrando iniciar_viagem()", local)

    # Processo modificado
    # Passa agora a gravar os dados da viagem numa tabela local do BD, para depois criarmos a viagem via sincronismo
    try:
        funcoes_logs.insere_log("Removendo arquivo de controle aberto.txt", local)
        os.system("sudo rm -rf " + path_atual + "/../../caixa-magica-operacao/aberto.txt")

        # Primeiro passo consiste em abrir o arquivo inicializacao.json, para obter detalhes da viagem a ser aberta
        linha_id = ""
        viagem_id = ""
        horario_viagem=""
        funcoes_logs.insere_log("Abrindo inicializacao.json para detalhes da viagem", local)
        try:
            with open(path_atual + "/../../caixa-magica-operacao/inicializacao.json", "r") as json_data:
                dados_inicializacao = json.load(json_data)
                linha_id = dados_inicializacao['linhaId']
                horario_viagem = dados_inicializacao['horarioid']
                viagem_id = dados_inicializacao['viagemid']
        except Exception as e:
            funcoes_logs.insere_log("Erro ao abrir inicializacao.json: " + str(e), local)
    
        if viagem_id == "":
            viagem_id = 0
        if horario_viagem == "":
            horario_viagem = 0

        connLocal = db.Conexao()

        # Geramos um ID de viagem
        uuid_viagem = gera_uuid.gera_uuid()

        # Marca as viagens anteriores como nao atuais
        sql = "update viagem set viagem_atual=false where viagem_atual=true"
        connLocal.manipular(sql)

        # Pegamos a geolocalizacao registrada mais recentemente
        geolocalizacao_abertura = funcoes_geo.get_geoloc_recente()

        # Pegamos o sentido inicial da viagem
        sentido_inicial = funcoes_viagem.get_sentido_atual_backend()

        
        # Obtemos o status da internet no momento da abertura
        try:
            with open(path_atual + "/../../caixa-magica-operacao/status_internet.json") as json_data:
                aux = json.load(json_data)
                STATUS_INT = aux['status']
        except:
            STATUS_INT = 'INDEFINIDO' 

        # Inserimos a viagem na tabela de controle
        dados=(uuid_viagem, str(linha_id), str(id_web_motorista), str(viagem_id), str(horario_viagem),
               str(geolocalizacao_abertura), str(sentido_inicial), STATUS_INT,)
        sql="""insert into viagem 
                (id_viagem_cm, 
                 linha_id, 
                 motorista_id, 
                 viagem_atual, 
                 viagem_id, 
                 horario_viagem_id, 
                 geolocalizacao_abertura, 
                 sentido_inicial, status_internet) 
                values 
               (%s, %s, %s, true, %s, %s, %s, %s, %s) on conflict (id_viagem_cm) do nothing;"""
        funcoes_logs.insere_log("Iniciando viagem local com sql: " + sql, local)
        connLocal.manipularComBind(sql, dados)

        funcoes_logs.insere_log("Gerando arquivo de controle aberto.txt", local)
        os.system("sudo touch " + path_atual + "/../../caixa-magica-operacao/aberto.txt")
        
        funcoes_logs.insere_log("Viagem criada na CM com id " + uuid_viagem, local)

        # Pega detalhes da viagem para envio da notificacao via Discord
        sql = """select concat('Aberta viagem na linha ', l.nome, ' pelo operador ', o.nome) mensagem
                 from viagem v,
	              linhas l,
	              operadores o
                 where v.id_viagem_cm ='"""+uuid_viagem+"""'
                   and v.linha_id  = l.id
                   and v.motorista_id = o.id_web"""
        retMensagem = connLocal.consultar(sql)
        for rowMensagem in retMensagem:
            functions_discord.insere_notificacao_fila(rowMensagem[0], 'eventos')

        return True
    except Exception as e:
        funcoes_logs.insere_log("Erro ao iniciar viagem na CM: " + str(e), local)
        return False

def fechar_viagem(total_passagens):
    # viagem.json
    try:
        with open('/home/pi/caixa-magica-operacao/viagem.json') as json_data:
            viagem = json.load(json_data)

            id_viagem = viagem['id']

    except Exception as e:
        print("Erro ao abrir 'viagem.json' em 'req.py': ", e)

    # idFechamentoViagem.json
    try:
        idFechamentoViagem = ''
        with open('/home/pi/caixa-magica-operacao/idFechamentoViagem.json') as json_data:
            FechamentoViagem = json.load(json_data)
            idFechamentoViagem = FechamentoViagem['idFechamentoViagem']
    except Exception as e:
        print("Erro ao abrir 'idFechamentoViagem.json' em 'req.py': ", e)

    url = baseurl + "RegistroViagem"
    h = {'CodigoAcesso': codigo_acesso,
        'content-type': 'application/json'}

    data_fechamento = datetime.datetime.now(timezone.utc).isoformat()
    total_passagens_turno = total_passagens

    payload = {
        'id': id_viagem,
        'dataTermino': data_fechamento,
        'totalPassageiros': total_passagens_turno,
        'idFechamentoViagem': idFechamentoViagem
    }

    funcoes_logs.insere_log("*** INICIANDO REQUEST DE FECHAR REGISTRO VIAGEM ***", local)
    funcoes_logs.insere_log("ENVIO: " + json.dumps(payload), local)
    timeout = time.time() + 60
    while True:
        try:
            r = requests.put(url, data = json.dumps(payload), headers = h)
            if not r.ok:
                funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
                funcoes_logs.insere_log("Erro ao fechar viagem.", local)
                return False
            else:
                funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
                funcoes_logs.insere_log("Viagem iniciada com sucesso.",local)
                os.system("sudo touch /home/pi/caixa-magica-operacao/aberto.txt")
                return r
        except Exception as e:
            if time.time() > timeout:
                funcoes_logs.insere_log("Excedido número de tentativas com backend, voltando para tela de fechamento.", local)
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - PUT VIAGEM. Esperando 5 segundos", local)
            time.sleep(1)


def sincronismo_principal(url_final, last_sync):
    if usar_auth:
        url_final = url_final.replace("Conta/", "Conta" + sufixo_rota + "/")
    url = baseurl + url_final + "?lastUpdateTime=" + str(last_sync) + "&bilhetadoraId="+str(bilhetadora_id)

    funcoes_logs.insere_log("*** INICIANDO REQUEST DO SINCRONISMO PRINCIPAL ***", local)
    timeout = time.time() + 60
    while True:
        try:
            token_auth=""

            # Definimos o header da requisição
            if not usar_auth:
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json'}
            else:
                token_auth = f_cred.obtem_token_atual()
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

            r   = requests.get(url, timeout=TIMEOUT_REQUESTS, headers=h) 
            if not r.ok:
                response_status = str(r)

                if "401" in response_status:
                    f_cred.gera_json_auth()

                return False
            else:
                return r
        except Exception as e:
            if time.time() > timeout:
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - SINCRONISMO PRINCIPAL. Esperando 5 segundos", local)
            time.sleep(1)

def atualizar_facial(url_final, last_sync):
    if usar_auth:
        url_final = url_final.replace("Conta/", "Conta" + sufixo_rota + "/")
    url = baseurl + url_final + "?lastUpdateMatrizFacialTime=" + str(last_sync) + "&bilhetadoraId="+str(bilhetadora_id)

    funcoes_logs.insere_log("*** INICIANDO REQUEST DO SINCRONISMO PRINCIPAL ***", local)
    timeout = time.time() + 60
    while True:
        try:
            token_auth=""

            # Definimos o header da requisição
            if not usar_auth:
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json'}
            else:
                token_auth = f_cred.obtem_token_atual()
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

            r   = requests.get(url, timeout=TIMEOUT_REQUESTS, headers=h) 
            if not r.ok:
                response_status = str(r)

                if "401" in response_status:
                    f_cred.gera_json_auth()

                return False
            else:
                return r
        except Exception as e:
            if time.time() > timeout:
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - atualizar_facial. Esperando 5 segundos", local)
            time.sleep(1)

def enviar_cobrancas(cobrancas):
    url = baseurl + "Cobranca"
    if usar_auth:
        url = url + sufixo_rota

    payload = cobrancas

    funcoes_logs.insere_log("*** INICIANDO REQUEST DA COBRANCA ***", local)
    timeout = time.time() + 60
    while True:
        try:
            token_auth=""

            # Definimos o header da requisição
            if not usar_auth:
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json'}
            else:
                token_auth = f_cred.obtem_token_atual()
                h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

            funcoes_logs.insere_log("URL requests: " + url, local)
            r = requests.post(url, data=json.dumps(payload), headers=h, timeout=TIMEOUT_REQUESTS)

            # Abre conexao com banco de dados local
            conn1 = db.Conexao()

            # registramos o log do request efetuado
            cnt_payload = 0

            while cnt_payload < len(payload):
                sql = """insert into log_integracao_cobranca 
                        (cobrancaid, datalog, url, headers, payload,
                         response_status, response_text,url_token, headers_token, payload_token, response_token)
                     values ((select id from cobrancas where chavecobranca= %s), 
                            now() at time zone 'utc',
                            %s, %s, %s,
                            %s, %s, %s, %s, %s, %s)"""
                dados=(str(payload[cnt_payload]['chavecobranca']), str(url), str(h),str(payload), str(r), str(r.text),
                       str(detalhes_param_auth[0]), str(detalhes_param_auth[1]), str(detalhes_param_auth[2]), str(token_auth),
                      )
                conn1.manipularComBind(sql, dados)

                cnt_payload = cnt_payload +1

            del conn1

            if not r.ok:
                response_status = str(r)

                if "401" in response_status:
                    f_cred.gera_json_auth()

                funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
                funcoes_logs.insere_log("Erro ao enviar cobranças.", local)
                return False
            else:
                funcoes_logs.insere_log("RESPOSTA: " + r.text, local)
                funcoes_logs.insere_log("Cobranças enviadas com sucesso.", local)
                return r
        except Exception as e:
            if time.time() > timeout:
                return False
            funcoes_logs.insere_log("Erro ao se comunicar com backend - ENVIAR COBRANÇA. Esperando 5 segundos", local)
            time.sleep(5)

def receber_operadores():
    retorno = []
    try:
        with open(path_atual + "/../../caixa-magica-operacao/sincronismo_operadores.json") as json_data_op:
            aux = json.load(json_data_op)
            lastUpdateTime = aux['lastUpdateTime']
    except:
        os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/sincronismo_operadores.json")
        os.system("sudo echo '{\"lastUpdateTime\":\"0001-01-01T00:00:00.000\"}' | sudo tee " + path_atual + "/../../caixa-magica-operacao/sincronismo_operadores.json")
        lastUpdateTime = '0001-01-01T00:00:00'

    pos = lastUpdateTime.find("+")

    if pos >= 0:
        lastUpdateTime = lastUpdateTime[0:pos]

    # Tenta chamar o método
    try:
        url = baseurl + "Operador?operadoraId=" + str(operadora_id)+"&lastUpdateTime=" + str(lastUpdateTime)

        token_auth=""

        # Definimos o header da requisição
        if not usar_auth:
            h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json'}
        else:
            token_auth = f_cred.obtem_token_atual()
            h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}
            url = url.replace("Operador?", "Operador" + sufixo_rota + "?")

        r = requests.get(url, headers=h, timeout=TIMEOUT_REQUESTS)
        estrutura = r.json()

        if not r.ok:
            response_status = str(r)

            if "401" in response_status:
                f_cred.gera_json_auth()

            return retorno
        else:
            for row in estrutura:
                fiscal = False
                metrica_face = ''
                
                linha = []
                linha.append(row['operadorId'])
                linha.append(row['usuarioId'])
                linha.append(row['usuarioNome'])
                linha.append("")
                
                try:
                    linha.append(row['matricula'])
                except:
                    linha.append("INDEFINIDA")
                fiscal = row['fiscal']
                linha.append(fiscal)
                linha.append(metrica_face)
                linha.append(row['funcaoId'])
                linha.append(row['funcaoDescricao'])
                linha.append(row['ativo'])
                linha.append(row['lastUpdateTime'])

                try:
                    linha.append(row['cpf'])
                except:
                    linha.append("")

                retorno.append(linha)
        return retorno
    except Exception as e:
        return retorno


def operacao_on():
   try:
       url_health_check = baseurl
       
       funcoes_logs.insere_log("Iniciando checagem 'operacao_on'. URL: " + url_health_check, local)
       r = requests.get(url_health_check, timeout=TIMEOUT_REQUESTS)
       saida = str(r)
       funcoes_logs.insere_log("Resposta http obtida da url " + saida + ": " + saida, local)
       if saida.find("200") == -1:
           funcoes_logs.insere_log("Viagem não será online. Retorno HTTP " + saida, local)
           return False
       else:
           funcoes_logs.insere_log("Viagem online. Retorno HTTP " + saida, local)
           return True
   except Exception as e:
       funcoes_logs.insere_log("Erro em operacao_on. Viagem sera offline: " + str(e), local)
       return False

