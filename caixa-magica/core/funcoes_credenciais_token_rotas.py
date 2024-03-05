# Importa a biblioteca do PyPI "requests" (envio de requisicoes HTTP).
import requests

# Do diretorio local "core" importa o arquivo "credenciais_token_rotas.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/credenciais_token_rotas.py
import credenciais_token_rotas

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Define o caminho do arquivo JSON que contem o token para autenticacao na chamada dos metodos.
arq_json = '/home/pi/caixa-magica-operacao/auth.json'

# Funcao que retorna uma lista com os dados para autenticacao para chamada dos metodos do AWS.
def obtem_param_auth():
    # Define a URL de metodos do AWS e armazena na variavel "url".
    url = credenciais_token_rotas.url

    # Define o payload com os dados a serem passados na chamada dos metodos do AWS e armazena na variavel "payload".
    payload = credenciais_token_rotas.payload

    # Define o dicionario com os headers a serem passados na chamada dos metodos do AWS e armazena na variavel "headers".
    headers = {
  'Authorization': 'Basic ' + str(credenciais_token_rotas.bearer),
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': credenciais_token_rotas.cookie
              }

    # Inicializa a lista de retorno com valor vazio.
    retorno = []

    # Adiciona a URL de metodos do AWS a lista de retorno.
    retorno.append(url)

    # Adiciona o dicionario de headers a lista de retorno.
    retorno.append(headers)

    # Adiciona o payload a lista de retorno.
    retorno.append(payload)

    # Retorna lista de retorno definida acima.
    return retorno

# Funcao que obtem um novo token de autenticacao para as APIs do AWS e o retorna em uma lista junto com os demais
# dados necessarios para a requisicao da API.
def obtem_token_auth():
    # Obtem a lista de dados para autenticacao das APIs do AWS e a grava na variavel "retorno".
    retorno = obtem_param_auth()
    
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Extrai a URL da API do AWS da lista de dados para autenticacao e grava na variavel "url".
        url = retorno[0]

        # Extrai o payload para requisicao das API do AWS da lista de dados para autenticacao e grava na variavel "payload".
        payload = retorno[2]

        # Extrai o dicionario com os headers para requisicao das API do AWS da lista de dados para autenticacao e grava na variavel "headers".
        headers = retorno[1]

        # Inicializa a lista de retorno da funcao com uma lista vazia.
        retorno = []

        # Adiciona a lista de retorno da funcao a URL da API do AWS.
        retorno.append(url)

        # Adiciona a lista de retorno da funcao o dicionario com os headers para requisicao das APIs do AWS.
        retorno.append(headers)

        # Adiciona a lista de retorno da funcao o payload para requisicao das API do AWS.
        retorno.append(payload)

        # Faz uma requisicao POST para a API de geracao de token de autenticacao e grava o retorno na variavel "response". 
        response = requests.request("POST", url, headers = headers, data = payload)

        # Se o "request.ok" retornou False (ou seja, se o status_code retornado for >= 400)...
        if not response.ok:
            # Adiciona a lista de retorno o texto "SEM TOKEN: " + retorno da requisicao POST.
            retorno.append("SEM TOKEN: " + response.text)

            # Retorna a lista de retorno.
            return retorno
        # Se o "request.ok" retornou True (ou seja, se o status_code retornado for < 400)...
        else:
            # Carrega o JSON retornado pela API de geracao de token e grava na lista "aux".
            aux = json.loads(response.text)

            # Grava o token retornado pela API na variavel "token".
            token = aux['access_token']

            # Adiciona a lista de retorno o token retornado pela API.
            retorno.append(token)

            # Retorna a lista de retorno.
            return retorno

    # Se ocorrer algum erro na chamada da API de geracao de token ou na definicao da lista de retorno...
    except Exception as e:
        # Retorna a lista de retorno.
        return retorno

# Funcao que retorna se deve ser utilizada a autenticacao na chamada dos metodos.
def usar_auth():
    # Define o caminho do arquivo JSON que contem os parametros de autenticacao para chamada dos metodos.
    arq_conf = '/home/pi/caixa-magica-vars/param_auth.json'

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre, no modo leitura (parametro "r"), o arquivo JSON de parametros de autenticacao para chamada dos metodos 
        # e cria uma referencia chamada "fil" para o arquivo.
        with open(arq_conf, 'r') as fil:
            # Le o conteudo do arquivo JSON de parametros de autenticacao para chamada dos metodos e armazena na variavel "aux".
            aux = json.load(fil)

            # Retorna o valor do parametro "uso_auth" do arquivo JSON (valor booleano).
            return aux['uso_auth']
    # Se ocorrer algum erro na abertura e leitura do arquivo JSON de parametros de autenticacao para chamada dos metodos...
    except Exception as e:
        # Retorna o valor "False".
        return False

# Funcao que atualiza o arquivo JSON de parametros de autenticacao com um novo token de autenticacao para chamada
# das APIs do AWS.
def gera_json_auth():
    # Deleta o arquivo JSON de parametros de autenticacao que contem o token invalido ("vencido").
    os.system("sudo rm -f " + arq_json)

    # Se foi indicado que deve utilizar autenticacao na chamada das APIs do AWS...
    if usar_auth():
        # Gera um novo token de autenticacao para chamada das APIs do AWS e grava a lista com os dados de autenticacao
        # na variavel "ret".
        ret = obtem_token_auth()

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Grava na variavel "saida" um string JSON com o token de autenticacao gerado acima.
        saida = '{"token": "' + ret[3] + '"}'
    # Se ocorrer algum erro na leitura do token de autenticacao...
    except:
        # Grava na variavel "saida" um string JSON com token vazio.
        saida = '{"token": ""}'
    
    # Define o comando shell que le o conteudo da variavel "saida" e grava no arquivo JSON de parametros de autenticacao
    # para chamada das APIs do AWS.
    comando = ("sudo echo '" + saida + "' | sudo tee " + arq_json)

    # Execute o comando shell definido acima.
    os.system(comando)

# Funcao que retorna o token de autenticacao atual para chamada das APIs do AWS.
def obtem_token_atual():
    # Inicializa a variavel de retorno da funcao com valor vazio.
    token = ""

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre o arquivo JSON que contem o token de autenticacao das APIs do AWS e cria uma referencia chamada "fil" a ele.
        with open(arq_json) as fil:
            # Le o conteudo do arquivo JSON e grava na variavel "aux".
            aux = json.load(fil)

            # Define o valor da variavel de retorno com o token lido do arquivo JSON.
            token = aux['token']
    # Se ocorrer algum erro na leitura do arquivo JSON com o token de autenticacao das APIs do AWS...
    except Exception as e:
        # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
        # ser substituido por outra instrucao futuramente.
        pass
    
    # Retorna o token de autenticacao das APIs do AWS.
    return token

# Funcao que retorna o sufixo da rota dos metodos do AWS, caso esteja configurado para utilizar a autenticacao
# na chamada dos mesmos.
def sufixo_rota():
    # Se esta configurado para utilizar a autenticacao na chamada dos metodos do AWS...
    if usar_auth():
        # Define o caminho do arquivo JSON que contem os parametros de autenticacao para chamada dos metodos.
        arq_conf = '/home/pi/caixa-magica-vars/param_auth.json'

        # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
        try:
            # Abre, no modo leitura (parametro "r"), o arquivo JSON de parametros de autenticacao para chamada dos metodos 
            # e cria uma referencia chamada "fil" para o arquivo.
            with open(arq_conf, 'r') as fil:
                # Le o conteudo do arquivo JSON de parametros de autenticacao para chamada dos metodos e armazena na variavel "aux".
                aux = json.load(fil)

                # Retorna o valor do parametro "sufixo_rota" do arquivo JSON.
                return aux['sufixo_rota']
        # Se ocorrer algum erro na abertura e leitura do arquivo JSON de parametros de autenticacao para chamada dos metodos...
        except Exception as e:
            # Retorna o valor vazio.
            return ""
    
    # Se chegou ate aqui e porque nao esta configurado para utilizar a autenticacao na chamada dos metodos do AWS. Nesse caso,
    # retorna o valor vazio.
    return ""
