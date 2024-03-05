import re
import os
import json
import threading
import subprocess
import multiprocessing

from time import sleep
from datetime import datetime
from funcoes_qrcode import checaTokenQrCode, desmembraQrCodeVars, check_qrcode_utilizado, cadastra_conta_qrcode
from funcoes_nfc_pn7150 import PN7150

ARQUIVO_SAIDA = '/home/pi/caixa-magica-operacao/saida_nfc.txt'
ARQUIVO_SAIDA_TAIL = '/home/pi/caixa-magica-operacao/saida_nfc_tail.txt'
ARQUIVO_SAIDA_JSON = '/home/pi/caixa-magica-operacao/nfc.json'
PATH_NFC_READER = '/home/pi/caixa-magica/nfc/'
ARQUIVO_HEALTHCHECK_NFC = '/home/pi/caixa-magica-operacao/lsusb_nfc.txt'

global VALOR_CONTEUDO_NFC
VALOR_CONTEUDO_NFC = ""

global LAST_MTIME_ARQUIVO_SAIDA
LAST_MTIME_ARQUIVO_SAIDA = -1

# Rotina de supressao de caracteres indevidos, possivelmente emitidos pela placa controladora serial
def remove_carac_indev(conteudo):
    return re.sub('(CA[0-9]{4}EZ)+','',conteudo)


# Rotina que cria a conta da pessoa, caso ela nao exista
def cadastra_conta_nfc(conta_id, nome_conta, saldo_conta):
    cadastra_conta_qrcode(conta_id, nome_conta, saldo_conta)

# Rotina que interpreta a validade do NFC
# A priori, a logica usada passa a ser identica a do QR CODE
def checaTokenNFC(nfc_string, num_seconds_expire):
    return checaTokenQrCode(nfc_string, num_seconds_expire)

# Rotina que interpreta o desmembramento do conteudo NFC
def desmembraNFCVars(nfc_string):
    return desmembraQrCodeVars(nfc_string)

# Rotina que checa se o NFC ja foi utilizado
def check_nfc_utilizado(nfc_string):
    return check_qrcode_utilizado(nfc_string)

def get_local_json():
    return ARQUIVO_SAIDA_JSON

def valor_nfc_json():
    # Abre o arquivo
    try:
        with open(ARQUIVO_SAIDA_JSON) as json_data:
            json_qrcode = json.load(json_data)
        return json_qrcode["nfc"]
    except:
        return ""


def reset_json():
    try:
        with open(ARQUIVO_SAIDA_JSON,"w") as f:
            f.write('{"nfc":""}')
        f.close()
    except Exception as e:
        pass

def grava_json(conteudo):
    try:
        with open(ARQUIVO_SAIDA_JSON,"w") as f:
            f.write('{"nfc":"'+str(conteudo.strip())+'"}')
        f.close()

        #shutdown_nfc()
    except Exception as e:
        pass


def remove_saida():
    try:
        os.system("sudo rm -f " + ARQUIVO_SAIDA_TAIL)
        os.system("sudo rm -f " + ARQUIVO_SAIDA)
        os.system("sudo touch " + ARQUIVO_SAIDA)
    except:
        pass

def shutdown_nfc():
    print("Parando NFC")
    os.system("sudo pkill -9 -f nfcCaixaMagica")

def healthcheck():
    try:
        process = subprocess.run(["lsusb"], capture_output=True)
        stdout_as_str = process.stdout.decode("utf-8")

        if "NXP Semiconductors" in stdout_as_str:
            return True
            
    except Exception as e:
        pass

    return False

# Identifica se o leitor NFC esta ativo
def old_healthcheck():
    arrReservados = ["NfcService Init Failed"]

    limite = 5
    tentativas = 0

    while tentativas < limite:
        try:
            tail_arquivo_saida()
            with open(ARQUIVO_SAIDA_TAIL) as f:
                conteudo = str(f.readlines()).strip()

                conteudo = remove_carac_indev(conteudo)
                conteudo = conteudo[len(conteudo)-50:len(conteudo)]

                for reservado in arrReservados:
                    if reservado in conteudo:
                        reset_json()
                        return False

                tentativas = tentativas + 1
                sleep(0.3)
        except Exception as e:
            reset_json()
            return False

    return True

# Identifica finalizador no arquivo
def finalizador():
    arrReservados = ["... press enter to quit ...","Waiting for a Tag/Device...", "NfcService Init Failed"]

    try:
        tail_arquivo_saida()
        with open(ARQUIVO_SAIDA_TAIL) as f:
            conteudo = str(f.readlines()).strip()

            if len(conteudo) < 50:
                return True

            conteudo = remove_carac_indev(conteudo)
            conteudo = conteudo[len(conteudo)-150:len(conteudo)]

            for reservado in arrReservados:
                if reservado in conteudo:
                    return True

            #print("Finalizador False")
            return False
    except Exception as e:
        return False

# Copia o conteudo do arquivo de saida, ultimas linhas
def tail_arquivo_saida():
    try:
        comando = "sudo tail -30 " + ARQUIVO_SAIDA + " | sudo tee " + ARQUIVO_SAIDA_TAIL
        os.system(comando)
    except:
        pass

# Rotina que efetua a leitura do retorno NFC atraves da saida NXP PN 7150
def coleta_pn7150():
    pn7150 = PN7150()
    pn7150.when_tag_read = lambda text: [grava_json(text)]
    pn7150.start_reading()
    pn7150.stop_reading()

# Funcao que inicializa o leitor NFC via C (Linux) e ainda coleta as saidas
def inicializa_coletor_nfc():
    os.system("sudo pkill -9 -f nfcCaixaMagica")
    os.system("sudo pkill -9 -f nfcDemoApp")
    sleep(1)
    while 1:
        t1 = multiprocessing.Process(target=coleta_pn7150)
        t1.start()
        t1.join(60)
            
        t1.terminate()
        os.system("sudo pkill -9 -f nfcCaixaMagica")
        os.system("sudo pkill -9 -f nfcDemoApp")
        sleep(1)

#inicializa_coletor_nfc()

