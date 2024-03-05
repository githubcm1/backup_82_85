import socket
import json
import db
import datetime
from datetime import datetime
import os

import sys
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

import funcoes_viagem
import gera_uuid
import funcoes_logs
import funcoes_geo

#Definindo endereços para o Socket
HOST = 'localhost'  # The server's hostname or IP address
PORT = 30030        # The port used by the server
orig  = (HOST, PORT)


# Variáveis globais
global localizacao
global lista_vt
lista_vt = []

local = 'cobranca.py'

# Obtemos a viagem atual
registro_viagem_id = funcoes_viagem.get_viagem_atual()

if registro_viagem_id == "":
    funcoes_logs.insere_log("Nao ha viagem aberta no momento", local, 2)

# Abre uma conexao compartilhada
conn = db.Conexao()

# Gera um registro de saldo base na conta, apenas caso nao exista
def geraControleSaldoBase(contaid):
    funcoes_logs.insere_log("Gerando registro saldo base para conta id " + str(contaid), local, 2)
    dados = (str(contaid), )
    sql = "insert into contas_controle_saldos (contaid, saldo_sumario, dateinsert) values (%s, 0, now()) on conflict (contaid) do nothing"
    conn.manipularComBind(sql, dados)

# Busca Conta de tal ID
def getConta(idUsuario):
    sql = "select nome from contas where id_web = {}".format(idUsuario)
    result = conn.consultar(sql)

    for row in result:
        return row
    return False

# Checa se o usuario possui isencao
def isIsento(idUsuario):
    dados = (str(idUsuario), )
    sql = "select 1 from contas where id_web = %s and (isento=true or pcd=true)"
    result = conn.consultarComBind(sql, dados)

    for row in result:
        return True
    #return False

    # Caso chegou aqui, nao trata-se de um caso de PCD nem isento 100
    # Assim sendo, podemos checar se a pessoa eh um acompanhante de PCD
    return checaAcompanhanteIsento(idUsuario)


#Busca Saldos de tal ID
def getSaldos(idUsuario):
    geraControleSaldoBase(idUsuario)

    global lista_vt

    # Checamos a tabela de saldos local
    # Se estiver engativo, ja bloqueamos
    data = (str(idUsuario),)
    if not isIsento(idUsuario):
        sql = "select saldo_sumario from contas_controle_saldos where contaid = %s and saldo_sumario > -5"
        result = conn.consultarComBind(sql,data)
    else:
        sql = "select saldo_sumario from contas_controle_saldos where contaid = %s"
        result = conn.consultarComBind(sql,data)

    for row in result:
        # Se chegou aqui, usuario tem saldo
        sql = "select * from saldo where conta = {} /*and bloqueado = false*/".format(idUsuario) + " limit 1"
        result = conn.consultar(sql)

        if result is not None:
            if idUsuario not in lista_vt:
                for row in result:
                    saldo = row
                    if row[2] == False:
                        lista_vt.append(idUsuario)
                        return saldo
        
        for row in result:
            saldo = row
            if row[2] == True:
                return saldo

    # Se chegou aqui, pessoa nao tem mais saldo e deve ser bloqueada
    return 'bloqueado'

# Busca se a pessoa pode passar na catraca
def getLiberadoSaldo(contaId):
    # Primeiro, checamos se a conta esta bloqueada em geral
    dados = (str(contaId),)
    sql = "select 1 from contas where id_web=%s and bloqueado = true"
    result = conn.consultarComBind(sql, dados)

    for row in result:
        return False

    # Se a pessoa tem isencao total
    if isIsento(contaId):
        return True

    # Checamos se o sujeito se enquadra como estudante
    #sql = "select 1 from contas where id_web=%s and estudante=true"
    #result = conn.consultarComBind(sql, dados)

    # Se for estudante
    #for row in result:
        # Checamos se a pessoa possui saldo
    #    sql = "select 1 from contas_controle_saldos where contaid=%s and saldo_estudante > 0"
    #    result = conn.consultarComBind(sql, dados)

        # Se tem saldo estudante, usamos o valor daqui
    #    for row in result:
    #        return True

    # Se chegou ate aqui, siginifica que nao tem isencao e nao possui saldo de estudante
    sql = "select 1 from contas_controle_saldos where contaid=%s and (saldo_sumario + saldo_estudante) > -5"
    result = conn.consultarComBind(sql, dados)

    # Se chegou aqui, tem saldo
    for row in result:
        return True

    #Se chegou aqui, nao tem conta bloqueada, mas tambem nao tem saldo
    return False

#Busca Saldos pelo próprio id_web na tabela de Saldo - Condição de apresentação de QR Code
def getSaldoQR(idSaldo):
    global lista_vt

    idUsuario = getContaIDfromSaldoID(idSaldo)
    geraControleSaldoBase(idUsuario)


    # Checamos a tabela de saldos local
    # Se estiver engativo, ja bloqueamos
    sql = """select saldo_sumario 
             from contas_controle_saldos 
             where contaid in
                (
                   select distinct conta from saldo where id_web = """ + str(idSaldo) + """
                ) 
                and saldo_sumario > 0"""
    result = conn.consultar(sql)

    for row in result:
        # Se chegou aqui, usuario tem saldo
        #return row[0]
        sql = "select * from saldo where id_web = {} and bloqueado = false".format(idSaldo)
        result = conn.consultar(sql)

        if result is not None:
            if idUsuario not in lista_vt:
                for row in result:
                    saldo = row
                    if row[2] == False:
                        lista_vt.append(idUsuario)
                        return saldo
        
        for row in result:
            saldo = row
            if row[2] == True:
                return saldo

    # Se chegou aqui, pessoa nao tem mais saldo e deve ser bloqueada
    return 'bloqueado'
    

#Busca Saldos pelo próprio id_web na tabela de Saldo - Condição de apresentação de QR Code
def getContaIDfromSaldoID(idSaldo):
    sql = "select * from saldo where id_web = {}".format(idSaldo)
    result = conn.consultar(sql)

    contaID = None
    if result is not None:
        contaID = result[0][3]
    return contaID

# Rotina que debita o valor da tarifa da viagem ativa do saldo do cliente
def debitaTarifaConta(contaid):
    if isIsento(contaid):
        return False

    estudante = False
    coluna_debitar = "saldo_sumario"

    valor_tarifa = funcoes_viagem.get_preco_passagem_cliente(contaid)
    funcoes_logs.insere_log("Valor da tarifa obtido: " + str(valor_tarifa), local, 2)

    # Checamos se trata-se de um caso de estudante
    sql="select 1 from contas where estudante=true and id_web=%s"
    dados=(str(contaid),)
    result=conn.consultarComBind(sql, dados)

    for row in result:
        estudante = True

    sql = "select saldo_sumario + saldo_estudante from contas_controle_saldos where contaid=%s"
    result = conn.consultarComBind(sql, dados)
    for row in result:
        funcoes_logs.insere_log("Saldo da conta id " + str(contaid) + " antes do debito da tarifa: " + str(row[0]), local, 2)

    # Se for estudante, checamos se tem saldo. Tendo saldo, usamos o residuo de estudante; caso contrario, usamos o residuo principal
    if estudante:
        sql_aux = "select 1 from contas_controle_saldos where contaid=%s and saldo_estudante > -5"
        result=conn.consultarComBind(sql_aux, dados)
        for row in result:
            coluna_debitar = "saldo_estudante"

    dados = (valor_tarifa, str(contaid),)
    sqlUpd = "update contas_controle_saldos set dateupdate=now(), " + coluna_debitar +" =(" + coluna_debitar + " - %s) where contaid=%s"
    funcoes_logs.insere_log("Atualizando saldo da conta id " + str(contaid) + " com o comando: " + sqlUpd, local, 2)
    conn.manipularComBind(sqlUpd, dados)

    # Efetua consulta do saldo atualizado
    dados=(str(contaid),)
    result = conn.consultarComBind(sql, dados)
    for row in result:
        funcoes_logs.insere_log("Saldo da conta id " + str(contaid) + " apos do debito da tarifa: " + str(row[0]), local, 2)


# Pega o sentido da viagem
def getSentidoMotorista():
    try:
        with open(path_atual + "/../../caixa-magica-operacao/sentido_viagem_motorista.json") as json_data:
            aux = json.load(json_data)
            return aux['sentido']
    except Exception as e:
        return 'IDA'

# Checa isencao de um acompanhante de PCD
# REGRA:
# SE O A PESSOA FOR ACOMPANHANTE, DEVEMOS CHECAR SE O PASSAGEIRO IMEDIATAMENTE ERA UM PCD
# SE ESSAS CONDICOES FOREM ATENDIDAS, DEVE-SE APLICAR A ISENCAO PARA O ACOMPANHANTE
def checaAcompanhanteIsento(contaId):
    #return False

    viagemId = funcoes_viagem.get_viagem_atual()
    condicao = False

    # Primeiro, checamos se a pessoa atual enquadra-se como acompanhante
    sql = "select 1 from contas where id_web=%s and acompanhante_pcd=true"
    data = (contaId,)
    result = conn.consultarComBind(sql, data)

    # Se entrou nesta condicao, entao trata-se de um acompanhante
    for row in result:
        # Uma vez que trata-se de acompanhante, checamos se o ultimo passageiro era PCD
        sql = """select 1
                 from cobrancas c,
	              contas co
                 where c.id in
                    (
	                select max(c.id)
	                from cobrancas c 
	                where c.viagemid=%s
	                  and c.contaid is not null
	                  and c.contaid <> %s
                    )	  
                  and c.contaid =co.id_web 
                  and co.pcd =true"""
        data = (viagemId, contaId,)
        result2 = conn.consultarComBind(sql, data)
        
        for row2 in result2:
            # Se chegou aqui, entao temos uma situacao onde trata-se de um acompanhante com PCD
            # Neste caso, aplicar a isencao
            condicao = True

    # Se chegou aqui, trata-se de um caso que nao permite a isencao por acompanhante
    return condicao

def atualizaDetalhesIsencaoCobranca(chavecobranca):
    sql = """select c2.isento, c2.pcd, c2.acompanhante_pcd, c.contaid
from cobrancas c,
	 contas c2 
where c.chavecobranca = %s
  and c.contaid is not null
  and c.contaid =c2.id_web"""
    data = (str(chavecobranca),)
    result = conn.consultarComBind(sql, data)
    
    for row in result:
        isento_acomp_pcd = checaAcompanhanteIsento(row[3])

        sql = """update cobrancas 
                 set isento = %s,
                     pcd = %s,
                     acompanhante_pcd = %s,
                     isento_acompanhante_pcd = %s
                 where chavecobranca = %s"""
        data = (row[0], row[1], row[2], isento_acomp_pcd, str(chavecobranca), )
        conn.manipularComBind(sql, data)

    return

#Recebe ID
def cobrar(data):
    global localizacao
    global passagens_eletronicas
    global passagens_dinheiro 
    global passagens_gratuidades

    # geramos um ID unico
    chavecobranca = gera_uuid.gera_uuid()

    preco_passagem = funcoes_viagem.get_preco_passagem_cliente(data['idConta'])

    # Abre arquivo de status da internet, no momento da cobranca
    status_internet = "INDEFINIDO"

    try:
        with open("/home/pi/caixa-magica-operacao/status_internet.json") as json_data:
            json_internet = json.load(json_data)
            status_internet = json_internet['status']
    except Exception as e:
        print("Erro ao abrir arquivo status_internet.json: ", e)

    try:
        localizacao = funcoes_geo.get_geoloc_recente()
    except Exception as e:
        localizacao = ''
        print("Erro ao abrir 'geolocalizacao' em 'cobranca.py': ", e)
    
    string = data['foto'] if data['foto'] else ''
    tipoIdentificacao = data["tipoIdentificacao"]

    # idSaldo = data["idSaldo"]
    # porValor = data["porValor"]
    now = datetime.utcnow().isoformat()

    if tipoIdentificacao == 8:
        preco_passagem = 0.0

    #Cobrança para dinheiro(5) e gratuidade(8)
    if(tipoIdentificacao == 5 or tipoIdentificacao == 8):
        try:
            dados=(str(preco_passagem), now, str(tipoIdentificacao), str(5), str(string), str(registro_viagem_id), str(localizacao), status_internet, chavecobranca, getSentidoMotorista(),)
            sql = "INSERT INTO cobrancas (valor, dataHora, tipoPagamento, tipoIdentificacao, fotoUsuario, enviada, viagemid, geolocalizacao, status_internet,chavecobranca,sentido) values(%s, %s, %s, %s, %s,false,%s, %s, %s, %s, %s);" 
            conn.manipularComBind(sql,dados)
            return True
        except:
            return False
    else:
        idConta = data["idConta"]
        porValor = data["porValor"]
        matriz_facial = data['matriz_facial']
        range_analise = data['range_analise']
        array_matriz_facial = ",".join(map(str, matriz_facial))

        isento = isIsento(idConta)

        valor_cobranca = preco_passagem

        # Se a pessoa tem isencao
        if isento:
            valor_cobranca = 0        

        # Obtemos aqui o saldo corrente da pessoa
        sql = "select saldo_estudante + saldo_sumario saldo from contas_controle_saldos where contaid=%s"
        dadosConta = (idConta,)
        resultSaldo = conn.consultarComBind(sql, dadosConta)
        saldo_anterior =0
        for row in resultSaldo:
            saldo_anterior = row[0]

        # Cobrança para Vale Transporte
        if porValor == False:
            dados = (str(1), now, str(1), str(tipoIdentificacao), str(string), str(idConta), str(registro_viagem_id), str(localizacao),
                     status_internet, chavecobranca, getSentidoMotorista(), str(isento), saldo_anterior, )
            sql = "INSERT INTO cobrancas (valor, dataHora, tipoPagamento, tipoIdentificacao, fotoUsuario, enviada, contaid, viagemid, geolocalizacao, status_internet, chavecobranca, sentido, isento, check_contas_analise, saldo_anterior_catraca) VALUES(%s,%s,%s,%s, %s,false,%s,%s,%s, %s, %s, %s,%s, false, %s);"
            conn.manipularComBind(sql, dados)

            funcoes_logs.insere_log("Debitando tarifa da conta via cobranca facial - trecho vale Transporte - conta id " + str(idConta), local)
            debitaTarifaConta(idConta)    
        else:
            #Caso seja uma passagem de um Usuário que contenha conta na Buspay, mas SEM BENEFICIO
            dados = (str(valor_cobranca), now, str(2), str(tipoIdentificacao), str(string), str(idConta), str(registro_viagem_id), str(localizacao), status_internet, chavecobranca, getSentidoMotorista(), str(isento), str(range_analise), saldo_anterior, )
            sql = "INSERT INTO cobrancas (valor, dataHora, tipoPagamento, tipoIdentificacao, fotoUsuario, enviada, contaid, viagemid, geolocalizacao, status_internet, chavecobranca, sentido, isento, check_contas_analise, matriz_facial, range_analise, saldo_anterior_catraca) VALUES(%s,%s,%s,%s,%s,false,%s,%s,%s,%s,%s,%s, %s, false, '" + array_matriz_facial + "', %s, %s);"
            conn.manipularComBind(sql, dados)

            funcoes_logs.insere_log("Debitando tarifa da conta via cobranca facial - trecho sem benficio - conta id " + str(idConta), local)
            debitaTarifaConta(idConta)

        # Obtemos aqui o saldo corrente da pessoa (apos passagem)
        sql = "select saldo_estudante + saldo_sumario saldo from contas_controle_saldos where contaid=%s"
        dadosConta = (idConta,)
        resultSaldo = conn.consultarComBind(sql, dadosConta)
        saldo_apos =0
        for row in resultSaldo:
            saldo_apos = row[0]

        sql = "update cobrancas set saldo_apos_catraca=%s where chavecobranca=%s"
        dados = (saldo_apos, chavecobranca,)
        conn.manipularComBind(sql, dados)

        atualizaDetalhesIsencaoCobranca(chavecobranca)


#Recebe ID
def cobrarQRcode(data):
    global localizacao    

    # gera um id unico
    chavecobranca = gera_uuid.gera_uuid()
    
    preco_passagem = funcoes_viagem.get_preco_passagem_cliente(data['contaId'])


    # Abre arquivo de status da internet, no momento da cobranca
    status_internet = "INDEFINIDO"

    try:
        with open("/home/pi/caixa-magica-operacao/status_internet.json") as json_data:
            json_internet = json.load(json_data)
            status_internet = json_internet['status']
    except Exception as e:
        print("Erro ao abrir arquivo status_internet.json: ", e)

    try:
        localizacao = funcoes_geo.get_geoloc_recente()
    except Exception as e:
        localizacao = ''
        print("Erro ao abrir 'geolocalizacao' em 'cobranca.py': ", e)

    string = data['foto'] if data['foto'] else ''
    tipoIdentificacao = data["tipoIdentificacao"]
    contaid = data['contaId']
    porValor = data['porValor']
    qrcode = data['qrcode']
    now = datetime.utcnow().isoformat()

    isento = isIsento(contaid)

    valor_cobranca = preco_passagem

    # Se a pessoa tem isencao
    if isento:
        valor_cobranca = 0

    # Cobrança para Vale Transporte
    if porValor == False:
        dados=(str(1), now, str(1), str(tipoIdentificacao), str(string), str(contaid), str(registro_viagem_id), str(localizacao), status_internet, chavecobranca, getSentidoMotorista(), str(qrcode), str(isento),)
        sql = "INSERT INTO cobrancas (valor, dataHora, tipoPagamento, tipoIdentificacao, fotoUsuario, enviada, contaid, viagemid, geolocalizacao, status_internet, chavecobranca, sentido, chave_qr_code_utilizado, isento, check_contas_analise) VALUES(%s,%s,%s,%s,%s,false,%s,%s,%s, %s, %s, %s, %s, %s, true);"
        conn.manipularComBind(sql, dados)
        debitaTarifaConta(contaid)
    else:
        dados=(str(valor_cobranca), now, str(2), str(tipoIdentificacao), str(string), str(contaid), str(registro_viagem_id), str(localizacao), status_internet, chavecobranca, getSentidoMotorista(), str(qrcode), str(isento),) 
        sql = "INSERT INTO cobrancas (valor, dataHora, tipoPagamento,tipoIdentificacao, fotoUsuario, enviada, contaid, viagemid, geolocalizacao, status_internet, chavecobranca, sentido, chave_qr_code_utilizado, isento,check_contas_analise) VALUES(%s,%s,%s,%s,%s,false,%s,%s,%s, %s, %s, %s, %s, %s, true);"
        conn.manipularComBind(sql, dados)
        debitaTarifaConta(contaid)

    atualizaDetalhesIsencaoCobranca(chavecobranca)

# Rotina que obtem o valor do saldo da pessoa apos uma passagem
def getSaldoPosPassagem(contaid):
    retorno = []

    # Somamos o saldo do estudante
    dados = (contaid, )
    sql = "select sum(coalesce(saldo_sumario,0) + coalesce(saldo_estudante,0)) from contas_controle_saldos where contaid=%s"
    result = conn.consultarComBind(sql, dados)

    for row in result:
        saldo = row[0]
        retorno.append(saldo)

    if isIsento(contaid):
        retorno.append(saldo)
        return retorno
    else:
        valor_tarifa = funcoes_viagem.get_preco_passagem_cliente(contaid)
        saldo = saldo - valor_tarifa
        retorno.append(saldo)

    return retorno

def formaMensagemSaldoPosPassagem(contaid):
    # Obtem saldo antes e depois
    try:
        retorno = getSaldoPosPassagem(contaid)
        retorno[0] = "${:,.2f}".format(retorno[0])
        retorno[1] = "${:,.2f}".format(retorno[1])
        mensagem = "Antes: R" + str(retorno[0]) + "\nAtual: R" + str(retorno[1])
    except:
        mensagem = ""
    return mensagem

