import time 
import json
import datetime
from datetime import timezone
from datetime import timedelta   

import sys
path_atual = "/home/pi/caixa-magica/core"

sys.path.insert(2, '/home/pi/caixa-magica/core/')
import funcoes_serial
import endpoints
import funcoes_tela_corrente
import funcoes_internet

import os

from tkinter import *
from tkinter import ttk
from threading import Thread
sys.path.insert(1, path_atual +'/../sincronismo/')
import req
import urllib.request as urllib2

from PIL import Image, ImageTk
import tkinter as tk
from itertools import count

sys.path.insert(2, path_atual +'/../')
from tela.AnimatedGIF import *

sys.path.insert(3, path_atual)
import funcoes_logs
import funcoes_viagem
import funcoes_qrcode

sys.path.insert(4, path_atual + "/../tela/")
import funcoes_telas

sys.path.insert(5, path_atual + "/../discord/")
import functions_discord

local = 'telaFechamento.py'
funcoes_logs.insere_log("Iniciando " + local, local, 2)

# registramos que estamos na tela de encerramento
funcoes_tela_corrente.registraTelaAtual("TELA_ENCERRAMENTO_VIAGEM")

os.system("sudo pkill -9 -f core.py")
funcoes_telas.inicia_tela_aguarde()
time.sleep(1)
os.system("sudo pkill -9 -f telaPrincipal.py")
os.system("sudo pkill -9 -f sincronismo_monitor_tela.py")

funcoes_telas.inicia_tela_aguarde()
time.sleep(1)

# Abre arquivo config.json para obter detalhes do tamanho da tela
try:
    with open(path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        aux = json.load(json_data)
        WIDTH_COL1 = aux['tela_fechamento_width_col1']
        WIDTH_COL2 = aux['tela_fechamento_width_col2']

        del aux
except Exception as e:
    WIDTH_COL1 = 242
    WIDTH_COL2 = 238

INIT = None
CONFIG = None
with open(path_atual +'/../../caixa-magica-vars/config_versao_cm.json') as json_data:
    CONFIG = json.load(json_data)

# Abrindo jsons

# motorista.json
try:
    funcoes_logs.insere_log("Obtendo nome do motorista", local, 2)
    with open(path_atual +'/../../caixa-magica-operacao/motorista.json') as json_data:
        motorista= json.load(json_data)
        motorista_nome = motorista['nome']
   
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir motorista.json: " + str(e), local, 3)
    motorista_nome = "NAO INFORMADO"

# Pegamos o status da internet no momento deste encerramento
status_internet = funcoes_internet.get_status_internet()

if status_internet != "ONLINE":
    try:
        with open(path_atual+'/../../caixa-magica-vars/config.json') as json_data:
            aux = json.load(json_data)
            frase_offline_encerramento = aux['frase_offline_encerramento']
            print("Obtive frase encerramento offline")
    except:
        frase_offline_encerramento = ""
        print("Nao obtive frase encerramento offline")
else:
    frase_offline_encerramento = ""

try:
    barcode_encerramento = sys.argv[1]
except:
    barcode_encerramento = 0

# Através do qrcode pegamos quem seria o operador
id_operador_encerramento = funcoes_qrcode.getIdOperadorQr(barcode_encerramento)

# Atraves da viagem atual, obtemos o nome da linha
nome_linha = funcoes_viagem.get_linha_nome()

# Obtemos os detalhes da viagem a partir do banco de dados
passagens_gratuidades = funcoes_viagem.getTotalGratuidade()

detalhes_viagem = funcoes_viagem.get_detalhes_fechamento_viagem()
responsavelId = detalhes_viagem[0]
preco_passagem = detalhes_viagem[1]
valor_passagem = float(detalhes_viagem[1])
valor_passagem_2 = '${:,.2f}'.format(valor_passagem)
id_registro_viagem =detalhes_viagem[2]
data_criacao = str(detalhes_viagem[3])
data_string = data_criacao[0:19]
datetime_object = datetime.datetime.strptime(data_string,"%Y-%m-%d %H:%M:%S")
datetime_object_brasilia = datetime_object - timedelta(hours = 3)
data_inicio= ("%02d/%02d/%s" %(datetime_object_brasilia.day,datetime_object_brasilia.month,datetime_object_brasilia.year))
hora_inicio=("%02d:%02d:%02d" %(datetime_object_brasilia.hour,datetime_object_brasilia.minute,datetime_object_brasilia.second))

url = endpoints.urlbase

# sincronismo.json
try:
    funcoes_logs.insere_log("Abrindo sincronismo.json para obter url base", local, 2)
    with open(path_atual + '/../../caixa-magica-operacao/sincronismo.json') as json_data:
        sincronismo = json.load(json_data)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir 'sincronismo.json' em 'telaFechamento.py': "+ str(e),local, 3)


# Pega o total de passagens em dinheiro
passagens_dinheiro = funcoes_viagem.getTotalDinheiro()

# Pega o tota de passagens eletronicas
passagens_eletronicas = funcoes_viagem.getTotalPassagensEletr()

total_dinheiro = funcoes_viagem.getSomaPassagens()
total_dinheiro_2= 'R${:,.2f}'.format(total_dinheiro)
valor_eletronico = valor_passagem * passagens_eletronicas
valor_eletronico_2 = 'R${:,.2f}'.format(valor_eletronico)

#total_passagens_turno = passagens_dinheiro + passagens_eletronicas + passagens_gratuidades
total_passagens_turno = funcoes_viagem.getTotalPassagens()

#total_recebido= valor_eletronico + total_dinheiro
total_recebido = funcoes_viagem.getSomaPassagens()

total_recebido_2 = 'R${:,.2f}'.format(total_recebido)

# Forca a geracao da chave de encerramento neste trecho
# Informamos o id do operador para encerramento
r = req.get_idFechamentoViagem(id_operador_encerramento)

# idFechamentoViagem.json
idFechamentoViagem = ''
try:
    with open('/home/pi/caixa-magica-operacao/idFechamentoViagem.json', 'r') as json_data:
        FechamentoViagem = json.load(json_data)
        idFechamentoViagem = FechamentoViagem['idFechamentoViagem']
except Exception as e:
    print('Erro ao abrir idFechamentoViagem.json em req.py', e)

# Inserimos aqui a notificacao de que a viagem foi encerrada
mensagem_discord = "Viagem encerrada na linha " + str(nome_linha) + ", motorista " + motorista_nome + " (id Encerramento: " + idFechamentoViagem + ")"
functions_discord.insere_notificacao_fila(mensagem_discord, 'eventos')

def restart():
    funcoes_viagem.set_desmarca_viagem_ativa()
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/camera_testes.txt")
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/aberto.txt")
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/inicializacao.json")
    os.system("sudo rm -f  "+ path_atual + "/../../caixa-magica-operacao/passagens_viagem.json")
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/viagem.json")
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/motorista.json")
    os.system("sudo rm -f " + path_atual + "/../../caixa-magica-operacao/idFechamentoViagem.json")
    os.system("sudo sh " + path_atual + "/../start.sh")

def tela_fechamento():
   root = Tk()

   subject="ENCERRAMENTO VIAGEM"

   style = ttk.Style(root)
   style.configure("Treeview", rowheight=33)
   style.configure("Treeview", highlightthickness=0, bd=0, font=('Calibri', 15)) # Modify the font of the body
   style.configure("Treeview.Heading", font=('Calibri', 12,'bold'))
   root.configure(background = "white")
   root.attributes("-fullscreen",True)

   time_str = time.strftime('%H:%M:%S')
   date_str= time.strftime('%d/%m/%Y')

   data = [ ["  Responsável:", motorista_nome],
            ["  Linha:", nome_linha],
            ["  Data início:", data_inicio],
            ["  Hora início:",hora_inicio],
            ["  Data termino:", date_str],
            ["  Hora termino:", time_str],
            ["  Botoeira R"+str(valor_passagem_2)+":",passagens_dinheiro],
            ["  Gratuidade:",passagens_gratuidades],
            ["  Pas. Eletrônicas:",passagens_eletronicas],
            ["  Tot passageiros",total_passagens_turno],
            ["  Venda a bordo",total_dinheiro_2]]

   str_data = ("Responsavel:"+ str(motorista_nome),
               "Linha:"+ str(nome_linha),
                "Data inicio:"+ str(data_inicio),
                "Hora inicio:"+str(hora_inicio),
            "Data termino:"+ str(date_str),
            "Hora termino:"+ str(time_str),
            "Botoeira R"+str(valor_passagem_2)+":",str(passagens_dinheiro),
            "Gratuidade:"+str(passagens_gratuidades),
            "Pas Eletronicas:" +str(passagens_eletronicas),
            "Tot passageiros:" +str(total_passagens_turno),
            "Venda a bordo:" +str(total_dinheiro_2) )

   frame = Frame(root,width = 460, height = 480)
   frame.pack()
   
   titulo = ttk.Label(frame, text= "FECHAMENTO VIAGEM/TURNO")
   titulo.config( font=('Calibri', 18,'bold'))
   titulo.pack(side= 'top')
   
   tree = ttk.Treeview(frame, columns = (1,2), height = 12, show = "headings")
   tree.pack(side = 'top')

   tree.heading(1, text="TIPO")
   tree.heading(2, text="ENTRADAS")

   tree.column(1, width = WIDTH_COL1) #242
   tree.column(2, width = WIDTH_COL2, anchor=E) #238

   for val in data:
      tree.insert('', 'end', values = (val[0], val[1]))
    
   frame.lbl_frase = Label(frame, text= frase_offline_encerramento, font=("Arial 11"))
   frame.lbl_frase.pack(pady=(5,10))

   frame.lbl_fechamento = Label(frame, text="ID ENCERRAMENTO", font=("Arial 15 bold"))
   frame.lbl_fechamento.pack(pady=(5,10))
   frame.lbl_id_fechamento = Label(frame, text= req.getIdFechamentoViagemTela(idFechamentoViagem), font=("Arial 18 bold"))
   frame.lbl_id_fechamento['justify'] = CENTER
   frame.lbl_id_fechamento.pack(pady=(5,10))

   frame.botao_sair = Button(frame, command=lambda:[root.destroy, restart()])
   frame.botao_sair['text'] = 'SAIR'
   frame.botao_sair['font'] = ('Verdana','22','bold')
   frame.botao_sair['height'] = '5'
   frame.botao_sair['width'] = '10'
   frame.botao_sair.pack()

   espaco2 = Label(frame, text="")
   espaco2.pack()
   root.mainloop()

thread_tela = Thread(target=tela_fechamento)
thread_tela.start()

time.sleep(120)
restart()
