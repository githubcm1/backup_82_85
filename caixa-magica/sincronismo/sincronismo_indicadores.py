import os
import json
import sys
import time
import threading

sys.path.insert(1, '/home/pi/caixa-magica/core')
import funcoes_serial
import funcoes_geo_hist
import db
import endpoints
import funcoes_qrcode
import funcoes_camera
import funcoes_elastic

try:
    conn = db.Conexao()
except:
    pass

# Define o path dos arquivos
path_arquivos = "/home/pi/caixa-magica-indicadores/"

os.system("sudo mkdir -p " + path_arquivos)

TAXA_ATUALIZACAO = 60
TAXA_ATUALIZACAO_DB = 90

# Funcao que gera o arquivo de saida
def geraSaida(nome, conteudo):
    try:
        conteudo = str(conteudo)
        with open(path_arquivos + "/" + nome, "w") as fil:
            fil.write(conteudo.strip())
    except Exception as e:
        pass

# Rotina usada para pegar eventuais onibus com movimento sem viagem aberta
def getVeiculoMovimentoSemViagem():
    while True:
        try:
            ret = funcoes_geo_hist.pega_mov_viagem_fechada()
            conteudo = ret[0]
        except Exception as e:
            conteudo = False

        geraSaida("mov_viagem_fechada.txt", conteudo)
        time.sleep(10)

# Pega o conteudo do token de atualizacao (para controle do time de infra)
def getToken():
    pathtoken = '/home/pi/caixa-magica-updates/token_update.json'

    while True:
        try:
            with open(pathtoken) as jsondata:
                aux = json.load(jsondata)
                conteudo = aux['token']
        except:
            conteudo = ""
            pass
        geraSaida("token_update.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que define o status da viagem
def getStatusViagem():
    while True:
        conteudo = ""
        try:
            if os.path.exists("/home/pi/caixa-magica-operacao/aberto.txt"):
                conteudo = "ABERTA"
            else:
                conteudo = "FECHADA"
        except Exception as e:
            pass

        geraSaida("statusviagem.txt", conteudo) 
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que define o numero de serie do dispositivo
def getSerial():
    while True:
        conteudo = ""
        try:
            conteudo = funcoes_serial.getSerial()

            if conteudo != "":
                geraSaida("serial.txt", conteudo)
        except:
            pass
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que busca a geolocalizacao
def geoloc():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/geolocalizacao.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = aux['geolocalizacao']
        except:
            conteudo = ""
            pass
        geraSaida("geolocalizacao.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que busca o numero do Onibus
def getNumeroOnibus():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/instalacao.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = aux['numeroVeiculo']
        except:
            conteudo = ""
        
        geraSaida("onibus.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que busca o numero do Onibus
def getOperadora():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/instalacao.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = aux['operadora']
        except:
            conteudo = ""

        geraSaida("operadora.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que busca o id da instalacao do onibus
def getIdInstalacaoOnibus():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/instalacao.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = aux['veiculo']
        except:
            conteudo = ""

        geraSaida("numeroinstalacao.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

def getMotorista():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/motorista.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = str(aux['id_web']) + "-" + aux['nome']
        except:
            conteudo = ""

        geraSaida("motorista.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

def getQRMotorista():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/motorista.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = str(aux['id_qrcode'])
        except:
            conteudo = ""

        geraSaida("qrmotorista.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

def getLinhaAtual():
    while True:
        conteudo = ""
        try:
            sql = """select l.codigopublico
                     from viagem v,
	                  linhas l 
                     where v.viagem_atual=true
                       and v.linha_id = l.id"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass

        geraSaida("linhaatual.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega quantidade de operadores
def getQtdeOperadores():
    while True:
        conteudo = ""
        try:
            sql = """select count(*) from operadores"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass

        geraSaida("qtdeoperadores.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega quantidade de contas
def getQtdeContas():
    while True:
        conteudo = ""
        try:
            sql = """select count(*) from contas"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass

        geraSaida("qtdecontas.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega quantidade de linhas
def getQtdeLinhas():
    while True:
        conteudo = ""
        try:
            sql = """select count(*) from linhas"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass

        geraSaida("qtdelinhas.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega quantidade de faces
def getQtdeFaces():
    while True:
        conteudo = 0
        try:
            ret = funcoes_elastic.lista_indices_faciais()
            conteudo = 0
            for row in ret:
                conteudo = conteudo + int(row[1])
        except:
            pass
        
        geraSaida("qtdefaces.txt", str(conteudo))
        time.sleep(TAXA_ATUALIZACAO_DB)

#Pega qtde viagem sem abertua
def getQtdeViagensPendAbertura():
    while True:
        conteudo = ""
        try:
            sql = """select count(*) from viagem where dateviagemabertabackend is null"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass
        geraSaida("qtdeviagenspendabertura.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

#Pega qtde viagem sem abertua
def getTarifaLinhaAtual():
    while True:
        conteudo = ""
        try:
            sql = """select l.valor_tarifa
                     from viagem v,
	                  linhas l 
                     where v.viagem_atual=true
                       and v.linha_id = l.id"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass
        geraSaida("tarifalinhaatual.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

#Pega qtde viagem sem abertua
def getCobrancasPendentes():
    while True:
        conteudo = ""
        try:
            sql = """select count(*) from cobrancas where enviada=false"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass
        geraSaida("cobrancaspend.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

#Pega qtde viagens abertas sem encerramento
def getQtdeViagensPendEncerramento():
    while True:
        conteudo = ""
        try:
            sql = "select count(*) from viagem v where v.encerramento_id is not null and v.dateviagemencerradabackend is null"
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass
        geraSaida("qtdeviagenspendencerramento.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega tamanho do diretorio de Logs
def getLogSize():
    saidaaux = path_arquivos + "/aux_logsize.txt"
    while True:
        try:
            comando = "sudo du -hs /home/pi/caixa-magica-logs/ | sudo tee " + saidaaux
            os.system(comando)

            with open(saidaaux) as fil:
                conteudo = fil.readline()
                fil.close()

                pos = conteudo.find("/")
                conteudo = conteudo[0:pos]
                conteudo = conteudo.replace("M", "")
                print(conteudo)
        except:
            conteudo = ""

        geraSaida("logsize.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Pega tamanho do diretorio de imagens
def getImgSize():
    saidaaux = path_arquivos + "/aux_imgsize.txt"
    while True:
        try:
            comando = "sudo du -hs /home/pi/caixa-magica-img/ | sudo tee " + saidaaux
            os.system(comando)

            with open(saidaaux) as fil:
                conteudo = fil.readline()
                fil.close()

                pos = conteudo.find("/")
                conteudo = conteudo[0:pos]
                conteudo = conteudo.replace("M","")
        except:
            conteudo = ""

        geraSaida("imgsize.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

#Pega SE O bd responde
def getBDAtivo():
    while True:
        conteudo = "OFF"
        try:
            sql = """select 1"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = "ON"
        except:
            pass
        geraSaida("bdativo.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega tamanho atual do BD
def getBDSize():
    while True:
        conteudo = ""
        try:
            sql = """select pg_size_pretty(sum(db_size)) tam
                     from
                    (
	                select t1.datname AS db_name,  
	                        (pg_database_size(t1.datname)) as db_size
	                from pg_database t1
	                order by pg_database_size(t1.datname) desc
                    ) x"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
                conteudo = conteudo.replace("MB", "").strip()
        except:
            pass

        geraSaida("bdsize.txt", conteudo)
        time.sleep(600)

# Pega info da ultima atualizacao de operadores
def getLastUpdateOperadores():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/sincronismo_operadores.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = str(aux['lastUpdateTime'])
        except:
            conteudo = ""

        geraSaida("lastsyncoperadores.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Pega info da ultima atualizacao de operadores
def getLastUpdateContas():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/sincronismo.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = str(aux['lastSyncAtualizacao'])
        except:
            conteudo = ""

        geraSaida("lastsynccontas.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

def getLastUpdateFacial():
    while True:
        try:
            with open("/home/pi/caixa-magica-operacao/sincronismo_facial.json") as jsondata:
                aux = json.load(jsondata)
                conteudo = str(aux['lastUpdateTime'])
        except:
            conteudo = ""

        geraSaida("lastsyncfacial.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Pega ultima atualizacao de linhas
def getLastUpdateLinhas():
    while True:
        conteudo = ""
        try:
            sql = """select max(greatest(dateupdate,dateinsert)) from linhas"""
            result = conn.consultar(sql)

            for row in result:
                conteudo = row[0]
        except:
            pass
        geraSaida("lastsynclinhas.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega ultima situacao de km rodada no dia
def getKmTotalDia():
    sql = """select round(sum(total_km),2) total
           from estatistica_total_km 
           where dat = (now() at time zone 'utc')::date"""
    
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass
        geraSaida("totalkmdia.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega o total de Kms percorridos no dia com a viagem fechada
def getKmTotalFechadaDia():
    sql = """select round(sum(total_km),2)
             from estatistica_total_status_viagem_km 
             where dat = (now() at time zone 'utc')::date
               and status_viagem='FECHADA'"""

    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass
        geraSaida("totalkmdiafechada.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega o total de Kms percorridos no dia com a viagem aberta
def getKmTotalAbertaDia():
    sql = """select round(sum(total_km),2)
             from estatistica_total_status_viagem_km 
             where dat = (now() at time zone 'utc')::date
               and status_viagem='ABERTA'"""

    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass
        geraSaida("totalkmdiaaberta.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega o total de Kms percorridos desde o encerramento da ultima viagem
def getKmTotalFechadaDesdeUltimaViagem():
    sql = """select round(sum(distancia_last_id_km),2)
    	     from historico_geoloc g 
	     where g.id >= (select max(id) from historico_geoloc where viagemid <> '')"""

    while True:
        conteudo =""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass
        geraSaida("totalkmdesdeultimaviagem.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

def getKmTotalViagemAtual():
    sql = """select coalesce(round(sum(distancia_last_id_km),2),0)
             from historico_geoloc g 
             where g.viagemid = (select v.id_viagem_cm from viagem v where v.viagem_atual =true)"""

    while True:
        conteudo =""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass
        geraSaida("totalkmviagematual.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega o total de horas em que a viagem esta aberta
def getHorasViagemAberta():
    sql = """select /*round(extract( epoch from (x.atual - x.abertura))/60/60) diff_minutos*/
		    floor((extract(epoch from x.atual) - extract(epoch from x.abertura))/3600) diff_horas
from
(
	select v.dateinsert abertura, now() at time zone 'utc' atual
	from viagem v where v.viagem_atual =true
) x"""
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass

        if conteudo == "":
            conteudo = 0
        geraSaida("horasviagemaberta.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega q quantidade de passagens pelo botao DINHEIRO no dia
def getTotalDinheiroDia():
    sql = """select count(*) 
from cobrancas c
where c.datahora::date >= ((now() at time zone 'utc')::date)
  and c.tipopagamento ='8'"""
    
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass

        if conteudo == "":
            conteudo = 0
        geraSaida("totalpassagensdiadinheiro.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega q quantidade de passagens pelo botao gratuidade no dia
def getTotalGratuidadeDia():
    sql = """select count(*) 
from cobrancas c
where c.datahora::date >= ((now() at time zone 'utc')::date)
  and c.tipopagamento ='5'"""
    
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass

        if conteudo == "":
            conteudo = 0
        geraSaida("totalpassagensdiagratuidade.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega q quantidade de passagens de FACE no dia
def getTotalFaceDia():
    sql = """select count(*) 
from cobrancas c
where c.datahora::date >= ((now() at time zone 'utc')::date)
  and c.tipopagamento ='2' and c.tipoidentificacao='3'"""
    
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass

        if conteudo == "":
            conteudo = 0
        geraSaida("totalpassagensdiaface.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)

# Pega q quantidade de passagens de FACE no dia
def getTotalQRDia():
    sql = """select count(*) 
from cobrancas c
where c.datahora::date >= ((now() at time zone 'utc')::date)
  and c.tipopagamento ='2' and c.tipoidentificacao='4'"""
    
    while True:
        conteudo = ""
        try:
            result = conn.consultar(sql)

            for row in result:
                conteudo = str(row[0])
        except:
            pass

        if conteudo == "":
            conteudo = 0
        geraSaida("totalpassagensdiaqr.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO_DB)


# Identifica qual ambiente o validador esta usando
def getEnv():
    while True:
        try:
            conteudo = endpoints.getEnv()
        except:
            conteudo = ""
        geraSaida("ambiente.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Pega se a versao é Pyconcrete ou Python
def getVersaoEncriptada():
    while True:
        try:
            if os.path.exists('/home/pi/caixa-magica/start.pye'):
                conteudo = 'ENCRIPTADA'
            else:
                conteudo = 'PYTHON'
        except:
            conteudo = ''
        geraSaida("tipoversao.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Identifica em qual tela o sistema esta
def getTelaCorrente():
    comando = "sudo cp -f /home/pi/caixa-magica-operacao/telaatual.txt /home/pi/caixa-magica-indicadores/telaatual.txt"
    while True:
        try:
            os.system(comando)
        except:
            pass

        time.sleep(1)

# identifica  o retorno do GPS do modem
def getRetornoGPS():
    comando = "sudo curl -X POST http://192.168.10.254/boafrm/formGetGps -d undefined= | sudo tee /home/pi/caixa-magica-indicadores/retorno_gps_elsys.txt"

    while True:
        try:
            os.system(comando)
        except:
            conteudo = ""
        time.sleep(TAXA_ATUALIZACAO)

# Identifica o status da leitora do QR Code
def getStatusQR():
    while True:
        try:
            status = funcoes_qrcode.retorna_status_qrcode()
        except:
            status=""
        geraSaida("statusleitoraqrcode.txt", status)
        time.sleep(TAXA_ATUALIZACAO)

# Identifica o status da camera
def getStatusCamera():
    while True:
        try:
            status = funcoes_camera.get_status_camera()
        except Exception as e:
            status=""
            print(str(e))
        geraSaida("statuscamera.txt", status)
        time.sleep(TAXA_ATUALIZACAO)

# Rotina que define o status do Elastic Search
def getElasticStatus():
    while True:
        conteudo = ""
        try:
            conteudo = funcoes_elastic.check_elastic_on()

            if conteudo != "":
                geraSaida("statuselasticativo.txt", str(conteudo))
        except:
            conteudo = "OFF"
            pass
        geraSaida("statuselasticativo.txt", conteudo)
        time.sleep(TAXA_ATUALIZACAO)

# Thread de temperatura
t1 = threading.Thread(target=getStatusCamera)
t2 = threading.Thread(target=getStatusViagem)
t3 = threading.Thread(target=getSerial)
t4 = threading.Thread(target=geoloc)
t5 = threading.Thread(target=getNumeroOnibus)
t6 = threading.Thread(target=getOperadora)
t7 = threading.Thread(target=getIdInstalacaoOnibus)
t8 = threading.Thread(target=getMotorista)
t9 = threading.Thread(target=getQRMotorista)
t10 = threading.Thread(target=getLinhaAtual)
t11 = threading.Thread(target=getQtdeOperadores)
t12 = threading.Thread(target=getQtdeContas)
t13 = threading.Thread(target=getQtdeLinhas)
t14 = threading.Thread(target=getQtdeFaces)
t15 = threading.Thread(target=getQtdeViagensPendAbertura)
t16 = threading.Thread(target=getTarifaLinhaAtual)
t17 = threading.Thread(target=getCobrancasPendentes)
t18 = threading.Thread(target=getQtdeViagensPendEncerramento)
t19 = threading.Thread(target=getLogSize)
t20 = threading.Thread(target=getImgSize)
t21 = threading.Thread(target=getBDAtivo)
t22 = threading.Thread(target=getBDSize)
t23 = threading.Thread(target=getLastUpdateOperadores)
t24 = threading.Thread(target=getLastUpdateContas)
t25 = threading.Thread(target=getLastUpdateFacial)
t26 = threading.Thread(target=getLastUpdateLinhas)
t27 = threading.Thread(target=getToken)
t28 = threading.Thread(target=getVeiculoMovimentoSemViagem)
t29 = threading.Thread(target=getKmTotalDia)
t30 = threading.Thread(target=getKmTotalFechadaDia)
t31 = threading.Thread(target=getKmTotalAbertaDia)
t32 = threading.Thread(target=getKmTotalFechadaDesdeUltimaViagem)
t33 = threading.Thread(target=getKmTotalViagemAtual)
t0 = threading.Thread(target=getTelaCorrente)
t34 = threading.Thread(target=getEnv)
t35 = threading.Thread(target=getVersaoEncriptada)
t36 = threading.Thread(target=getRetornoGPS)
t37 = threading.Thread(target=getHorasViagemAberta)
t38 = threading.Thread(target=getTotalDinheiroDia)
t39 = threading.Thread(target=getTotalGratuidadeDia)
t40 = threading.Thread(target=getTotalFaceDia)
t41 = threading.Thread(target=getTotalQRDia)
t42 = threading.Thread(target=getStatusQR)
t43 = threading.Thread(target=getElasticStatus)

t0.start()
t1.start()
time.sleep(1)
t2.start()
time.sleep(1)
t3.start()
time.sleep(1)
t4.start()
time.sleep(1)
t5.start()
time.sleep(1)
t6.start()
time.sleep(1)
t7.start()
time.sleep(1)
t8.start()
time.sleep(1)
t9.start()
time.sleep(1)
t10.start()
time.sleep(1)
t11.start()
time.sleep(1)
t12.start()
time.sleep(1)
t13.start()
time.sleep(1)
t14.start()
time.sleep(1)
t15.start()
time.sleep(1)
t16.start()
time.sleep(1)
t17.start()
time.sleep(1)
t18.start()
time.sleep(1)
t19.start()
time.sleep(1)
t20.start()
time.sleep(1)
t21.start()
time.sleep(1)
t22.start()
time.sleep(1)
t23.start()
time.sleep(1)
t24.start()
time.sleep(1)
t25.start()
time.sleep(1)
t26.start()
time.sleep(1)
t27.start()
time.sleep(1)
t28.start()
time.sleep(1)
t29.start()
time.sleep(1)
t30.start()
time.sleep(1)
t31.start()
time.sleep(1)
t32.start()
time.sleep(1)
t33.start()
time.sleep(1)
t34.start()
time.sleep(1)
t35.start()
time.sleep(1)
t36.start()
time.sleep(1)
t37.start()
time.sleep(1)
t38.start()
time.sleep(1)
t39.start()
time.sleep(1)
t40.start()
time.sleep(1)
t41.start()

t42.start()
t43.start()
