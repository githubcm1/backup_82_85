import requests
import os
import json
import datetime
import time

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo/"
sys.path.insert(1, path_atual + "/../pd/")

import codecs
import serial
from subprocess import PIPE, run

sys.path.insert(2, path_atual + "/../core/")
import funcoes_logs
import funcoes_viagem
import funcoes_serial
import funcoes_geo
import endpoints

local = 'syncGPS.py'

funcoes_logs.insere_log("Iniciando " + local, local)

BASEURL = endpoints.urlbase

funcoes_logs.insere_log("Abrindo instalacao.json", local)
try:
    with open(path_atual + '/../../caixa-magica-operacao/instalacao.json') as i:
        inst = json.load(i)
        codigo_acesso = inst['acesso']
        veiculo_id = inst['veiculo']
        veiculo_numero = inst['numeroVeiculo']
        operadora_id = inst['operadora']
        funcoes_logs.insere_log("Codigo acesso da Caixa Magica: " + codigo_acesso, local)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir o arquivo 'instalacao.json': " + str(e), local)

# Abrindo json de configuracao
funcoes_logs.insere_log("Abrindo config.json", local)
try:
    with open(path_atual +'/../../caixa-magica-vars/config_versao_cm.json') as json_data_config:
        configVersao = json.load(json_data_config)
        VERSAOCM = configVersao['versaoCM']
        USOGPSELSYS = configVersao['usoGPSElsys']
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir o arquivo 'config_versao_cm.json': " + str(e), local)

try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data_config2:
        aux = json.load(json_data_config2)
        habilita_geoloc_google_maps = aux['habilita_geoloc_google_maps']
except:
    habilita_geoloc_google_maps = False


url = BASEURL + "Geolocalizacao"

# Obtemos serial da caixa magica
caixa_magica_id = funcoes_serial.getSerial()

class GpsRead():
    port = ''
    def __init__(self, port='/dev/ttyS0'):
        self.port = port

    def get_gps(self):
        funcoes_logs.insere_log("Obtendo info do GPS interno via porta " + str(self.port), local)
        with serial.Serial(self.port, 9600) as ser:
            r = ser.read(256)
            ser.close()
            return r
        return False

def get_localization():
    funcoes_logs.insere_log("Entrando em get_localization() para info do GPS", local)
    
    # se estamos na versao da caixa magica 1
    if USOGPSELSYS == "N":
        funcoes_logs.insere_log("Pegando info do GPS local", local)
        try:
            gps = GpsRead()
            r = gps.get_gps()
            s = codecs.encode(r, 'hex').decode('utf-8')
            q = codecs.decode(s, "hex").decode('utf-8')

            if (q.find("RMC") != -1):
                start = q.find("RMC")
                stringG = q[start: start+60]
                final = stringG.find("W")
                localizacao = '$GP' + q[start: start + final + 1]

                funcoes_logs.insere_log("Localizacao obtida: " + str(localizacao), local)
                return localizacao
        except Exception as e:
            funcoes_logs.insere_log("Erro ao pegar geolocalizacao via Raspberry:" + str(e), local)
            return 'error'
        
    # Se for versao 2
    else:
        funcoes_logs.insere_log("Pegando info do GPS Elsys", local)
        try:
            comando = "curl -X POST http://192.168.10.254/boafrm/formGetGps -d undefined= --http0.9"
            funcoes_logs.insere_log("Rodando comando GPS: " + comando, local)
            result = run(comando, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
            data = result.stdout
            long_lat = json.loads(data)
            localization = long_lat['Longitude'] + ', ' + long_lat['Latitude']
            funcoes_logs.insere_log("Localizacao: " + str(localization), local)
            return localization

        # Se deu erro ao obter info do modem, pegamos direto do Google Maps
        except Exception as e:
            funcoes_logs.insere_log("Erro ao pegar geolocalização do Elsys: " + str(e), local)
            return get_localization_google()

# Pegamos a geoloc do GOOGLE MAPS
def get_localization_google():
    if habilita_geoloc_google_maps == False:
        funcoes_logs.insere_log("Geolocalizacao do Google Maps desabilita em config.json")
        return ""

    try:
        funcoes_logs.insere_log("Obtendo geolocalizacao do Google Maps", local)
        comando = 'curl https://www.google.com.br/maps/'
        result = run(comando, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        data = result.stdout
        pos = data.find("APP_INITIALIZATION_STATE")
        data = data[pos:len(data)]

        # Localizamos a primeira virgula, que eh aonde ocorre o inicio da geoloc
        pos = data.find(",")
        data = data[pos+1:len(data)]

        pos = data.find("]")
        data = data[0:pos].strip()

        # Agora que temos a geoloc, invertemos pra chegarmos em latitude + longitude
        pos = data.find(",")
        campo1 = data[0:pos]
        campo2 = data[pos+1:len(data)]
        retorno = campo2 + ", " + campo1
    except:
        funcoes_logs.insere_log("Erro ao obter geolocalizacao do Google Maps: " + str(e), local)
        retorno = ""
    return retorno

def enviar_localizacao():
    global url


    TIMEOUT_REQUESTS = 15

    funcoes_logs.insere_log("Entrando em enviar_localizacao()", local)

    # Pegamos o ID da viagem atual
    id_viagem_cm = funcoes_viagem.get_viagem_atual()

    # Se existe uma viagem aberta
    if id_viagem_cm != None:
        viagemAberta = True
    else:
        viagemAberta = False

    # Busca demais detalhes da viagem aberta
    linhaId = ""
    linhaNome = ""
    linhaCodigo = ""
    sentido_atual = ""

    if viagemAberta:
        arrDetalhes = funcoes_viagem.get_linha_detalhes_viagem_aberta()
        linhaId = arrDetalhes[0]
        linhaNome = arrDetalhes[1]
        linhaCodigo = arrDetalhes[2]
        
        # Obtemos o sentido da viagem atual
        sentido_atual = funcoes_viagem.get_sentido_atual()

        if sentido_atual == "VOLTA":
            sentido_atual = 2
        else:
            sentido_atual = 1

    while True:
            funcoes_logs.insere_log("refazendo arquivo geolocalizacao.json", local)

            now = datetime.datetime.now().isoformat()
            prossegue_envio = False
            localization = funcoes_geo.get_latitude_longitude_icr()
            if localization != "":
                prossegue_envio = True

            # reseta arquivo de geolocalizacao, para garantir que esteja sempre atualizado com o conteudo a seguir
            os.system("echo '{\"geolocalizacao\": \"\"}' > /home/pi/caixa-magica-operacao/geolocalizacao.json")

            # se chegou aqui, devemos enviar dados da geolocalizacao
            if prossegue_envio:
                conteudo_json = {"geolocalizacao": localization}
                
                # Gravamos a geolocalizacao no arquivo interno
                with open(path_atual+"/../../caixa-magica-operacao/geolocalizacao.json", "w+") as geolocalizacao_json:
                    geolocalizacao_json.write(json.dumps(conteudo_json))
                    funcoes_logs.insere_log('Geolocalização enviada com sucesso para backend', local)
                
                funcoes_logs.insere_log("Chamando url " + url, local)
                h = {
                        "CodigoAcesso": codigo_acesso,
                        "content-type": "application/json"
                    }
                viagemAberta="true"
                payload = {
                        "geolocalizacao": localization,
                        "linhaId": linhaId,
                        "veiculoId": veiculo_id,
                        "caixaMagicaId": caixa_magica_id,
                        "operadoraId": operadora_id,
                        "linhaNome": linhaNome,
                        "linhaCodigo": linhaCodigo,
                        "viagemAberta": viagemAberta,
                        "sentidoViagem": sentido_atual,
                        "veiculoNumero": veiculo_numero
                          }
                funcoes_logs.insere_log("Parametros header: " + str(h), local)
                funcoes_logs.insere_log("Parametros: " + str(payload), local)
                r = requests.post(url, data=json.dumps(payload), headers=h, timeout=TIMEOUT_REQUESTS)
                funcoes_logs.insere_log("retorno URL: " + url + ": " + str(r), local)

                if not r.ok:
                    funcoes_logs.insere_log("Erro no request put de localização: " +str(r), local)
                    return 2
                else:
                    return 1
            else:
                return 2
