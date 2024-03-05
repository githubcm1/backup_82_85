# Importa a biblioteca padrao do Python "time" (funcoes para calculos e conversoes de tempo).
import time

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Define o diretorio deste script, para facilitar a indicacao de arquivos utilizados neste script.
path_atual = "/home/pi/caixa-magica/sincronismo"

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, path_atual + '/../core/')

# Do diretorio local "core" importa o arquivo "db.py".
# Caminho do script: /home/pi/caixa-magica/core/db.py
import db

# Do diretorio local "core" importa o arquivo "funcoes_logs.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_logs.py
import funcoes_logs

# Do diretorio local "core" importa o arquivo "funcoes_temperatura.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_temperatura.py
import funcoes_temperatura

# Do diretorio local "core" importa o arquivo "endpoints.py".
# Caminho do script: /home/pi/caixa-magica/core/endpoints.py
import endpoints

# Do diretorio local "core" importa o arquivo "funcoes_credenciais_token_rotas.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_credenciais_token_rotas.py
import funcoes_credenciais_token_rotas as f_cred

# Do diretorio local "core" importa o arquivo "funcoes_elastic.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_elastic.py
import funcoes_elastic

# import os

# Importa a biblioteca do PyPI "requests" (envio de requisicoes HTTP).
import requests

# Da biblioteca padrao do Python "datetime" importa apenas a classe "datetime" (manipulacao de datas e horarios).
from datetime import datetime

# Redefine o valor do diretorio atual, para facilitar a indicacao de arquivos utilizados neste script.
# Caminho do diretorio: /home/pi/caixa-magica/scripts_bd
path_atual = path_atual + "/../scripts_bd/"

# Insere nos paths do sistema o diretorio atual definido acima.
sys.path.insert(2, path_atual)

# Le o parametro de utilizacao de autenticacao na chamada dos metodos do AWS, definido no arquivo JSON correspondente,
# e armazena o seu valor na variavel "usar_auth".
usar_auth = f_cred.usar_auth()

# Obtem os parametros de autenticacao para os metodos do AWS e armazena a lista de parametros na variavel "detalhes_param_auth".
# detalhes_param_auth = f_cred.obtem_param_auth()

# Inicializa a variavel de sufixo da rota (que define a versao da API chamada) com valor vazio.
sufixo_rota = ""

# Se esta configurado para utilizar a autenticacao na chamada dos metodos do AWS...
if usar_auth:
    # Busca o sufixo da rota (versao da API) definido no arquivo JSON de configuracao.
    sufixo_rota = f_cred.sufixo_rota()

# Inicialmente, indica que a sincronizacao de dados nao devera ser forcada.
force = False

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Se na chamada deste script foi passado o parametro "force"...
    if sys.argv[1] == "force":
        # Indica que a sincronizacao de dados devera ser forcada.
        force = True
# Se ocorrer algum erro na leitura do parametro passado para o script...
except:
    # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
    # ser substituido por outra instrucao futuramente.
    pass

# Define o nome deste script, para gravacao na tabela de log.
local = 'sincronismo_obtem_linhas.py'

# Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Iniciando " + nome deste script.
funcoes_logs.insere_log("Iniciando " + local, local)

# Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Abrindo arquivo instalacao.json 
# para obter operadora".
funcoes_logs.insere_log("Abrindo arquivo instalacao.json para obter operadora", local)

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Abre o arquivo JSON de parametros da instalacao do validador e cria uma referencia ao arquivo chamada "json_data".
    with open(path_atual + "/../../caixa-magica-operacao/instalacao.json") as json_data: 
        # Le o conteudo do arquivo JSON de parametros da instalacao do validador e grava na variavel "conf".
        conf = json.load(json_data)

        # Define o codigo de acesso a ser passado no header das chamadas das APIs do AWS, conforme parametrizado no arquivo JSON.
        codigo_acesso = conf['acesso']

        # Define o ID da operadora para chamada da API de consulta de linhas, conforme parametrizado no arquivo JSON.
        operadoraid = conf['operadora']
# Se ocorrer algum erro na leitura do arquivo JSON de parametros da instalacao do validador...
except Exception as e:
    # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Erro ao abrir instalacao.json: " +
    # mensagem de erro.
    funcoes_logs.insere_log("Erro ao abrir instalacao.json: " + str(e), local)
    
    # Define com valor vazio o codigo de acesso a ser passado no header das chamadas das APIs do AWS.
    codigo_acesso = ""

    # Define o ID da operadora com valor "-1".
    operadoraid = -1

# Define a URL base das APIs do AWS, conforme definido no arquivo "endpoints.py".
baseurl = endpoints.urlbase

# Define a URL da API de busca de dados das linhas da operadora cujo ID esta no arquivo JSON de parametros da instalacao
# do validador.
url_request = 'OperadoraLinhaTarifa?operadoraId=' + str(operadoraid)

# Se esta configurado para utilizar a autenticacao na chamada dos metodos do AWS...
if usar_auth:
    # Adiciona a URL da API de busca de dados da linha da operadora o sufixo da rota (versao da API).
    url_request = url_request.replace('OperadoraLinhaTarifa?', 'OperadoraLinhaTarifa' + sufixo_rota + '?')

# Define inicialmente como 60 segundos o intervalo entre tentativas de execucao de acoes deste script.
NOVA_TENTATIVA_IMPORTA_LINHAS = 60

# Define o timeout para requisicoes as APIs do AWS.
TIMEOUT_REQUESTS = 15

# Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Abrindo config.json para determinar tempo de atualizacao".
funcoes_logs.insere_log("Abrindo config.json para determinar tempo de atualizacao", local)

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Abre o arquivo JSON de parametros gerais do validador e cria uma referencia a ele com o nome "json_data".
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        # Grava o conteudo do arquivo JSON de parametros gerais do validador na variavel "conf".
        conf = json.load(json_data)
        
        # Atualiza o intervalo entre tentativas de execucao de acoes deste script de acordo com a configuracao no arquivo JSON.
        NOVA_TENTATIVA_IMPORTA_LINHAS = conf['nova_tentativa_importa_linhas']

        # Atualiza o timeout para requisicoes as APIs do AWS de acordo com a configuracao no arquivo JSON.
        TIMEOUT_REQUESTS = conf['timeout_requests']
# Se ocorrer algum erro na leitura do arquivo JSON de parametros gerais do validador...
except Exception as e:
    # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Erro ao abrir config.json: " +
    # mensagem de erro.
    funcoes_logs.insere_log("Erro ao abrir config.json: " + str(e), local)

# Funcao que requisita os dados das linhas da operadora deste validador e retorna esses dados para sincronizacao
# com o banco de dados PostgreSQL local.
def sincronismo_principal(url_final):
    # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Entrando em sincronismo_principal()".
    funcoes_logs.insere_log("Entrando em sincronismo_principal()", local)

    # Define a URL completa da API do AWS a ser chamada para buscar os dados das linhas, concatenando a URL base definida
    # no arquivo "endpoints.py" com a "url_request" definida no inicio deste script.
    url = baseurl + url_final

    # Insere um registro na tabela de log do banco de dados PostgreSQL local com a URL da API do AWS que sera chamada.
    funcoes_logs.insere_log("URL " + url, local)

    # Calcula o numero de segundos do epoch (01/01/1970) ate a data/hora atuais e armazena o valor na variavel "timeout". 
    timeout = time.time()

    # Declara um laco while para executar as proximas instrucoes em loop infinito.
    while True:
        # Inicializa o token para chamada da API do AWS com valor vazio.
        token_auth = ""

        # Se foi indicado que nao deve utilizar a autenticacao na chamada da API do AWS...
        if not usar_auth:
            # Define o dicionario com os headers necessarios para a requisicao da API.
            h = {'CodigoAcesso' : codigo_acesso,'content-type': 'application/json'}
        # Se foi indicado que deve utilizar a autenticacao na chamada da API do AWS...
        else:
            # Obtem o token de autenticacao das APIs do AWS definido no arquivo JSON correspondente e atribui
            # o token a variavel "token_auth".
            token_auth = f_cred.obtem_token_atual()

            # Define o dicionario com os headers para a requisicao da API, contendo o token de autenticacao obtido acima.
            h = {'codigoAcesso': codigo_acesso, 'Content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}

        # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
        try:
            # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Efetuando request na url " +
            # URL da API do AWS.
            funcoes_logs.insere_log("Efetuando request na url " + url, local)
            
            # Envia uma requisicao GET para a URL da API do AWS e grava o retorno na variavel "r".
            r = requests.get(url, headers = h, timeout = TIMEOUT_REQUESTS)
            
            # Se o "request.ok" retornou False (ou seja, se o status_code retornado for >= 400)...
            if not r.ok:
                # Grava o status_code retornado pela API na variavel "response_status".
                response_status = str(r)

                # Se a chamada da API retornou o status_code "401"...
                if "401" in response_status:
                    # Atualiza o arquivo JSON de parametros de autenticacao para chamada das APIs do AWS.
                    f_cred.gera_json_auth()

                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Erro retorno url " + URL da API +
                # retorno da API.
                funcoes_logs.insere_log("Erro retorno url " + url + ": " + str(r), local)
                
                # Retorna False, indicando que nao foi possivel buscar os dados das linhas da operadora.
                return False
            # Se o "request.ok" retornou True (ou seja, se o status_code retornado for < 400)...
            else:
                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Retorno sucesso url " + 
                # URL da API + retorno da API.
                funcoes_logs.insere_log("Retorno sucesso url " + url + ": " + str(r), local)

                # Retorna o resultado da requisicao da API de dados das linhas da operadora.
                return r
        # Se ocorrer algum erro na chamada da API de dados das linhas da operadora...
        except Exception as e:
            # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Nova tentativa request na url " + URL da API.
            funcoes_logs.insere_log("Nova tentativa request na url " + url, local)
            
            # Se o numero de segundos do epoch (01/01/1970) ate a data/hora atuais for maior que o valor gravado na variavel "timeout"...
            if time.time() > timeout:
                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Esgotadas tentativas request na url " + 
                # URL da API.
                funcoes_logs.insere_log("Esgotadas tentativas request na url " + url, local)
                
                # Retorna False, indicando que nao foi possivel buscar os dados das linhas da operadora.
                return False
            
            # Interrompe a execucao do sistema por 1 segundo.
            time.sleep(1)

# Declara um laco while para executar as proximas instrucoes em loop infinito.
while True:
    # Executa a funcao que interrompe a execucao do programa por alguns segundos por superaquecimento da CPU
    # (valido apenas para maquinas Raspberry).
    funcoes_temperatura.holdProcessTemperature(local)

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre o arquivo JSON de parametros gerais do validador e cria uma referencia a ele com o nome "json_data".
        with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
            # Grava o conteudo do arquivo JSON de parametros gerais do validador na variavel "aux".
            aux = json.load(json_data)

            # Atribui o valor de horario de inicio da sincronizacao de dados do validador lido do arquivo JSON
            # de parametros gerais do validador e atribui a "constante" "HORARIO_DE".
            HORARIO_DE = aux['horario_atualizacao_de_importa_linhas']

            # Atribui o valor de horario de termino da sincronizacao de dados do validador lido do arquivo JSON
            # de parametros gerais do validador e atribui a "constante" "HORARIO_ATE".
            HORARIO_ATE = aux['horario_atualizacao_ate_importa_linhas']
    # Se ocorrer algum erro na leitura do arquivo JSON de parametros gerais do validador...
    except Exception as e:
        # Caso o arquivo nao tenha sido carregado, executamos a rotina novamente apos alguns segundos
        time.sleep(NOVA_TENTATIVA_IMPORTA_LINHAS)

        # Interrompe a execucao da iteracao atual do laco "while".
        continue

    # Declara a variavel booleana "prossegue" e, inicialmente, indica que a sincronizacao de dados do validador
    # nao deve prosseguir.
    prossegue = False

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Se o arquivo "/home/pi/caixa-magica-operacao/aberto.txt" existe (ou seja, se ha uma viagem aberta no momento neste validador)
        # e nao foi indicado que deve forcar a sincronizacao de dados (o que ocorre quando a maquina for ligada ou quando a viagem for
        # encerrada)...
        if os.path.exists("/home/pi/caixa-magica-operacao/aberto.txt") and not force:
            # Interrompe a execucao do programa por 1 minuto.
            time.sleep(60)

            # Interrompe a execucao da iteracao atual do laco "while".
            continue

        # Da data/hora UTC atuais, extrai o horario (numero de horas) e converte o valor para inteiro. 
        horario = int(datetime.utcnow().strftime("%H"))

        # Se o horario UTC atual estiver no intervalo permitido para sincronizacao de dados do validador...
        if horario >= HORARIO_DE and horario <= HORARIO_ATE:
            # Indica que deve prosseguir com a sincronizacao de dados.
            prossegue = True

        # Se foi indicado que a sincronizacao de dados deve ser forcada (ou seja, se a maquina esta sendo ligada ou 
        # se a viagem foi encerrada...
        if force:
            # Indica que deve prosseguir com a sincronizacao de dados.
            prossegue = True

        # Se nao indicou que deve prosseguir com a sincronizacao de dados...
        if not prossegue:
            # Interrompe a execucao do programa pelo numero de segundos definido na "constante" "NOVA_TENTATIVA_IMPORTA_LINHAS".
            time.sleep(NOVA_TENTATIVA_IMPORTA_LINHAS)

            # Interrompe a execucao da iteracao atual do laco "while".
            continue

        # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Buscando dados da linha em " + URL da
        # API do AWS.
        funcoes_logs.insere_log("Buscando dados da linha em " + url_request, local)

        # Envia uma requisicao a API de dados de linhas da operadora e armazena o resultado na variavel "r".
        r = sincronismo_principal(url_request)
        
        # Se o "request.ok" da requisicao da API de dados de linhas da operadora retornou True...
        if r.ok:
            # Le o JSON retornado pela API de dados de linhas da operadora e grava os dados extraidos na lista "registros".
            registros = r.json()

            # Grava o numero de registros retornados na variavel "len_registros".
            len_registros = len(registros)

            # Se a API de dados de linhas da operadora retornou algum registro...
            if len_registros > 0:
                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Numero registros retornados " + URL da
                # API do AWS + numero de registros retornados.
                funcoes_logs.insere_log("Numero registros retornados " + url_request + ": " + str(len_registros), local)

                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Marcando linhas existentes para exclusao".
                funcoes_logs.insere_log("Marcando linhas existentes para exclusao", local)

                # Abre uma conexao com o banco de dados PostgreSQL local e cria uma referencia chamada "conn" a ela.
                conn = db.Conexao()

                # Define o comando SQL que inativa todos os registros da tabela "linhas".
                sql = "update linhas set dateupdate = now() at time zone 'utc', marcardelete = true"

                # Executa o comando SQL para inativacao dos registros da tabela "linhas".
                conn.manipular(sql)

                # Fecha conexao com o banco de dados PostgreSQL local.
                del conn

                # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Iniciando import linhas".
                funcoes_logs.insere_log("Iniciando import linhas", local)

                # Para cada registro retornado pela API de dados de linhas da operadora...
                for s in registros:
                    # Abre uma conexao com o banco de dados PostgreSQL local e cria uma referencia chamada "conn" a ela.
                    conn = db.Conexao()
                    
                    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
                    try:
                        # Imprime a mensagem "Criando linha " + ID da linha na tela do terminal.
                        print("Criando linha " + str(s['linhaId']))

                        # Define a tupla com os dados da linha para insercao/atualizacao na tabela "linhas" do banco de dados PostgreSQL local.
                        dados = (s['linhaId'], str(s['codigoPublico']), str(s['codigo']), str(s['codigoPublico']), s['valorTarifa'], 
                                 str(s['codigoPublico']), str(s['codigo']), s['valorTarifa'], str(s['codigoPublico']),)
                        
                        # Define o comando SQL que insere ou atualiza o registro da linha na tabela "linhas" do banco de dados PostgreSQL local.
                        sql = """insert into linhas (id, nome, codigo, codigopublico, valor_tarifa, ativa, dateinsert, marcardelete)
                                 values (%s, %s, %s, %s, %s, true, now() at time zone 'utc', false)
                                 on conflict (id) do
                                 update set nome = %s, codigo = %s, valor_tarifa = %s, ativa = true, codigopublico = %s, 
                                            dateupdate = now() at time zone 'utc', marcardelete = false"""
                        
                        # Insere um registro na tabela de log do banco de dados PostgreSQL local com o texto "Executando sql: " + comando SQL.
                        funcoes_logs.insere_log("Executando sql: " + sql, local)

                        # Executa o comando SQL para insercao/atualizacao do registro da linha na tabela "linhas" do banco
                        # de dados PostgreSQL local.
                        conn.manipularComBind(sql, dados)

                        # Checa a necessidade de criacao da tabela de favoritos da linha (caso a mesma ja nao exista)
                        funcoes_elastic.cria_indice_linha(s['linhaId'])
                        print("Criada linha " + str(s['linhaId']))
                    except Exception as e:
                        funcoes_logs.insere_log("Erro inserir linha " + str(s['linhaId']) + ": " + str(e), local)

                    del conn

                # por fim, rmeovemos os registros marcados para delete
                conn = db.Conexao()
                funcoes_logs.insere_log("Desativando linhas nao retornadas pelo back-end", local)
                sql = "update linhas set ativa=false where marcardelete=true"
                conn.manipular(sql)

    except Exception as e:
        funcoes_logs.insere_log("Erro execucao: " + str(e), local)
        time.sleep(0.01)

        # Se o processo foi executado pelo modo FORCE, entao encerrar os proximos loopings
        if force:
            break

        funcoes_logs.insere_log("Nova tentativa pos-erro em " + str(NOVA_TENTATIVA_IMPORTA_LINHAS), local )
        time.sleep(NOVA_TENTATIVA_IMPORTA_LINHAS)

    # Se o processo foi executado pelo modo FORCE, entao encerrar os proximos loopings
    if force:
        break

    funcoes_logs.insere_log("Nova tentativa em " + str(NOVA_TENTATIVA_IMPORTA_LINHAS), local )
    time.sleep(NOVA_TENTATIVA_IMPORTA_LINHAS)
