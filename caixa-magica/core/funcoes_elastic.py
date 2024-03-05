# Da biblioteca do PyPI "elasticsearch" importa apenas a classe "Elasticsearch" (banco de dados das matrizes para reconhecimento facial).
from elasticsearch import Elasticsearch

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
# import sys

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Da biblioteca padrao do Python "datetime" importa apenas a classe "datetime" (manipulacao de datas e horarios).
# from datetime import datetime

# Importa a biblioteca padrao do Python "threading" (manipulacao de threads para execucao de multiplas tarefas em paralelo).
# import threading

# Importa a biblioteca padrao do Python "multiprocessing" (execucao de multiplos processos em paralelo).
import multiprocessing

# Da biblioteca padrao do Python "time" importa apenas o metodo "sleep" (funcoes para calculos e conversoes de tempo).
# from time import sleep

# Importa a biblioteca do PyPI "requests" (envio de requisicoes HTTP).
import requests

# Declara a variavel global "SEMAFORO".
global SEMAFORO

# Inicialmente, atribui a variavel global "SEMAFORO" o valor "false".
SEMAFORO = False

# Declara a variavel global "GLOBAL_MATRIZ", que armazenara a matriz facial do usuario que esta passando pelo validador.
global GLOBAL_MATRIZ

# Define o diretorio base do script, para facilitar a indicacao de arquivos utilizados neste script.
path_base = "/home/pi/caixa-magica/"

# Define o caminho do arquivo JSON de parametrizacao do Elasticsearch.
json_param = path_base + "../caixa-magica-vars/param_elastic.json"

# Define o caminho do arquivo JSON de parametrizacao dos indices validos do Elasticsearch.
json_param_indices = path_base + "../caixa-magica-vars/param_elastic_indices.json"

# Define o caminho do arquivo que armazena a lista de indices para consulta de matrizes faciais. 
arquivo_indices = path_base + "../caixa-magica-operacao/indices_faciais.txt"

# Define o caminho do arquivo que armazena as linhas dos indices para consulta de matrizes faciais.
arquivo_indices_linhas = path_base + "../caixa-magica-operacao/indices_faciais_linhas.txt"

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Abre o arquivo JSON de parametrizacao do Elasticsearch e armazena o conteudo lido na variavel "fil".
    with open(json_param, "r") as fil:
        # Converte o conteudo do arquivo JSON de parametrizacao do Elasticsearch em array e armazena na variavel "aux".
        aux = json.load(fil)

        # Define o indice para consulta de matrizes faciais a ser utilizado.
        indice_facial = aux['indice_facial']

        # Define a URL para conexao com o Elasticsearch.
        url_es = aux['url']

        # Define o numero limite de registros por indice.
        limite_regs_indice_facial = aux['limite_regs_indice_facial']

        # habilitado = aux['habilitado']
        
        # Define as dimensoes (numero de pontos da matriz faciais) do indice para consulta a ser utilizado.
        dimensoes = aux['indice_dimensoes']

        # Define o score minimo (0 a 1) aceito para o "match" entre a matriz facial do usuario e a matriz lida do Elasticsearch.
        min_score_facial = aux['min_score_facial']

        # Define o nome do indice para consulta de matrizes faciais a ser utilizado.
        indice_facial_linha = aux['indice_facial_linha']

        # Define a URL para a qual e enviada a requisicao do health check do Elasticsearch.
        url_health = aux['health_check']

        # Define o indicador de uso do indice para consulta definido.
        usar_indice_linha = aux['usar_indice_linha']
# Se ocorrer algum erro na leitura do JSON de parametrizacao do Elasticsearch...
except:
    # Define o indice para consulta de matrizes faciais a ser utilizado com valor vazio.
    indice_facial = ""

    # Define a URL para conexao com o Elasticsearch com valor vazio.
    url_es = ""

    # Define o numero limite de registros por indice com valor 100.000.
    limite_regs_indice_facial = 100000

    # habilitado = False
    
    # Define as dimensoes (numero de pontos da matriz faciais) do indice para consulta a ser utilizado com valor 128.
    dimensoes = 128

    # Define o score minimo (0 a 1) aceito para o "match" entre a matriz facial do usuario e a matriz lida do Elasticsearch com valor 0.8 (80%).
    min_score_facial = 0.8

    # Define o indicador de uso do indice para consulta definido com valor "false".
    usar_indice_linha = False

# Declara a variavel global "GLOBAL_RESULTADOS", que armazenara o resultado da consulta da matriz facial do usuario
# no Elasticsearch.
global GLOBAL_RESULTADOS

# Efetua a conexao com o Elasticsearch. O parametro "connections_per_node" indica que cada node aceitara 10 conexoes HTTP para requisicoes concorrentes.
es = Elasticsearch(url_es,connections_per_node=10)

# Obtem os tipos de indices faciais possiveis
# Retorna estrutura contendo: prioridade, indice_dimensoes, indice_facial, limite_regs_indice_facial, total_particoes, limite_fotos_conta, 
# algoritmo, habilita_rec
def lista_conf_indices():
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre o arquivo JSON de parametrizacao dos indices validos do Elasticsearch e armazena o conteudo lido na variavel "fil".
        with open(json_param_indices, "r") as fil:
            # Converte o conteudo do arquivo JSON de parametrizacao dos indices validos do Elasticsearch em array e armazena na variavel "aux".
            aux = json.load(fil)

            # Atribui a variavel arrIndices a estrutura "abaixo" da estrutura principal "indices_faciais".
            arrIndices = aux['indices_faciais']
    
    # Se ocorrer algum erro na leitura do JSON de parametrizacao dos indices validos do Elasticsearch...
    except Exception as e:
        # Finaliza a execucao do metodo.
        return

    # Retorna o array com os dados dos indices validos do Elasticsearch lidos do arquivo JSON.
    return arrIndices

# Consulta a relacao de indices
def lista_indices_faciais():
    ret = []
    indices = es.indices.get_alias().keys()
    soma_registros = 0

    # Pegamos a listagem de indices validos
    arrIndices = lista_conf_indices()

    arrIndicesValidos = []
    for row in arrIndices:
        arrIndicesValidos.append(row['indice_facial'])

    # Lista todos os indices com o prefixo da matriz facial
    for index in indices:
        for indice_check in arrIndicesValidos:
            if indice_check in index:
                aux = []
                aux.append(index)
                aux.append(conta_documentos(index))
                aux.append(limite_regs_indice_facial)
                ret.append(aux)

                soma_registros = soma_registros + aux[1]
    ret = sorted(ret)

    return ret


# Cria a base de matrizes faciais no Elasticsearch (caso nao exista), de acordo com o indice e as dimensoes (numero de pontos
# da matriz) informados como parametros.
def cria_base_facial(param_indice, dimensoes):
    # Define o JSON com o corpo da requisicao para criacao da base de matrizes faciais.
    body = {
          "mappings":
          {
              "properties": {
                  "arquivoFoto": {"type": "keyword"},
                  "contaId": {"type": "keyword"},
                  "contaIdIndex": {"type": "keyword"},
                  "lastUpdate": {"type": "keyword"},
                  "matrizFacial": {
                      "type": "dense_vector",
                      "dims": dimensoes
                  },
                  "nome": {"type": "keyword"}
              }
          }
       }
    
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Cria um index no Elasticsearch com o nome e o corpo da requisicao informados.
        es.indices.create(index=param_indice, body = body)
    # Se ocorrer algum erro na criacao do index no Elasticsearch...
    except Exception as e:
        # Imprime o erro encontrado.
        print(str(e))

        # pass

# Remove uma base de dados
def remove_base_facial(param_indice):
    try:
        es.indices.delete(index=param_indice)
    except Exception as e:
        pass

# Remove documento
def remove_registro(id_doc):
    lista_del = lista_indices_faciais()
    
    for row in lista_del:
        try:
            indice_del = row[0]
            es.delete(index=indice_del, id=id_doc)
        except:
            pass

# Identifica as linhas em que o registro esta vinculado
def lista_linhas_vinculo_conta(id_conta):
    retorno = []

    arrIndices = []
    try:
        with open(arquivo_indices_linhas,"r") as fil:
            lines = [line.rstrip() for line in fil]

            for row in lines:
                arrIndices.append(row)
    except Exception as e:
        pass

    # a partir da linhas, identificamos quais o id da conta consta
    for row in arrIndices:
        try:
            indice = row
            query = {"size": 1,
                 "query": {'match': {'contaId': id_conta} }
                }
            r = es.search(index=indice, body=query)
            hits = r['hits']['hits']
            if len(hits) > 0:
                indice = row
                retorno.append(indice)
        except:
            pass

    return retorno

# Obtem todas as fotos da conta a partir do indice principal
def obtem_registros_conta_indice_principal(id_conta):
    id_doc = str(id_conta) + "_1"
    indice = define_indice_insercao(id_doc, False)
    retorno = []

    if indice != "":
        try:
            query = {"size": 10000,
                 "query": {'match': {'contaId': id_conta} }
                }
            r = es.search(index=indice, body=query)
            hits = r['hits']['hits']

            cnt = 0
            while cnt < len(hits):
                documento = hits[cnt]['_source']
                id_doc = hits[cnt]['_id']
                arrAux = []
                arrAux.append(id_doc)
                arrAux.append(documento)
                retorno.append(arrAux)
                cnt = cnt+1
        except:
            pass

    return (retorno)

# Copia o registro para uma linha especifica
def copia_matriz_facial_para_linha_passagem(id_conta, id_linha):
    indice = indice_facial_linha + "_" + str(id_linha)
    copia_matriz_facial_para_linha(id_conta, indice)

# Copia o registro de uma matriz principal para uma matriz de linha
def copia_matriz_facial_para_linha(id_conta, indice_destino):
    registros = obtem_registros_conta_indice_principal(id_conta)

    for row in registros:
        insere_registro(row[1], row[0], indice_destino)

# move registros da conta referente ao indice principal para os indices de linhas
def copia_matriz_facial_linhas(id_conta):
    registros = obtem_registros_conta_indice_principal(id_conta)

    indices_vinculo = lista_linhas_vinculo_conta(id_conta)
    for indice in indices_vinculo:
        copia_matriz_facial_para_linha(id_conta, indice)


# insere registro na base facial
def insere_registro(documento, id_doc, indice_especifico = "", skip_delete = False, dimensao_matriz=128):
    try:
        if not skip_delete:
            remove_registro(id_doc, indice_especifico)
            pass
    except Exception as e:
        pass

    try:
        if indice_especifico == "":
            indice = define_indice_insercao(id_doc, False, dimensao_matriz)
        else:
            indice = indice_especifico

        es.index(index=indice, document=documento, id=id_doc)

        return ""
    except Exception as e:
        return str(e)

def conta_documentos(indice):
    try:
        ret = es.count(index=indice)
        return (ret['count'])
    except Exception as e:
        return 0

# Efetua a consulta pela matriz facial
def consulta_matriz_facial(indice):
    global GLOBAL_RESULTADOS
    global GLOBAL_MATRIZ

    matriz = GLOBAL_MATRIZ

    try:
        query = {"size": 1,  
             "query": {
                        "script_score": {"query": {"match_all":{}}, 
                            "script":{"source":"cosineSimilarity(params.queryVector, 'matrizFacial')",
                                               "params": {"queryVector": list(matriz) } 
                                                  }
                                        }
                      }
            }

        requests = []
        requests.append('{"index": "'+indice+'"}')
        requests.append(query)

        # Retorna basicamente a estrutura para consulta
        return requests
    except Exception as e:
        #print(str(datetime.utcnow()) + " Encerrando thread " + str(indice) + " " + str(e))
        return

def consulta_msearch_elastic(requests):
    retorno = []
    #print(str(datetime.utcnow()) + " Iniciando query em " + str(requests[0]))
    try:
        retorno = es.msearch(body = requests, request_timeout=20)
        #print(retorno)
    except Exception as e:
        pass    
    #print(str(datetime.utcnow()) + " Encerrando query")
    return retorno

# Efetua a consulta utilizando threads, de forma a checar nas N bases do Elastic Search
def consulta_matriz_facial_thread(matriz, id_linha):
    global GLOBAL_RESULTADOS
    GLOBAL_RESULTADOS = []
    global SEMAFORO
    global GLOBAL_MATRIZ
    GLOBAL_MATRIZ = matriz

    if SEMAFORO:
        return

    SEMAFORO = True

    # REVISAR TRECHO INTEIRO. MATRIZES DE LINHA TAMBEM DEVERAO SER DE 128 OU 512
    # Primeiro, tentamos achar na lista de favoritos da linha
    if id_linha != "" and usar_indice_linha == True:
        indice = indice_facial_linha + "_" + str(id_linha)
        arrIndices=[]
        arrIndices.append(indice)

        NUMBER_OF_PROCESSES = multiprocessing.cpu_count()
        NUMBER_OF_PROCESSES = 10
        pool = multiprocessing.Pool(processes=NUMBER_OF_PROCESSES)

        parametros=[]
        parametros_elastic=[]
        for row in arrIndices:
            parametros.append(row)
        for i in pool.imap_unordered(consulta_matriz_facial, parametros):
            parametros_elastic.append(i)

        # Para cada parametro (header + body)
        requests =[]
        for registro_request in parametros_elastic:
            requests.append(registro_request[0])
            requests.append(registro_request[1])

        r = consulta_msearch_elastic(requests)
        try:
            hits = []
            for row in r['responses']:
                hits.append(row['hits']['hits'])

            for registro in hits:
                try:
                    registro = registro[0]
                    if min_score_facial > registro['_score']:
                        continue

                    arrAux = []
                    arrAux.append(registro['_source']['contaId'])
                    arrAux.append(registro['_source']['contaIdIndex'])
                    arrAux.append(registro['_id'])
                    arrAux.append(registro['_score'])
                    arrAux.append(registro['_index'])
                    arrAux.append(registro['_source']['nome'])
                    GLOBAL_RESULTADOS.append(arrAux)
                except:
                    pass

            ordenados = sorted(GLOBAL_RESULTADOS, key=lambda x:x[3], reverse=True)

            # Se encontrou na lista de favoritos da linha
            if len(ordenados) > 0:
                return ordenados
        except Exception as e:
            pass

    # Se chegou aqui, indica que a consulta nao foi feita por linha ou o retorno na linha nao deu matches
    arrIndices = []
    try:
        with open(arquivo_indices,"r") as fil:
            lines = [line.rstrip() for line in fil]
            
            for row in lines:
                arrIndices.append(row)
    except Exception as e:
        SEMAFORO = False
        return

    NUMBER_OF_PROCESSES = multiprocessing.cpu_count()
    NUMBER_OF_PROCESSES = 10
    pool = multiprocessing.Pool(processes=NUMBER_OF_PROCESSES)

    parametros=[]
    parametros_elastic=[]
    for row in arrIndices:
        parametros.append(row)
    for i in pool.imap_unordered(consulta_matriz_facial, parametros):
        parametros_elastic.append(i)

    # Para cada parametro (header + body)
    requests =[]
    cnt_simult = 1
    for registro_request in parametros_elastic:
        requests.append(registro_request[0])
        requests.append(registro_request[1])
    r = consulta_msearch_elastic(requests)

    hits = []
    for row in r['responses']:
        try:
            hits.append(row['hits']['hits'])
        except:
            pass

    for registro in hits:
        try:
            registro = registro[0]
            if min_score_facial > registro['_score']:
                continue

            arrAux = []
            arrAux.append(registro['_source']['contaId'])
            arrAux.append(registro['_source']['contaIdIndex'])
            arrAux.append(registro['_id'])
            arrAux.append(registro['_score'])
            arrAux.append(registro['_index'])
            arrAux.append(registro['_source']['nome'])
            GLOBAL_RESULTADOS.append(arrAux)
        except:
            pass

    #print("Termino: " + str(datetime.utcnow()) )
    #print("Ocorrencias: " + str(len(GLOBAL_RESULTADOS)))

    ordenados = sorted(GLOBAL_RESULTADOS, key=lambda x:x[3], reverse=True)

    SEMAFORO = False
    return ordenados

# Remove todos os indices (reset base)
def remove_indices_faciais(remove_faciais = True, remove_linhas = True):
    if remove_faciais:
        lista_indices = lista_indices_faciais()
        for reg_indice in lista_indices:
            remove_base_facial(reg_indice[0])

    if remove_linhas:
        lista_indices = lista_indices_faciais_linhas()
        for reg_indice in lista_indices:
            remove_base_facial(reg_indice[0])

# Cria todos os indices a partir da listagem definida
def cria_todos_indices_lista():
    # Busca a lista de indices validos do Elasticsearch e grava na variavel "arrLista".
    arrLista = lista_conf_indices()

    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Para cada indice valido do Elasticsearch da lista acima...
        for row in arrLista:
            # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
            try:
                # Inicializa o contador de particoes criadas com valor zero.
                ini_range = 0

                # Define o limite de particoes de acordo com o configurado na lista de indices validos do Elasticsearch.
                limite_range = row['total_particoes']

                # Enquanto o contador de particoes criadas for menor ou igual ao limite de particoes...
                while ini_range <= limite_range:
                    # Inicializa o contador de fotos por particao com valor um.
                    ini_fotos = 1

                    # Define o limite de fotos por particao de acordo com o configurado na lista de indices validos do Elasticsearch.
                    limite_fotos = row['limite_fotos_conta']

                    # Enquanto o contador de fotos por particao for menor ou igual ao limite de fotos por particao...
                    while ini_fotos <= limite_fotos:
                        # Define a sequencia da particao com o valor do contador de particoes criadas com 4 digitos, preenchendo
                        # com zeros a esquerda.
                        sequencia_particao = "{:04d}".format(ini_range)

                        # Define o ID da particao concatenando o nome do indice, a sequencia da particao definida acima e
                        # o contador de fotos por particao com 3 digitos, preenchendo com zeros a esquerda.
                        particao = row['indice_facial'] + "_" + sequencia_particao + "_" + "{:03d}".format(ini_fotos)

                        # Soma um ao contador de fotos por particao.
                        ini_fotos = ini_fotos + 1

                        # Cria o index no Elasticsearch, de acordo com o ID da particao definido acima e as dimensoes
                        # (numero de pontos da matriz facial) definido no arquivo JSON de configuracao.
                        cria_base_facial(particao, row['indice_dimensoes'])
                        
                        # print(particao)

                    # Soma um ao contador de particoes criadas.
                    ini_range = ini_range + 1
            # Se houver algum erro na criacao dos indices no Elasticsearch...
            except:
                # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
                # ser substituido por outra instrucao futuramente.
                pass
    # Se houver algum erro na leitura da lista de indices validos do Elasticsearch...
    except:
        # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
        # ser substituido por outra instrucao futuramente.
        pass

# cria_todos_indices_lista()
# quit()

# Cria todas as particoes previamente
def cria_todos_indices(limite_range, limite_fotos):
    ini_range = 0

    while ini_range <= limite_range:
        ini_fotos=1
        while ini_fotos <= limite_fotos:
            sequencia_particao = "{:04d}".format(ini_range)
            particao = indice_facial + "_" + sequencia_particao + "_" + "{:03d}".format(ini_fotos)

            ini_fotos = ini_fotos+1
            cria_base_facial(particao, dimensoes)
        ini_range = ini_range+1

# Cria indice especifico pela linha
def cria_indice_linha(linha_id):
    indice = indice_facial_linha + "_" + str(linha_id)
    cria_base_facial(indice, dimensoes)

# Define o prefixo do indice, de acordo com a dimensao especificada
def define_prefixo_indice(dimensao_matriz):
    arrLista = lista_conf_indices()
    for row in arrLista:
        try:
            if dimensao_matriz == row['indice_dimensoes']:
                return row['indice_facial']
        except:
            pass

    return ""

# busca indice a ser inserido o registro
def define_indice_insercao(chave, cria_particao = False, dimensao_matriz = 128):
    arrChave = chave.split("_")
    contaId = int(arrChave[0])
    seq_foto = int(arrChave[1])

    if contaId <= 0:
        contaId = 1
    sequencia_particao = int(contaId / limite_regs_indice_facial)
    sequencia_particao = "{:04d}".format(sequencia_particao)
    particao = str(define_prefixo_indice(dimensao_matriz)) + "_" + sequencia_particao + "_" + "{:03d}".format(seq_foto)

    if cria_particao:
        cria_base_facial(particao, dimensao_matriz)
    
    return particao

# Lista os indices que sao de linhas
def lista_indices_faciais_linhas():
    ret = []
    indices = es.indices.get_alias().keys()
    soma_registros = 0

    # Lista todos os indices com o prefixo da matriz facial
    for index in indices:
        if indice_facial_linha in index:
            aux = []
            aux.append(index)
            aux.append(conta_documentos(index))
            aux.append(limite_regs_indice_facial)
            ret.append(aux)

            soma_registros = soma_registros + aux[1]
    ret = sorted(ret)

    return ret

# Rotina que gera a listagem dos indices possiveis para consulta facial
def define_lista_indices():
    # Primeiro, efetua atualizacao dos indices faciais normais
    lista_indices = lista_indices_faciais()
    soma_registros = 0
    arrIndices = []
    for row in lista_indices:
        if row[1] > 0:
            arrIndices.append(row[0])
            soma_registros = soma_registros + row[1]

    cnt = 0
    limite = len(arrIndices)

    try:
        with open(arquivo_indices, "w") as fil:
            while cnt < limite:
                fil.write(arrIndices[cnt] + "\n")
                cnt=cnt+1
        fil.close()
    except Exception as e:
        pass

    # Agora, efetua atualizacao dos indices faciais de linhas
    lista_indices = lista_indices_faciais_linhas()
    soma_registros = 0
    arrIndices = []
    for row in lista_indices:
        arrIndices.append(row[0])
        soma_registros = soma_registros + row[1]

    cnt = 0
    limite = len(arrIndices)
    
    try:
        with open(arquivo_indices_linhas, "w") as fil:
            while cnt < limite:
                fil.write(arrIndices[cnt] + "\n")
                cnt=cnt+1
        fil.close()
    except Exception as e:
        pass

# Efetua o health check do Elasticsearch (verifica se o servico esta ativo).
def check_elastic_on():
    # Inicialmente, indica que o servico do Elasticsearch nao esta ativo.
    servico_on = False
    
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre uma requisicao GET para a URL do health check e armazena o retorno na variavel "r".
        r = requests.get(url_health)

        # Se a URL do health check retornou "ok"...
        if r.ok:
            # Indica que o servico do Elasticsearch esta ativo.
            servico_on = True
    # Se ocorrer algum erro na abertura de requisicao para a URL do health check do Elasticsearch...
    except Exception as e:
        # Indica que o servico do Elasticsearch nao esta ativo.
        servico_on = False

    # Retorna o indicador de ativo do servico do Elasticsearch.
    return servico_on

