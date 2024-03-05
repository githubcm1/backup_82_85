import time

import sys
import pathlib
import json

path_atual = "/home/pi/caixa-magica/sincronismo"
file_sincronismo = path_atual + "/../../caixa-magica-operacao/sincronismo_beneficios.json"

sys.path.insert(1, path_atual + '/../core/')
import db
import funcoes_logs
import funcoes_temperatura
import endpoints
import funcoes_credenciais_token_rotas as f_cred

import os
import requests

local = 'sincronismo_obtem_beneficios_pontuais.py'

funcoes_logs.insere_log("Iniciando " + local, local)

# Checamos se devemos usar autenticação ou nao
usar_auth = f_cred.usar_auth()
detalhes_param_auth = f_cred.obtem_param_auth()

sufixo_rota = ""
if usar_auth:
    sufixo_rota = f_cred.sufixo_rota()

# Abre arquivo de configuracao, obtendo o ID da empresa
funcoes_logs.insere_log("Abrindo arquivo instalacao.json para obter operadora", local)
try:
    with open(path_atual + "/../../caixa-magica-operacao/instalacao.json") as json_data: 
        conf = json.load(json_data)
        codigo_acesso = conf['acesso']
        operadoraid = conf['operadora']
        bilhetadoraid = conf['bilhetadoraId']
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir instalacao.json: " + str(e), local)

# obtem dados da API
funcoes_logs.insere_log("Abrindo arquivo sincronismo.json para obter prefixo API", local)
try:
    with open(path_atual + '/../../caixa-magica-operacao/sincronismo.json') as json_data:
        conf = json.load(json_data)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir sincronismo.json: " + str(e), local)

baseurl = endpoints.urlbase + "RegraBeneficio/Paginated?bilhetadoraId=" + str(bilhetadoraid)

NOVA_TENTATIVA = 60
TIMEOUT_REQUESTS=15

funcoes_logs.insere_log("Abrindo config.json para determinar tempo de atualizacao", local)
try:
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        conf = json.load(json_data)
        NOVA_TENTATIVA = conf['nova_tentativa_importa_beneficios_pontuais']
        TIMEOUT_REQUESTS = conf['timeout_requests']
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir config.json: " + str(e), local)

def sincronismo_principal(url_final):
    funcoes_logs.insere_log("Entrando em sincronismo_principal()", local)
    #h   = {"CodigoAcesso" : codigo_acesso}
    h = ""
    url = url_final
    funcoes_logs.insere_log("URL " + url, local)
    funcoes_logs.insere_log("Header: " + str(h), local)

    timeout = time.time() + 60
    while True:
        try:
            token_auth = ""
            if not usar_auth:
                h = ""
            else:
                token_auth = f_cred.obtem_token_atual()
                h = {'codigoAcesso': codigo_acesso, 'Content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

            funcoes_logs.insere_log("Efetuando request na url " + url, local)
            r   = requests.get(url,headers=h, timeout=TIMEOUT_REQUESTS)
            if not r.ok:
                # Se o status da requisicao foi 401, entao devemos regerar o token
                if "401" in response_status:
                    funcoes_logs.insere_log("Gerando novo token de autenticacao", local,2)
                    f_cred.gera_json_auth()

                funcoes_logs.insere_log("Erro retorno url " + url + ": " + str(r), local)
                return False
            else:
                funcoes_logs.insere_log("Retorno sucesso url " + url + ": " + str(r), local)
                return r
        except Exception as e:
            funcoes_logs.insere_log("Nova tentativa request na url " + url, local)
            if time.time() > timeout:
                funcoes_logs.insere_log("Esgotadas tentativas request na url " + url, local)
                return False
            time.sleep(1)


# Abre conexao com o banco de dados
conn = db.Conexao()

# Checamos se o arquivo de sincronismo de beneficios existe no sistema
comando = "sudo echo '{\"lastUpdateTime\": \"0001-01-01\"}' | sudo tee " + file_sincronismo
os.system(comando)

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    try:
        # Obtem a data do ultimo sincronismo
        with open(file_sincronismo) as fil:
            aux = json.load(fil)
            lastUpdateTime = aux['lastUpdateTime']
            url_request = baseurl + "&lastUpdateTime=" + str(lastUpdateTime)

        funcoes_logs.insere_log("Buscando dados da linha em " + url_request, local)
        r = sincronismo_principal(url_request)

        # Se houve retorno
        if r.ok:
            registros = r.json()

            try:
                registros = registros['regrasBenefios']
            except:
                continue

            # Se existem registros no retorno
            len_registros = len(registros)

            if len_registros > 0:
                funcoes_logs.insere_log("Numero registros retornados " + url_request + ": " + str(len_registros), local)

                funcoes_logs.insere_log("Iniciando import", local)
                for s in registros:
                    tabela = ""

                    # Apenas beneficios pontuais possuem vigencias de datas
                    if s['descontoBilhetagem'] == True:
                        tabela = "beneficios_pontuais"
                        inicio_desconto =  str(s['dataHoraInicioDescontoBilhetagem'])
                        termino_desconto = str(s['dataHoraFimDescontoBilhetagem'])
                    else:
                        tabela = "beneficios"
                        inicio_desconto='1900-01-01'
                        termino_desconto='9999-12-31'
            
                    valorfixo = 0
                    percentual = 0

                    if s['tipoDesconto'] == 2:
                        percentual = s['valorDesconto']
                    elif s['tipoDesconto'] == 1:
                        valorfixo = s['valorDesconto']

                    # Se ambos valores fixo e percentual forem menor ou igual a ZERO, nao faz sentido inserirmos o beneficio nesta base de dados
                    if percentual <= 0 and valorfixo <= 0:
                        continue
                    else:
                        dados = (str(s['regraBeneficioId']),str(s['nomeBeneficio']), str(s['ativo']), inicio_desconto, termino_desconto, 
                             str(percentual), str(valorfixo),
                             str(s['nomeBeneficio']), str(s['ativo']), inicio_desconto, termino_desconto,
                             str(percentual), str(valorfixo), 
                            )
                        sql = """insert into """ + tabela + """ (id, nome, ativo, validode, validoate, percentual, valorfixo, marcadoativo)
                            values (%s, %s, %s, %s, %s, %s, %s, true)
                            on conflict (id) do
                            update set nome = %s, ativo=%s, validode = %s, 
                                       validoate=%s, 
                                       percentual = %s, valorfixo = %s,
                                       marcadoativo=true, dateupdate=now()"""
                        funcoes_logs.insere_log("Executando sql: " + sql, local)
                        conn.manipularComBind(sql, dados)

                        lastUpdate = str(s['lastUpdateTime'])
                        lastUpdate = lastUpdate[0:len(lastUpdate)-6]
                        comando = "sudo echo '{\"lastUpdateTime\": \"" + lastUpdate + "\"}' | sudo tee " + file_sincronismo
                        os.system(comando)

    except Exception as e:
        print(str(e))
        funcoes_logs.insere_log("Erro execucao: " + str(e), local)
        funcoes_logs.insere_log("Nova tentativa pos-erro em " + str(NOVA_TENTATIVA), local )
        time.sleep(NOVA_TENTATIVA)

    funcoes_logs.insere_log("Nova tentativa em " + str(NOVA_TENTATIVA), local )
    time.sleep(NOVA_TENTATIVA)
