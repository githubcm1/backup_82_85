import os
from datetime import datetime
import time
import json

path_json_prova_vida = '/home/pi/caixa-magica-operacao/prova_vida.json'
path_json_lock_tela_viagem = '/home/pi/caixa-magica-operacao/lock_tela_viagem.json'
path_json_status_camera = '/home/pi/caixa-magica-operacao/status_camera.json'
path_json_status_cobranca = '/home/pi/caixa-magica-operacao/status_cobranca.json'

# Remove arquivo de status de vida
def remove_prova_vida():
    try:
        os.remove(path_json_prova_vida)
    except Exception as e:
        print("Erro remove: " + str(e))
        pass

# Pegamos o parametro de prova de vida expiracao
def get_param_expiracao_prova_vida():
    try:
        with open("/home/pi/caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            return aux["expiracao_prova_vida"]
    except:
        return 0

# Grava arquivo com status de processamento da cobranca
def grava_processamento_cobranca(status, faz_sleep = True):
    return
    if status == True:
        status = "true"
    else:
        # Indica que a cobranca foi finalizada. Porem, aguarda alguns segundos antes de mudar o status
        # Motivo: evitar delays com a camera, para que uma segunda cobranca nao seja feita indevidamente
        # Para a pessoa na catraca
        status = "false"

        if faz_sleep:
            time.sleep(0.1)

    string_file = '{"ativa": ' + str(status) + '}'

    with open(path_json_status_cobranca, "w") as f:
        f.write(string_file)

# Checamos o status atual da cobranca
def get_status_cobranca():
    try:
        with open(path_json_status_cobranca) as json_data:
            aux = json.load(json_data)
            return aux["ativa"]
    except Exception as e:
        return False

# Grava o arquivo de status atual da camera
def atualiza_status_camera(status):
    if status == True:
        status = "true"
    else:
        status = "false"

    string_file = '{"ativa": ' + str(status) + '}'

    with open(path_json_status_camera, "w") as f:
        f.write(string_file)

# Checamos o status atual da camera
def get_status_camera():
    try:
        with open(path_json_status_camera) as json_data:
            aux = json.load(json_data)
            return aux["ativa"]
    except Exception as e:
        return False

# Grava o status de lock da abertura da viagem
def atualiza_lock_tela_viagem(status):
    if status == True:
        status = "true"
    else:
        status = "false"

    string_file = '{"lock": ' + str(status) + '}'
    with open(path_json_lock_tela_viagem, "w") as f:
        f.write(string_file)

# Checamos se o parametro de prova de vida esta ligado
def get_param_lock_tela_viagem():
    try:
        with open(path_json_lock_tela_viagem) as json_data:
            aux = json.load(json_data)
            return aux["lock"]
    except Exception as e:
        return False

# Inicializa arquivo JSON com o conteudo do status de prova de vida
def status_inicial_prova_vida():
    atualiza_status_prova_vida(True)

# obtem ultimamodificao do arquivo de prova de vida
def ultima_atualizacao_prova_vida():
    try:
        ts = os.path.getmtime(path_json_prova_vida)
    except:
        ts = 0
    return ts

# Checa se prova de vida esta expirada
def check_expirada_prova_vida():
    ts_pv = ultima_atualizacao_prova_vida()
    ts_now = datetime.now().timestamp()

    if (ts_now - ts_pv) > get_param_expiracao_prova_vida():
        return True
    else:
        return False

# Grava o arquivo de mensagem alterando o conteudo do pacote a ser enviado
def atualiza_status_prova_vida(status):
    if status == True:
        status = "true"
    else:
        status = "false"

    string_file = '{"boolean_status_vida": ' + str(status) + '}'

    with open(path_json_prova_vida, "w") as f:
        f.write(string_file)

# Obtemos o valor do status de prova de vida
def obtem_status_prova_vida():
    status = False

    # Caso o parametro de prova de vida esteja desligado, entao sempre consideramos este valor como True
    if not get_param_liga_prova_vida():
        status = True
        return status

    try:
        with open(path_json_prova_vida) as json_data:
            aux = json.load(json_data)
            status = aux['boolean_status_vida']
    except Exception as e:
        status = False

    return status

# Checamos se o parametro de prova de vida esta ligado
def get_param_liga_prova_vida():
    try:
        with open("/home/pi/caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            return aux["liga_prova_vida"]
    except:
        return False

# Obtemos o timeout da camera (em segundos)
def get_param_timeout():
    try:
        with open("/home/pi/caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            return aux["timeout_streaming_camera"]
    except:
        return 30

# Mantem o timestamp de camera atualizado, de forma a controlar se o processo da mesma encontra-se em execucao
def atualiza_health_camera():
    return datetime.utcnow()

# Calcula a diferenca da ultima atualizacao da camera com o horario atual
def check_camera_timeout(ultimo_timestamp):
    try:
        atual = datetime.utcnow().timestamp()
        ultimo_timestamp = ultimo_timestamp.timestamp()
        timeout_segundos = get_param_timeout()

        diff = atual - ultimo_timestamp
        if diff > timeout_segundos:
            return True
        return False
    except:
        return False

def get_camera_testes():
    try:
        with open("/home/pi/caixa-magica-operacao/camera_testes.txt") as fil:
            path = fil.readline()
            path = path.strip()
            fil.close()
            return path
    except Exception as e:
        return ""

    return ""
