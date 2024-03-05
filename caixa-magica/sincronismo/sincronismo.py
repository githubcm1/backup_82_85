import sync
import time
import threading

import sys
import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"
sys.path.insert(1, path_atual + "/../core/")
import funcoes_logs

import db
import json
import os
import funcoes_serial


local = 'sincronismo.py'

funcoes_logs.insere_log("Iniciando " + local, local)

GLOBAL_DIAS_EXPURGO_JOURNAL = 7
GLOBAL_DIAS_EXPURGO_HIST_INTERNET = 1
GLOBAL_NOVA_TENTATIVA_EXPURGO_JOURNAL_MINUTOS = 3600
GLOBAL_NOVA_TENTATIVA_EXPURGO_HIST_INTERNET = 3600
GLOBAL_NOVA_TENTATIVA_RECEBER_CONTAS = 60
GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS = 60
GLOBAL_NOVA_TENTATIVA_DESBLOQUEAR_CONTAS = 60
GLOBAL_NOVA_TENTATIVA_ENVIO_COBRANCA = 30
GLOBAL_NOVA_TENTATIVA_RECEBER_OPERADORES = 120 
GLOBAL_NOVA_TENTATIVA_ABRE_OFFLINE = 60
GLOBAL_NOVA_TENTATIVA_FECHA_OFFLINE = 60
GLOBAL_NOVA_TENTATIVA_SINC_PRINCIPAL = 60
GLOBAL_NOVA_TENTATIVA_ATUALIZAR_SALDOS = 15

try:
    with open(path_atual+ '/../../caixa-magica-vars/config.json') as json_data:
        CONFIG = json.load(json_data)

        try:
            GLOBAL_NOVA_TENTATIVA_ATUALIZAR_SALDOS = config['nova_tentativa_atualizar_saldos']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_SINC_PRINCIPAL = CONFIG['nova_tentativa_sinc_principal']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_ABRE_OFFLINE = CONFIG['nova_tentativa_abre_offline']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_FECHA_OFFLINE = CONFIG['nova_tentativa_fecha_offline']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_RECEBER_OPERADORES = CONFIG['nova_tentativa_receber_operadores']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_ENVIO_COBRANCA = CONFIG['nova_tentativa_envio_cobranca']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_RECEBER_CONTAS = CONFIG['nova_tentativa_receber_contas']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_DESBLOQUEAR_CONTAS = CONFIG['nova_tentativa_desbloquear_contas']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS = CONFIG['nova_tentativa_atualizar_contas']
        except:
            pass

        try:
            GLOBAL_DIAS_EXPURGO_JOURNAL = CONFIG['dias_expurgo_journal']
        except:
            pass

        try:
            GLOBAL_DIAS_EXPURGO_HIST_INTERNET = CONFIG['dias_expurgo_hist_internet']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_EXPURGO_JOURNAL_MINUTOS = CONFIG['nova_tentativa_expurgo_journal_minutos']
        except:
            pass

        try:
            GLOBAL_NOVA_TENTATIVA_EXPURGO_HIST_INTERNET = CONFIG['nova_tentativa_expurgo_hist_internet']
        except:
            pass

except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir config.json", local)


# rotina que grava o ID da caixa magica na tabela de controle
def grava_db_serial():
    funcoes_logs.insere_log("Iniciando grava_db_serial()", local)
    cpuserial = funcoes_serial.getSerial()
    funcoes_logs.insere_log("Serial obtido: " + cpuserial, local)

    funcoes_logs.insere_log("Inserindo o serial na tabela caixa_magica", local)
    conn = db.Conexao()
    sql = "delete from caixa_magica"
    conn.manipular(sql)

    sql = "insert into caixa_magica (caixamagica_serial) values ('" + cpuserial + "')"
    conn.manipular(sql)
    funcoes_logs.insere_log("Serial inserido na tabela caixa_magica, id " + cpuserial, local)

def remover_facial():
    funcoes_logs.insere_log("Iniciando remover_facial", local)
    while True:
        try:
            funcoes_logs.insere_log("Chamando rotina remover_facial()", local)
            sync.remove_facial_fila()
            funcoes_logs.insere_log("Encerrando rotina remover_facial()", local)
        except Exception as e:
            funcoes_logs.insere_log("Erro no remover_facial(): " + str(e), local)

        time.sleep(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS)

def atualizar_facial():
    funcoes_logs.insere_log("Iniciando atualizar_facial", local)
    while True:
        print(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS)
        try:
            funcoes_logs.insere_log("Chamando rotina de atualizar faces", local)
            atualizar = sync.atualizar_facial_bulk()
        except Exception as e:
            print(str(e))
            funcoes_logs.insere_log("Erro no Sincronismo, na atualizacao de faces", local)
        funcoes_logs.insere_log("Aguardando " + str(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS), local)
        time.sleep(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS)

def threading_principal():
    funcoes_logs.insere_log("Iniciando threading_principal", local)
    while True:
        print(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS)
        #if 1==1:
        try:
            funcoes_logs.insere_log("Chamando rotina de atualizar contas", local)
            atualizar = sync.atualizar_contas_bulk()
        except Exception as e:
            funcoes_logs.insere_log("Erro no Sincronismo, na atualizacao de contas", local)
        funcoes_logs.insere_log("Aguardando " + str(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS), local)
        time.sleep(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_CONTAS)

def atualizar_saldos_fila():
    while True:
        try:
            funcoes_logs.insere_log("Chamando rotina de atualizar saldos", local)
            sync.atualizar_saldos_fila()
        except Exception as e:
            funcoes_logs.insere_log("Erro no sincronismo de saldos: " + str(e), local)
        time.sleep(GLOBAL_NOVA_TENTATIVA_ATUALIZAR_SALDOS)

def enviar_cobrancas():
    funcoes_logs.insere_log("Iniciando enviar_cobrancas", local)
    while True:
        try:
            funcoes_logs.insere_log("Chamando rotina para enviar_cobrancas", local)
            enviar = sync.enviar_cobrancas()
            if enviar == 2:
                funcoes_logs.insere_log("Todas as cobrancas foram enviadas - aguardando nova checagem", local)
            if enviar == 0:
                funcoes_logs.insere_log("Erro na conexao - esperando 15 segundos", local)
            time.sleep(GLOBAL_NOVA_TENTATIVA_ENVIO_COBRANCA)
        except Exception as e:
            print("Erro enviar_cobrancas(): " + str(e))
            funcoes_logs.insere_log("Erro no sincronismo, no envio de cobrancas. Esperando 30 segundos: " + str(e),local)
            time.sleep(GLOBAL_NOVA_TENTATIVA_ENVIO_COBRANCA)


def receber_operadores():
    funcoes_logs.insere_log("Iniciando receber_operadores", local)
    while True:
        try:
            funcoes_logs.insere_log("Chamando rotina receber_operadores", local)
            rec_operadores = sync.receber_operadores()
            if rec_operadores == 1:
                funcoes_logs.insere_log("Operadores recebido parcialmente", local)
            if rec_operadores == 2:
                funcoes_logs.insere_log("Recebido completamente", local)
           
            # Aguarda mais 1 minuto para sincronizacao da informacao
            time.sleep(GLOBAL_NOVA_TENTATIVA_RECEBER_OPERADORES)
        except Exception as e:
            funcoes_logs.insere_log("Erro no sincronismo, no envio para receber contas dos operadores. Esperando 30 segundos:" + str(e), local)
            time.sleep(GLOBAL_NOVA_TENTATIVA_RECEBER_OPERADORES) 

# Chama rotina de gravacao do serial
grava_db_serial()

a = threading.Thread(target=threading_principal)
b = threading.Thread(target=enviar_cobrancas)
c = threading.Thread(target=receber_operadores)
d = threading.Thread(target=atualizar_saldos_fila)
e = threading.Thread(target=atualizar_facial)
f = threading.Thread(target=remover_facial)

funcoes_logs.insere_log("Iniciando thread principal", local)
a.start()
funcoes_logs.insere_log("Iniciada thread principal", local)

funcoes_logs.insere_log("Iniciando envio de cobrancas", local)
b.start()
funcoes_logs.insere_log("Iniciado envio de cobrancas", local)

funcoes_logs.insere_log("Iniciando thread de receber operadores", local)
c.start()
funcoes_logs.insere_log("Iniciada thread de receber operadores", local)

funcoes_logs.insere_log("Iniciando thread de sincronismo de saldos", local)
d.start()
funcoes_logs.insere_log("Iniciada thread de sincronismo de saldos", local)

funcoes_logs.insere_log("Iniciando thread de sincronismo facial", local)
e.start()
funcoes_logs.insere_log("Iniciada thread de sincronismo facial", local)

funcoes_logs.insere_log("Iniciando thread de remover facial", local)
f.start()
funcoes_logs.insere_log("Iniciada thread de remover facial", local)

