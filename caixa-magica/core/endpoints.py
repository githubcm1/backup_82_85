# Funcao que retorna a sigla do ambiente que esta sendo utilizado, de acordo com a URL de health check do ambiente
# de operacao configurada abaixo.
def getEnv():
    # Se a URL base contem a string ".homolog."...
    if urlbase.find(".homolog.") > 0:
        # Retorna a sigla "HOMOLOG".
        return "HOMOLOG"
    # Se a URL base contem a string ".dev"...
    if urlbase.find(".dev") > 0:
        # Retorna a sigla "DEV".
        return "DEV"
    
    # Se chegou ate aqui e porque o ambiente nao e HOMOLOG nem DEV. Nesse caso, retorna "PROD".
    return "PROD"

# Define a URL de health check do ambiente de operacao
urlbase = "https://api-operacao.buspay.com.br/"

# Define a URL de health check do ambiente de administracao.
urladm = "https://api-administracao.buspay.com.br/"

urlbase="https://api-operacao.buspay.com.br/"
urladm="https://api-administracao.buspay.com.br/"
