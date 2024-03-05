import os
import sys
import time

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

sys.path.insert(1, path_atual + '/../sincronismo/')
import req as sincronismo
import json

from PIL import Image, ImageTk
import tkinter as tk
import threading
from itertools import count

sys.path.insert(2, path_atual +'/../tela/')
from AnimatedGIF import *
import funcoes_telas

sys.path.insert(3, path_atual + '/../core/')
import funcoes_logs
import funcoes_viagem
import funcoes_tela_corrente
import funcoes_qrcode
import funcoes_camera
import funcoes_nfc

local = 'inicializar_sistema.py'

funcoes_logs.insere_log("Iniciando " + local, local, 2)

def obtem_beneficios_pontuais():
    while 1:
        try:
            funcoes_viagem.gera_json_beneficios_pontuais()
        except:
            pass

        time.sleep(5)

def run_caixa_magica():
    funcoes_telas.inicia_tela_aguarde()

    os.system("sudo pkill -9 -f sincronismo")
    os.system("sudo pkill -9 -f telaPrincipal")
    funcoes_tela_corrente.registraTelaAtual("TELA_LOADING_VIAGEM")

    # gera o JSON com dados do motorista
    funcoes_viagem.forma_motorista_json()

    # gera JSON com os dados dos beneficios pontuais
    t = threading.Thread(target=obtem_beneficios_pontuais)
    t.start()

    funcoes_logs.insere_log("Iniciando telaPrincipal", local, 2)
    os.system("sudo taskset -c 0,1,2 python3 " + path_atual + "/../tela/telaPrincipal.py &")

    # Iniciando rotina de prova de vida
    funcoes_camera.status_inicial_prova_vida()
    liga_prova_vida = funcoes_camera.get_param_liga_prova_vida()

    if liga_prova_vida:
        funcoes_logs.insere_log("Iniciando check prova de vida", local, 2)
        os.system("sudo taskset -c 0,1 python3 " + path_atual + "/prova_vida.py &")
    
    # Inicializa Thread de leitura e captura informacoes do QRCode
    funcoes_qrcode.inicializa_coletor_qrcode()

    # Inicializa Thread que remove arquivo de semaforo, caso tenha ficado "preso"
    funcoes_viagem.thread_check_semaforo_expirado()

    funcoes_logs.insere_log("Iniciando sincronismo_inicia_jobs.py", local, 2)
    os.system("sudo taskset -c 1,2 python3 " + path_atual + "/../sincronismo/sincronismo_inicia_jobs.py &")

    # Inicia jog de coleta do NFC
    funcoes_nfc.inicializa_coletor_nfc()

run_caixa_magica()

funcoes_logs.insere_log("Finalizando " + local, local, 2)
