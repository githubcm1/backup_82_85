import os
import db
import time
import json
import requests

import rec_facial

import sys
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

import endpoints
import funcoes_logs
import funcoes_viagem
import funcoes_placa_serial
import funcoes_camera

def obtemPctRecFacial():
    valor = -1
    try:
        url = endpoints.urlbase + "Parametro?chave=PercentualMinimoSimilaridadeValidador"
        r = requests.get(url, timeout=10)
        if r.ok:
            json_aux = json.loads(r.text)
            valor = json_aux['valor']
            valor = (100 - float(valor)) / 100
    except Exception as e:
        valor = -1
    return valor

local = 'operacoes.py'

funcoes_logs.insere_log("Iniciando " + local, local, 2)

conn = db.Conexao()
counter = 0

GLOBAL_NUM_REGS_PROXIMIDADE_FACIAL = 5
GLOBAL_TIMEOUT_CATRACA = 20

CONFIG = None
with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
    CONFIG = json.load(json_data)

try:
    PATH_FILE_CHECK_CATRACA = CONFIG['path_file_check_catraca']
except:
    pass


try:
    GLOBAL_NUM_REGS_PROXIMIDADE_FACIAL = CONFIG['num_regs_proximidade_facial']
except:
    pass

try:
    GLOBAL_TIMEOUT_CATRACA = CONFIG['timeout_catraca']
except:
    pass

# Abrimos o arquivo de viagem, para saber qual é o id da viagem
GLOBAL_LINHA_ID = funcoes_viagem.get_linha_atual()

# forcamos o travamento da catraca
funcoes_placa_serial.trava_catraca()

max_rate_user = CONFIG['rec_facial']['max_rate_user']
min_rate_user = obtemPctRecFacial()

try:
    delay_catraca = CONFIG['delay_catraca']
except:
    delay_catraca = 0

if min_rate_user < 0:
    min_rate_user = CONFIG['rec_facial']['min_rate_user']

def remove_espera_catraca():
    #try:
    #    os.system("sudo rm -f " + PATH_FILE_CHECK_CATRACA)
    #except:
    #    pass

    # remove o semaforo
    funcoes_viagem.remove_semaforo()

def cria_espera_catraca():
    #try:
    #    os.system("sudo touch " + PATH_FILE_CHECK_CATRACA)
    #except:
    #    pass

    # Ativa o semaforo
    funcoes_viagem.inicia_semaforo()

def salvar_imagem(nome, conta, metricas):
    array_str = ",".join(map(str, metricas))
    dados=(str(nome), str(conta), array_str,)
    sql = "INSERT INTO facial(nome, conta, data) VALUES(%s, %s, cube(ARRAY[%s]));"
    conn.manipularComBind(sql,dados)
    funcoes_logs.insere_log("Matriz inserida para a conta " + str(conta), local, 2)

def liberar():
    funcoes_logs.insere_log("Entrando em liberar()", local, 2)
    
    funcoes_placa_serial.libera_catraca()

    Timeout = time.time() + GLOBAL_TIMEOUT_CATRACA
    funcoes_logs.insere_log("Iniciando contagem timeout da catraca (" + str(GLOBAL_TIMEOUT_CATRACA) + ") segundos", local, 2)
    
    cria_espera_catraca()
    
    # Fica no aguardo do giro da catraca, ou timeout
    while 1:
        try:
            if time.time() > Timeout:
                funcoes_logs.insere_log('Timeout de catraca', local, 2)
            
                # Envia o sinal para a catraca, para que seja novamente travada
                funcoes_placa_serial.trava_catraca()

                remove_espera_catraca()

                funcoes_camera.atualiza_status_prova_vida(False)

                return False
            else:
                # Checamos o retorno do botao de catraca
                valores = funcoes_placa_serial.obtem_variaveis_retorno()

                # Dando retorno da catraca, devemos retornar True para efetivacao da cobranca
                if valores['catraca'] == 1:
                    funcoes_placa_serial.trava_catraca()
                    remove_espera_catraca()

                    funcoes_camera.atualiza_status_prova_vida(False)
                    
                    # Aplica o delay de catraca, caso ele tenha sido configurado
                    print("Delay: " + str(delay_catraca))
                    if delay_catraca > 0:
                        print("Aplicando delay")
                        time.sleep(delay_catraca)

                    return True
        except Exception as e:
            pass

    # se chegou aqui, entao a catraca girou
    # Cobranca deve ser processada
    funcoes_placa_serial.trava_catraca()
    remove_espera_catraca()

    funcoes_camera.atualiza_status_prova_vida(False)

    return True

def get_user_linha(metricas):
    global GLOBAL_LINHA_ID
    tabela_consulta = 'facial_linha_' + str(GLOBAL_LINHA_ID)
    return get_user(metricas, tabela_consulta)

def get_user(metricas, tabela_consulta = 'facial'):

    array_str = ",".join(map(str, metricas))
    
    try:
        funcoes_logs.insere_log("Chamando get_user com a matriz " + str(array_str), local, 2)
        result = rec_facial.get_user( array_str )
        funcoes_logs.insere_log("Finalizando query reconhecimento facial", local, 2)
    except:
        funcoes_logs.insere_log("Erro ao consultar tabela " + tabela_consulta, local, 3)
        return ""

    cnt = 1
    r = result[0]
    return r

def get_rate(user):
    funcoes_logs.insere_log("Entrando em get_rate para user info " + str(user), local, 2)
    r = user
    r[2] = float(r[2])
    funcoes_logs.insere_log("User: " + str(r[2]), local, 2)

    if (r[2] <= min_rate_user):
        funcoes_logs.insere_log("Rate obtido 1 (" + str(r[2]) + " <= " + str(min_rate_user), local, 2)
        return 1
    elif (max_rate_user>=r[2]>min_rate_user):
        funcoes_logs.insere_log("Rate obtido 2 ( " + str(max_rate_user) + " >= " + str(min_rate_user), local, 2)
        return 2
    else:
        funcoes_logs.insere_log("rate obtido 3", local, 2)
        return 3

def get_cartao(id_cartao):
    funcoes_logs.insere_log("Entrando em get_cartao()", local,2)
    sql = "SELECT conta FROM cartao WHERE numero='{}'".format(id_cartao)
    result = conn.consultar(sql)
    if result:
        for r in result:
            return r[0]
    return False

