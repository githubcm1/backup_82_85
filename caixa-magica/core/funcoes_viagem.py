import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import db
import funcoes_geo
import endpoints
import funcoes_credenciais_token_rotas as f_cred
import json
import requests
import os
from datetime import datetime
import threading

path_semaforo = '/home/pi/caixa-magica-operacao/semaforoleitura.txt'

global codigo_acesso
global timeout_catraca

try:
    with open(path_atual + '/../../caixa-magica-operacao/instalacao.json') as json_data:
        instalacao = json.load(json_data)
        codigo_acesso = instalacao['acesso']
except Exception as e:
    codigo_acesso = ""
    pass

# Pegamos detalhe do timeout da catraca
try:
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        aux = json.load(json_data)
        timeout_catraca = aux['timeout_catraca']
        del aux
except Exception as e:
    timeout_catraca = 5


# Checamos se devemos usar autenticação ou nao
usar_auth = f_cred.usar_auth()
detalhes_param_auth = f_cred.obtem_param_auth()

sufixo_rota = ""
if usar_auth:
    sufixo_rota = f_cred.sufixo_rota()

# Checamos se o id do cliente eh da mesma pessoa que abriu a viagem
# se for, barramos na passagem pela catraca
def checkClienteMotoristaViagem(conta_id, conn_db):
    sql = """select 1
             from viagem v,
	          operadores o,
	          contas c
             where v.viagem_atual =true
               and v.motorista_id  = o.id_web 
               and c.cpf  = o.cpf
               and c.id_web = %s"""
    dados = (conta_id,)
    result = conn_db.consultarComBind(sql, dados)

    # Se trouxe algo, indica que o cliente eh o motorista da viagem
    for row in result:
        return True
    return False

# rotina que busca o total de vendas realizadas (valor real, sem considerar isentos)
def getSomaPassagens():
    viagemid = get_viagem_atual()
    connLocal = db.Conexao()
    dados = (str(viagemid), )
    sql = """select coalesce(sum(valor),0)
             from cobrancas c
             where viagemid =%s"""
    result = connLocal.consultarComBind(sql, dados)
    del connLocal
    for row in result:
        return row[0]

# rotina que busca o total de passagens feitas
def getTotalPassagens():
    viagemid = get_viagem_atual()

    connLocal = db.Conexao()
    dados=(str(viagemid),) 
    sql = """select count(*) from cobrancas
             where viagemid = %s"""
    result = connLocal.consultarComBind(sql, dados)
    del connLocal
    for row in result:
        return row[0]

# rotina que retorna o total de gratuidade
def getTotalGratuidade():
    viagemid = get_viagem_atual()

    connLocal = db.Conexao()
    dados=(str(viagemid),)
    sql = """select count(*) 
             from cobrancas 
             where valor <= 0
               and viagemid =%s"""
    result = connLocal.consultarComBind(sql,dados)
    del connLocal
    for row in result:
        return row[0]

# rotina que pega o total de passagens eletronicas (face + qrcode)
def getTotalPassagensEletr():
    viagemid = get_viagem_atual()
    connLocal = db.Conexao()
    dados = (str(viagemid),)
    sql = """select count(*)
             from cobrancas 
             where viagemid =%s
               and tipopagamento in('2','3')"""
    result = connLocal.consultarComBind(sql,dados)

    del connLocal
    for row in result:
        return row[0]

# rotina que retorna o total de passagens por dinheiro (botoeira)
def getTotalDinheiro():
    viagemid = get_viagem_atual()
    connLocal = db.Conexao()
    dados=(str(viagemid),)
    sql = """select count(*)
             from cobrancas
             where viagemid =%s
               and tipopagamento = '5'
               and valor > 0"""
    result = connLocal.consultarComBind(sql, dados)
    del connLocal
    for row in result:
        return row[0]

def gravaSentido(sentido):
    # Pegamos a geolocalizacao recente
    geoloc = funcoes_geo.get_geoloc_recente()

    connLocal = db.Conexao()

    if sentido == "IDA":
        sentido_base = 1
    else:
        sentido_base = 2

    sql = """insert into viagem_sentido_motorista (id_viagem_cm, codigolinha, motoristaid, dateinsert, sentido, geolocalizacao)
	select id_viagem_cm, linha_id, motorista_id, now(), %s, %s
	from viagem where viagem_atual =true"""

    dados=(str(sentido_base), str(geoloc), )
    connLocal.manipularComBind(sql, dados)

    del connLocal
    return

# Checa se o passageiro pode ser considerado pcd ou nao
def get_passageiro_pcd(contaId):
    conn_interna = db.Conexao()

    dados=(str(contaId), )
    sql = "select 1 from contas where pcd = true and id_web=%s"
    result = conn_interna.consultarComBind(sql, dados)

    del conn_interna

    for row in result:
        return True
    return False

# Checamos se o ultimo passageiro da viagem era PCD ou nao
def get_ultimo_passageiro_pcd():
    conn_pcd = db.Conexao()
    sql = """select c.contaid
from cobrancas c
where c.id in
(
        select max(id)
        from cobrancas c
        where c.viagemid in(select v.id_viagem_cm from viagem v where v.viagem_atual =true)
          and c.contaid is not null
)
  and exists
     (
       select 1
       from contas c2
       where c2.id_web = c.contaid
         and c2.pcd = true
     )"""
    result = conn_pcd.consultar(sql)

    # Se ha retorno, entao o ultimo usuario foi PCD
    for row in result:
        return True
    return False

# Checamos se trata-se de um caso de acompanhante q deve ter gratudade
# Isso ocorre e o passageiro imediatamente anterior for um pcd
def get_gratuidade_acompanhante(contaIdAcompanhante):
    # Checamos se o ultimo usuario foi um PCD
    ultimo_pcd = get_ultimo_passageiro_pcd()

    # Se nao era um pcd, entao esta pessoa nao pode receber gratuidade de acompanhante
    if not ultimo_pcd:
        return False
    else:
        # checamos se a pessoa atual se enquandra como acompanhante
        conn_local = db.Conexao()
        dados=(str(contaIdAcompanhante), )
        sql = "select 1 from contas where acompanhante_pcd = true and id_web = %s"
        result = conn_local.consultarComBind(sql, dados) 
        del conn_local

        # Se retornou algo na consulta acima, entao esta permitida a gratuidade de acompanhante
        for row in result:
            return True

    del conn_local

    return False

# Desmarca eventuais viagens que estejam ativas
# Uso no processo de encerramento da viagem
def set_desmarca_viagem_ativa():
    conn_interna = db.Conexao()
    sql = "update viagem set viagem_atual = false where viagem_atual = true"
    conn_interna.manipular(sql)
    del conn_interna
    return

# determina o ID de encerramento da viagem
def set_id_encerramento_viagem(id_encerramento, id_web_responsavel):
    # Pegamos a geolocalizacao recente
    geoloc = funcoes_geo.get_geoloc_recente()
    
    conn_interna = db.Conexao()
    dados=(str(id_encerramento), str(id_web_responsavel), str(geoloc),)
    sql = "update viagem set encerramento_id =%s, data_viagem_encerrada=(now() at time zone 'utc'), responsavel_encerramento=%s, geolocalizacao_encerramento=%s where viagem_atual =true"
    conn_interna.manipularComBind(sql, dados)
    del conn_interna 
    return

# obtemos detalhes do fechamento da  linha
def get_detalhes_fechamento_viagem():
    conn_interna = db.Conexao()
    sql = """select v.motorista_id responsavelId,
	            coalesce(l.valor_tarifa,0) valor_passagem,
                    v.id_viagem_cm,
	            coalesce(v.dateinsert,now()) dateinsert 
             from viagem v,
	          linhas l
            where v.viagem_atual =true
              and v.linha_id  = l.id"""
    result = conn_interna.consultar(sql)
    del conn_interna
    
    for row in result:
        return row

    # Se chegou ate aqui, retonamos informacoes vazias
    ret = []
    ret.append("")
    ret.append(0.00)
    ret.append("")
    ret.append("1900-01-01 00:00:00")
    return ret

def get_linha_detalhes_viagem_aberta():
    conn_interna = db.Conexao()
    sql = "select id, nome, codigo, codigopublico from linhas l where l.id = (select linha_id from viagem where viagem_atual =true limit 1)"
    result = conn_interna.consultar(sql)
    del conn_interna
    for row in result:
        return row
    return

# Checa nome d alinha
def get_linha_nome():
    conn_interna = db.Conexao()
    sql = "select nome from linhas l where l.id = (select linha_id from viagem where viagem_atual =true limit 1)"
    result = conn_interna.consultar(sql)
    del conn_interna
    for row in result:
        return row[0]
    return

# Checa o id da viagem atual
def get_viagem_atual():
    conn_interna = db.Conexao()
    sql = "select id_viagem_cm from viagem where viagem_atual = true"
    result = conn_interna.consultar(sql)
    del conn_interna
    for row in result:
        return row[0]
    return ""

# Pega id da linha atual
def get_linha_atual():
    conn_interna = db.Conexao()
    sql = "select linha_id from viagem where viagem_atual = true"
    result = conn_interna.consultar(sql)
    del conn_interna
    for row in result:
        return row[0]
    return


# Obtemos o valor da passagem
def get_preco_passagem():
    conn_interna = db.Conexao()
    sql = """select coalesce(max(valor_tarifa),0) from linhas l
	   where l.id in
              (select v.linha_id 
               from viagem v 
               where v.viagem_atual = true)"""
    result = conn_interna.consultar(sql)
    del conn_interna
    for row in result:
        return row[0]
    return

def json_sentido_linha(SENTIDO):
    json_sentido = {'sentido': SENTIDO}
    with open(path_atual + '/../../caixa-magica-operacao/sentido_informado_motorista.json', 'w') as json_data:
        json.dump(json_sentido, json_data)

# Obtemos o sentido corrente
def get_sentido_atual():
    try:
        with open(path_atual + '/../../caixa-magica-operacao/sentido_informado_motorista.json') as json_data:
            aux = json.load(json_data)
            sentido = aux['sentido']
    except:
        sentido = "IDA"

    return sentido

# Obtem o sentido tual dentro do dominio a enviar pro backend
def get_sentido_atual_backend():
    sentido = get_sentido_atual()

    if sentido == "IDA":
        return 1
    else:
        return 2

def informe_sentido_habilitado():
    informe_sentido_habilitado = False
    try:
        with open(path_atual + "/../../caixa-magica-vars/config_sentido_viagem.json") as json_data_aux:
            confAux = json.load(json_data_aux)
            informe_sentido_habilitado = confAux['informe_sentido_habilitado']
            if informe_sentido_habilitado:
                return True
    except:
        pass

    return False

# Busca sentidos deviagens sem integracao com o backend
def getSentidoViagemSemIntegr():
    conn1 = db.Conexao()

    sql = """update viagem_sentido_motorista 
             set geolocalizacao ='' 
             where dateenviadobackend is null 
               and trim(geolocalizacao) = ','"""
    conn1.manipular(sql)

    # Viagem ja deve ter sido enviada ao backend
    sql = """select r.id_viagem_cm, r.id, r.codigolinha, r.motoristaid, r.sentido, 
             r.dateinsert, r.geolocalizacao
           from viagem_sentido_motorista r,
                viagem v
           where r.dateenviadobackend is null 
             and r.id_viagem_cm = v.id_viagem_cm
             and v.dateviagemabertabackend is not null
             and trim(r.geolocalizacao) <> ','
           order by r.id"""
    result = conn1.consultar(sql)

    if len(result) > 0:
        return result
    else:
        return None

# Rotina que integra registros de sentidos com o backend
# Havendo retorno positivo na integracao, marcamos o registro como enviado
def enviaSentidoViagemSemIntegr():

    url = endpoints.urlbase
    url = url + "RegistroViagem/MudarSentido"

    if usar_auth:
        url = url.replace("RegistroViagem", "RegistroViagem" + sufixo_rota)

    # Definimos o header da requisição
    if not usar_auth:
        h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json'}
    else:
        token_auth = f_cred.obtem_token_atual()
        h = {'CodigoAcesso': codigo_acesso,'content-type': 'application/json-patch+json', 'Authorization': 'Bearer ' + token_auth}
    
    # Obtemos o recordset dos registros
    retorno = getSentidoViagemSemIntegr()

    if retorno != None:
        for row in retorno:
            sucesso_envio = False

            # Montamos aqui o payload e chamada do retorno
            geoloc = row[6]
            if geoloc == None or geoloc == "":
                geoloc = '0,0'

            try:
                payload = {"caixaMagicaGuid": str(row[0]), 
		       "sentidoViagem": str(row[4]), 
		       "dataInicio": str(row[5]), 
  		       "responsavelId": str(row[3]), 
		       "geolocalizacao": str(geoloc) }
                # Efetua o request
                print(h)
                print(url)
                r = requests.patch(url, data=json.dumps(payload), headers = h, timeout=10)

                # Registra o envio e retorno em log
                conn1 = db.Conexao()

                sql = """insert into log_integracao_viagem_sentido_motorista
                            (viagem_sentido_motorista_id,
                             datalog,
                             url, headers, payload, response_status, response_text)
                         values (%s, now() at time zone 'utc',
                                 %s, %s, %s, %s, %s)"""
                data = (str(row[1]), url, str(h), str(payload), str(r), str(r.text),)
                conn1.manipularComBind(sql, data)
                del conn1

                if r.ok:
                    sucesso_envio = True
                else:
                    f_cred.gera_json_auth()
            except Exception as e:
                sucesso_envio = False
                f_cred.gera_json_auth()

            if sucesso_envio:
                conn1 = db.Conexao()
                dados=(str(row[1]),)
                # marcamos o registro como enviado na base de dados
                sql = """update viagem_sentido_motorista
                         set dateenviadobackend=(now() at time zone 'utc')
                         where id = %s"""
                conn1.manipularComBind(sql, dados)

                del conn1


def forma_motorista_json():
    viagemid = get_viagem_atual()
    if viagemid != None:
        conn1 = db.Conexao()
        sql = """select nome, id_qr id_qrcode, id_web, matricula
               from operadores o
               where o.id_web = (select motorista_id from viagem where id_viagem_cm = %s)"""
        dados = (viagemid,)
        result = conn1.consultarComBind(sql, dados)
        for row in result:
            conteudoarq = {"nome": row[0],
                           "id_qrcode": row[1],
                           "id_web": row[2],
                           "matricula": row[3]
                          }
            with open(path_atual + "/../../caixa-magica-operacao/motorista.json", "w") as f:
                json.dump(conteudoarq, f)

# Retorna a lista de beneficios pontuais ativos
def get_beneficios_pontuais():
    conn1 = db.Conexao()
    
    sql = """select id, nome, percentual, valorfixo,
                    case when valorfixo > 0 then
                       'false'
                    else 'true'
                    end por_percentual,
                    case when valorfixo > 0 then
                       'true'
                    else 'false'
                    end por_valorfixo,
                    validoate at time zone 'UTC' validoate
	     from beneficios_pontuais bp 
	     where bp.ativo =true 
  	       and now() at time zone 'UTC'  between bp.validode and bp.validoate
             order by 1"""
    result = conn1.consultar(sql)
    del conn1

    return result

# gera arquivo json com os beneficios pontuais especificos do monento
def gera_json_beneficios_pontuais():
    lista = get_beneficios_pontuais()
    
    path_aux = path_atual + "/../../caixa-magica-operacao/beneficios_pontuais.json"

    # Limpa arquivo json existente
    os.system("sudo rm -rf " + path_aux)

    conteudo = ""
    for row in lista:
        if row[2] == None:
            percentual = "0"
        else:
            percentual = row[2]
        if row[3] == None:
            valorfixo = "0"
        else:
            valorfixo = row[3]
        conteudo = conteudo + '{"id": ' + str(row[0]) + ',"nome":"' + row[1] + '", "percentual": ' + str(percentual) + ', "valorfixo": ' + str(valorfixo) + ', "por_percentual": ' + row[4] + ', "por_valorfixo": ' + row[5] + ', "validoate": "' + str(row[6]) + '"},'

    if conteudo != "":
        conteudo = conteudo[0:len(conteudo)-1]
        conteudo = "[" + conteudo + "]"

    comando = "sudo echo '" + conteudo + "' | sudo tee " + path_aux
    os.system(comando)

# Obtem beneficio pontual vigente
def get_beneficio_pontual_vigente():
    path_aux = path_atual + "/../../caixa-magica-operacao/beneficios_pontuais.json"

    now = datetime.utcnow()

    try:
        with open(path_aux) as json_data:
            aux = json.load(json_data)

            validoate = aux[0]['validoate']
           
            # Se o beneficio ainda esta valido, retornamos o mesmo
            if str(now) <= str(validoate):
                return aux[0]

        # Caso nao tenhamos beneficios validos, retornamos vazio
        # Neste cenario, catraca opera com valor padrao de tarifa (valor da propria linha)
        return []
    except Exception as e:
        return []

# Obtem beneficio do cliente, se tiver
def get_beneficio_cliente(contaId):
    conn1 = db.Conexao()
    
    sql = "select beneficioid from contas_controle_saldos where contaid = %s and beneficioid > 0"
    dados = (contaId,)
    result = conn1.consultarComBind(sql, dados)
    
    for row in result:
        sql = """select id, nome, coalesce(percentual,0), coalesce(valorfixo,0),
                    case when valorfixo > 0 then
                       false
                    else true
                    end por_percentual,
                    case when valorfixo > 0 then
                       true
                    else false
                    end por_valorfixo
	     from beneficios bp 
	     where bp.ativo =true 
  	       and (now() at time zone 'UTC') between bp.validode and bp.validoate
               and id = %s
             order by 1"""
        dados = (row[0], )
        result = conn1.consultarComBind(sql, dados)
        del conn1

        for row in result:
            return row
    del conn1
    return []

def get_preco_passagem_cliente(contaId):
    tarifa = get_preco_passagem()
    tarifa_cliente = tarifa
    tarifa_pontual = tarifa

    # Checamos se existe um beneficio pontual vigente.
    if tarifa > 0:
        try:
            beneficio = get_beneficio_pontual_vigente()

            # Se for beneficio pontual, usamos esse beneficio sem considerar outros beneficios
            if len(beneficio) > 0:
                # Se for um beneficio por percenual
                if beneficio['por_percentual'] == True:
                    if beneficio['percentual'] >= 100:
                        tarifa_pontual = 0
                    elif beneficio['percentual'] <= 0:
                        pass
                    else:
                        tarifa_pontual = tarifa * ((100 - beneficio['percentual']) / 100)
                # Se for por valor
                else:
                    if beneficio['valorfixo'] <= 0:
                        pass
                    elif beneficio['valorfixo'] >= tarifa:
                        tarifa_pontual = 0
                    else:
                        tarifa_pontual = tarifa - beneficio['valorfixo']
        except:
            pass

        # Checamos se existe um beneficio do cliente
        try:
            beneficio = get_beneficio_cliente(contaId)

            # Se for beneficio pontual, usamos esse beneficio sem considerar outros beneficios
            if len(beneficio) > 0:
                # Se for um beneficio por percenual
                if beneficio[4] == True:
                    if beneficio[2] >= 100:
                        tarifa_cliente = 0
                    elif beneficio[2] <= 0:
                        pass
                    else:
                        tarifa_cliente = tarifa * ((100 - beneficio[2]) / 100)
                # Se for por valor
                else:
                    if beneficio[3] <= 0:
                        pass
                    elif beneficio[3] >= tarifa:
                        tarifa_cliente = 0
                    else:
                        tarifa_cliente = tarifa - beneficio[3]
        except Exception as e:
            pass


    # S eo beneficio pontual for maior que o individual, retornamos o PONTUAL
    # Caso contrario, retornamos o INDIVIDUAL
    if tarifa_pontual > tarifa_cliente:
        return tarifa_cliente
    else:
        return tarifa_pontual

# Rotina que aplica o semaforo de leitura (seja QR, facial ou outros dispositivos)
def inicia_semaforo():
    comando = "sudo touch " + path_semaforo
    os.system(comando)

# Rotina que remove o semaforo de leitura
def remove_semaforo():
    comando = "sudo rm -f " + path_semaforo
    os.system(comando)

# Rotina que checa se o semaforo esta ativo
def semaforo_ativo():
    #return False
    if os.path.exists(path_semaforo):
        return True
    return False

# Checa se o arquivo de lock da catraca ja expirou 
def check_semaforo_expirado():
    global timeout_catraca

    while 1:
        try:
            mtime = os.path.getmtime(path_semaforo)
        except:
            mtime = -1

        if mtime > 0:
            try:
                now = datetime.timestamp(datetime.now())

                if now > (mtime + timeout_catraca + 1):
                    remove_semaforo()
            except:
                pass

def thread_check_semaforo_expirado():
    t1 = threading.Thread(target=check_semaforo_expirado)
    t1.start()


