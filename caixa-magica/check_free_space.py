import os
from time import sleep
import json
from tkinter import *
from tkinter import ttk
import tkinter as tk

import sys
import pathlib
path_atual = "/home/pi/caixa-magica"
sys.path.insert(1, path_atual)

sys.path.insert(1, path_atual + "/core/")
import funcoes_logs

local = 'check_free_space.py'

funcoes_logs.insere_log("Iniciando " + local, local)

def alerta_fail_disk_space():
    global root1
    root1 = Tk()
    style = ttk.Style(root1)
    root1.update()
    root1.deiconify()
    root1.configure(background="blue")
    root1.attributes("-fullscreen",True)
    verif = Label(root1, text="\n\n\n\nEspaço em disco\ninsuficiente.\n\n\n\nEncerrando aplicação.\n\n\n\nContate o admin.",fg="white", bg="blue", font=('Verdana',24,'bold'))
    verif.pack(side='top',fill=X)
    root1.after(15000,lambda:[root1.quit(), root1.destroy()])
    root1.mainloop()
    return

LIMITE_ESPACO_PCT = 97
ALERTA_LIMITE_ESPACO_PCT = 94
DISK_CHECK_SPACE = ""

while True:
    try:
        # Le arquivo de configuracao
        try:
            with open("/home/pi/caixa-magica-vars/config.json") as json_data:
                funcoes_logs.insere_log("Arquivo config.json aberto", local)
                config = json.load(json_data)
                LIMITE_ESPACO_PCT = int(config['limite_espaco_pct'])
                ALERTA_LIMITE_ESPACO_PCT = int(config['alerta_limite_espaco_pct'])
                DISK_CHECK_SPACE = config['disk_check_space']
        except Exception as e:
            funcoes_logs.insere_log("Erro ao abrir config.json: " + str(e), local)

        # obtem espaco em disco atual
        funcoes_logs.insere_log("Obtendo espaco em disco da maquina (via SO)", local)
        os.system("sudo rm -f /home/pi/caixa-magica/espaco_disco.txt")
        os.system("sudo touch /home/pi/caixa-magica/espaco_disco.txt")
        os.system("sudo df -H " + DISK_CHECK_SPACE + " | sudo tee -a /home/pi/caixa-magica/espaco_disco.txt > /dev/null")

        f = open("/home/pi/caixa-magica/espaco_disco.txt")
        aux = f.readline() 
        aux = f.readline()
        pos_pct = aux.find("%")

        # obtem o pct retornado pelo SO
        pct_usado = int(aux[(pos_pct-3): pos_pct])

        if pct_usado > LIMITE_ESPACO_PCT:
            print("Espaco excedido")

            funcoes_logs.insere_log("Percentual usado (" + str(pct_usado) + ") superior ao limite (" + str(LIMITE_ESPACO_PCT) + "). Reiniciando aplicacao", local)
            try:
                alerta_fail_disk_space()
            except Exception as e:
                pass
            sleep(5)
            os.system("sudo sh /home/pi/caixa-magica/start.sh")
    except Exception as e:
        funcoes_logs.insere_log("Erro: " + str(e), local)
    
    sleep(600)

