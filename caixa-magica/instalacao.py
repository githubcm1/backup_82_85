from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from functools import partial
import sys

path_atual = "/home/pi/caixa-magica"
sys.path.insert(1, path_atual)

sys.path.insert(1, path_atual + '/core/')
import funcoes_serial
import funcoes_logs
import funcoes_tela_corrente

sys.path.insert(2, path_atual + '/sincronismo/')
import req
import os
import time
import json

import tkinter as tk
#from itertools import count
from PIL import Image, ImageTk

local = 'instalacao.py'

os.system("sudo pkill -9 -f keep_alive")
funcoes_tela_corrente.registraTelaAtual("INSTALACAO")

# Inicia servico de check sincronismo, para garantir que o arquivo de configuracao (endpoint)
# esteja criado
ARQ = path_atual + '/../caixa-magica-operacao/sincronismo.json'
os.system("sudo rm -rf " + ARQ)
os.system("sudo touch " + ARQ)

comando = ('sudo echo \'{\"lastSyncAtualizacao\": \"0001-01-01T00:00:00.000000\", \"lastSyncBloq\": \"1900-01-01T00:00:00.000000\", \"lastSyncDesbloq\":\"1900-01-01T00:00:00.000000\"}\' | sudo tee -a '+ ARQ)
os.system(comando)

# Iniciar processo que efetua alocacao da maquina no shellhub
funcoes_logs.insere_log("Adicionando maquina no ShellHub", local, 2)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_adiciona_shellhub.py &")

# Instala o cliente do ZeroTier
funcoes_logs.insere_log("Adicionando client ZeroTier", local, 2)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_inicia_zerotier.py &")

global STRING_ERRO

STRING_ERRO = ""

def iniciar_instalacao(onibus_id):
    global STRING_ERRO

    numero_serie = str(funcoes_serial.getSerial())

    try:
        r = req.instalacao(numero_serie, onibus_id)

        if not r.ok:
            try:
                retorno = json.loads(r.text)
                STRING_ERRO = "Motivo: "+retorno['errors'][0]['message']
            except Exception as e:
                STRING_ERRO = ""

            return False
        else:
            retorno = json.loads(r.text)

            dados = {
            'token': 'hash',
            'operadora': retorno['data']['operadoraId'],
            'acesso': retorno['data']['codigoAcesso'],
            'caixa_id': retorno['data']['caixaMagicaId'],
            'bilhetadoraId': retorno['data']['bilhetadoraId'],
            'numeroVeiculo': retorno['data']['numeroVeiculo'],
            'veiculo': retorno['data']['onibusId']
            }
            funcoes_logs.insere_log("Gravando instalacao.json com o conteudo: " + str(dados), local, 2 )

            with open('/home/pi/caixa-magica-operacao/instalacao.json', 'w') as json_data:
                json_data.write(json.dumps(dados))
            funcoes_logs.insere_log("Gravado instalacao.json", local, 2)

            funcoes_logs.insere_log("Instalacao concluida para numero de serie " + str(numero_serie) + ", onibus id " + str(onibus_id), local, 2 )
        
            funcoes_logs.insere_log("Iniciando aplicacao Caixa Magica com start.sh", local, 2)
            os.system("sudo touch /home/pi/caixa-magica-operacao/recriar_particoes.txt")
            os.system('sudo sh start.sh')
            return True
    except Exception as e:
        funcoes_logs.insere_log("Erro na instalacao: " + str(e), local, 4)
        return False

def tela_validacao_instalacao(mensagem, ambiente):
    root1 = Tk()
    root1.deiconify()
    root1.configure(background = "orange red")
    root1.attributes("-fullscreen", True)

    root1.aviso = Message(root1)
    root1.aviso["text"] = "\n\n" + mensagem + ".\n\n" + "Deseja prosseguir com a instalação?\n\n\n\n"
    root1.aviso["bg"] = "orange red"
    root1.aviso["font"] = ("Verdana", "26", "bold")
    root1.aviso["width"] = "420"
    root1.aviso["justify"] = CENTER
    root1.aviso.pack()
    
    root1.button = Button(root1,command = lambda:[root1.destroy(), root1.quit()])
    root1.button['text'] = 'SIM'
    root1.button['font'] = ('Verdana','30','bold')
    root1.button['height'] = '3'
    root1.button['width'] = '5'
    root1.button.pack(side = "left", padx = (40, 0))

    root1.button = Button(root1,command = lambda:[root1.destroy(), input_instalacao()])
    root1.button['text'] = 'NÃO'
    root1.button['font'] = ('Verdana','30','bold')
    root1.button['height'] = '3'
    root1.button['width'] = '5'
    root1.button.pack(side = "right", padx = (0, 40))

    root1.mainloop()
    return False

def salvar_novos_valores(root):
    onibus_id = root.txt_veiculo.get()
    root.destroy()  
    # root.quit()
    if onibus_id != '':
        iniciar_instalacao(onibus_id)
    tela_instalacao_invalida()
    return False

def tela_instalacao_invalida():
    global STRING_ERRO
    
    root3 = Tk()
    root3.deiconify()
    root3.configure(background = "orange red")
    root3.attributes("-fullscreen", True)

    root3.aviso = Message(root3)
    root3.aviso["text"] = '\n\n\n\n\nINSTALAÇÃO INVÁLIDA\n\nTENTE NOVAMENTE!!!\n'
    root3.aviso["bg"] = "orange red"
    root3.aviso["font"] = ("Verdana", "26", "bold")
    root3.aviso["width"] = "420"
    root3.aviso["justify"] = CENTER
    root3.aviso.pack()

    try:
        if STRING_ERRO != "":
            root3.aviso1 = Message(root3)
            root3.aviso1["text"] = STRING_ERRO
            root3.aviso1["bg"] = "orange red"
            root3.aviso1["font"] = ("Verdana", "18", "bold")
            root3.aviso1["width"] = "420"
            root3.aviso1["justify"] = CENTER
            root3.aviso1.pack()
            STRING_ERRO = ""
    except:
        pass

    root3.after(5000, lambda: [root3.destroy(), input_instalacao()])

    root3.mainloop()
    return False

def input_instalacao():
    funcoes_logs.insere_log("Abrindo tela de instalacao", local, 2)

    root = Tk()
    root.focus_force()
    root.attributes('-fullscreen',True)
    style = ttk.Style(root)
    fonte = ("Arial 50 bold")
    fonte2 = ("Arial 26 bold")
    root.dados_onibus = StringVar()
    root.title('Instalação')
    root.frame_dados_onibus = Frame(root, borderwidth=10)
    root.frame_dados_onibus.pack(fill='x')
    
    root.lbl_onibus = Label(root.frame_dados_onibus, text="Instalação: ", font=fonte2)
    root.lbl_onibus.pack(side='left')

    root.txt_veiculo = Entry(root.frame_dados_onibus, textvariable=root.dados_onibus)
    root.txt_veiculo["font"] = fonte
    root.txt_veiculo.delete(0, END)
    root.txt_veiculo.focus_set()
    root.txt_veiculo.pack(side='left', fill='x', expand=True)

    fonte_botoes = ('Arial', '90', 'bold')

    #frame 123
    root.frame_1 = Frame(root)
    root.frame_1.configure(bg='white')
    root.frame_1.pack(fill='both', expand=True)

    ###111
    root.butt_1 = Button(root.frame_1, command = lambda:key_1(root))
    root.butt_1['text'] = '1'
    root.butt_1['font'] = fonte_botoes
    # root.butt_1["command"] = key_1(root)
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)
    
    ###222
    root.butt_2 = Button(root.frame_1, command = lambda:key_2(root))
    root.butt_2['text'] = '2'
    root.butt_2['font'] = fonte_botoes
    # root.butt_2["command"] = key_2(root)
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)
    
    ###333
    root.butt_3 = Button(root.frame_1, command = lambda:key_3(root))
    root.butt_3['text'] = '3'
    root.butt_3['font'] = fonte_botoes
    # root.butt_3["command"] = key_3(root)
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    # #frame 
    root.frame_4 = Frame(root)
    root.frame_4.configure(bg='white')
    root.frame_4.pack(fill='both', expand=True)

    ###444
    root.butt_4 = Button(root.frame_4, command = lambda:key_4(root))
    root.butt_4['text'] = '4'
    root.butt_4['font'] = fonte_botoes
    # root.butt_4["command"] = key_4(root)
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    ###555
    root.butt_5 = Button(root.frame_4, command = lambda:key_5(root))
    root.butt_5['text'] = '5'
    root.butt_5['font'] = fonte_botoes
    # root.butt_5["command"] = key_5(root)
    root.butt_5.configure(bg='white',
                                    activebackground='white')
    root.butt_5.pack(side='left', fill='both', expand=True)

    ###666
    root.butt_6 = Button(root.frame_4, command = lambda:key_6(root))
    root.butt_6['text'] = '6'
    root.butt_6['font'] = fonte_botoes
    # root.butt_6["command"] = key_6(root)
    root.butt_6.configure(bg='white',
                                    activebackground='white')
    root.butt_6.pack(side='left', fill='both', expand=True)

    #frame 789
    root.frame_7 = Frame(root)
    root.frame_7.configure(bg='white')
    root.frame_7.pack(fill='both', expand=True)
    
    ###777
    root.butt_7 = Button(root.frame_7, command = lambda:key_7(root))
    root.butt_7['text'] = '7'
    root.butt_7['font'] = fonte_botoes
    # root.butt_7["command"] = key_7(root)
    root.butt_7.configure(bg='white',
                                    activebackground='white')
    root.butt_7.pack(side='left', fill='both', expand=True)

    ###888
    root.butt_8 = Button(root.frame_7, command = lambda:key_8(root))
    root.butt_8['text'] = '8'
    root.butt_8['font'] = fonte_botoes
    # root.butt_8["command"] = key_8(root)
    root.butt_8.configure(bg='white',
                                    activebackground='white')
    root.butt_8.pack(side='left', fill='both', expand=True)

    ###999
    root.butt_9 = Button(root.frame_7, command = lambda:key_9(root))
    root.butt_9['text'] = '9'
    root.butt_9['font'] = fonte_botoes
    # root.butt_9["command"] = key_9(root)
    root.butt_9.configure(bg='white',
                                    activebackground='white')
    root.butt_9.pack(side='left', fill='both', expand=True)
    
    #frame espaco
    root.frame_espaco = Frame(root)
    root.frame_espaco.configure(bg='white')
    root.frame_espaco.pack(fill='both', expand=True)
    

    ###_backspace
    root.butt_backspace = Button(root.frame_espaco, command = lambda:def_backspace(root))
    root.butt_backspace['text'] = '←'
    root.butt_backspace['font'] = ('Arial', '51', 'bold')
    root.butt_backspace['width'] = '2'
    # root.butt_backspace["command"] = def_backspace(root)
    root.butt_backspace.configure(bg='white',
                                    activebackground='white')
    root.butt_backspace.pack(side='left', fill='both', expand=True)        


    ###000
    root.butt_0 = Button(root.frame_espaco, command = lambda:key_0(root))
    root.butt_0['text'] = '0'
    root.butt_0['font'] = ('Arial', '100', 'bold')
    # root.butt_0["command"] = key_0(root)
    root.butt_0.configure(bg='white',
                                    activebackground='white')
    root.butt_0.pack(side='left', fill='both', expand=True)

    ###aceitar
    root.butt_confirmar = Button(root.frame_espaco)
    root.butt_confirmar['text'] = '✓'
    root.butt_confirmar['font'] = ('Arial', '68', 'bold')
    root.butt_confirmar["command"] = lambda: salvar_novos_valores(root)
    root.butt_confirmar.configure(bg='white',
                                    activebackground='white')
    root.butt_confirmar.pack(side='left', fill='both', expand=True)
    root.mainloop()
    return False

def key_1(root):
    insert_text(root, '1')  
    
def key_2(root):
    insert_text(root, '2')
    
def key_3(root):
    insert_text(root, '3')

def key_4(root):
    insert_text(root, '4')

def key_5(root):
    insert_text(root, '5')

def key_6(root):
    insert_text(root, '6')

def key_7(root):
    insert_text(root, '7')

def key_8(root):
    insert_text(root, '8')

def key_9(root):
    insert_text(root, '9')

def key_0(root):
    insert_text(root, '0')

#espaco
def def_espaco(root):
    root.insert_text(' ')

#apagar
def def_backspace(root):
    if root.focus_get()==root.txt_veiculo:
        pos_fin = len(root.txt_veiculo.get()) -1
        root.txt_veiculo.delete(int(pos_fin))

def insert_text(root, value):
    if root.focus_get() == root.txt_veiculo:
        root.txt_veiculo.insert(END, value.upper())

input_instalacao()
