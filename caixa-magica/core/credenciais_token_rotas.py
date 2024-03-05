# IMPORTANTE:
# AS CREDENCIAIS FICAM DENTRO DESTE TRECHO DO CODIGO E NAO EM ARQUIVO DE PARAMETRIZACAO, POR QUESTOES DE SEGURANCA.
# COMO O CODIGO FICA ENCRIPTADO, ENTAO HA MENOR CHANCE DE VAZAMENTO DO TOKEN

# Do diretorio local "core" importa o arquivo "endpoints.py".
# Caminho do script: /home/pi/caixa-magica/core/endpoints.py
import endpoints

# Define o ambiente que esta sendo utilizado e grava a sigla correspondente na variavel "ambiente".
ambiente = endpoints.getEnv()

# Se o ambiente utilizado for o de desenvolvimento...
if ambiente == "DEV":
    # Define a URL correta do AWS.
    url = "https://buspaycogdev.auth.us-east-1.amazoncognito.com/oauth2/token"
    
    # Define o payload com os dados a serem enviados na requisicao do metodo do AWS.
    payload = "grant_type=client_credentials&scope=https%3A%2F%2Fapi-operacao.dev.buspay.com.br%2FValidador"
    
    # Define o bearer token a ser informado na chamada do metodo do AWS.
    bearer = "OW1mdjF1bWI4djExanVjc3Npb3Y0YzdjazprZWJpamoyZzk0ODdzb3VwdXA5ZjdsYWhnMmdydHE0Z3JhOHI1OXFiYmh0NnA1NjI3bHQ="
    
    # Define o XSRF-TOKEN a ser passado na chamada do metodo do AWS.
    cookie = "XSRF-TOKEN=1468468b-a324-4382-9004-534f295ad003"

# Se o ambiente utilizado for o de homologacao...
elif ambiente == "HOMOLOG":
    # Define a URL correta do AWS.
    url = "https://buspaycogvalidadorhomolog.auth.sa-east-1.amazoncognito.com/oauth2/token"
    
    # Define o payload com os dados a serem enviados na requisicao do metodo do AWS.
    payload = "grant_type=client_credentials&scope=https%3A%2F%2Fapi-operacao.homolog.buspay.com.br%2FValidador"
    
    # Define o bearer token a ser informado na chamada do metodo do AWS.
    bearer = "NWZxcmRyYnY1aGc3cmJkaDF2dDI2ZTBobXY6djVsZ2ZoazdwNmQ2czNvb2U0OXFjcnUyYzVkYmxwMXAwOHFnY3RhOTdkMDg5OGJxazR2"
    
    # Define o XSRF-TOKEN a ser passado na chamada do metodo do AWS.
    cookie = "XSRF-TOKEN=49241884-a028-41f0-8d7f-f729bbcc1115"

# Se o ambiente utilizado for o de producao...
elif ambiente == "PROD":
    # Define a URL correta do AWS.
    url = "https://buspaycogvalidadorprod.auth.sa-east-1.amazoncognito.com/oauth2/token"
    
    # Define o payload com os dados a serem enviados na requisicao do metodo do AWS.
    payload = "grant_type=client_credentials&scope=https%3A%2F%2Fapi-operacao.buspay.com.br%2FValidador"
    
    # Define o bearer token a ser informado na chamada do metodo do AWS.
    bearer = "M2J2MmRhMTQ3aXZxcm1tN2VwYTVmNmNyMWs6MTBhYzI4YjZhaWkwc21kYzBoYjduazk2dm9hdXQ5aGpxNTlyaDg2cTBzNTY5MnJicDE1Zg=="
    
    # Define o XSRF-TOKEN a ser passado na chamada do metodo do AWS.
    cookie = "XSRF-TOKEN=25a1897c-82cc-4e2f-9a93-68f0b50b3ec9"
