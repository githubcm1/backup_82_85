import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"

import funcoes_tela_corrente
import json
import time 
import os
from tkinter import *
import tkinter.messagebox
from tkinter import ttk
from tkinter import messagebox
from threading import Thread 
sys.path.insert(1, path_atual + "/../")
from sincronismo import req as sincronismo

import datetime
from datetime import timezone
import db
import funcoes_logs
import funcoes_viagem
import funcoes_serial
import socket
import funcoes_camera

import subprocess as sp

from PIL import Image, ImageTk
import tkinter as tk
import threading
from itertools import count

sys.path.insert(2, path_atual +'/../tela/')
from tela.AnimatedGIF import *
import funcoes_telas

sys.path.insert(3, path_atual)
import funcoes_atualiza

local = 'telas_init.py'

funcoes_logs.insere_log("Iniciando " + local, local, 2)

NUM_TENTATIVAS_TELA = 10
CNT_TENTATIVAS_TELA = 0

global fonte_botoes
fonte_botoes = ('Courier', '64', 'bold')

class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)

class TelaAguarde(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    def destroy(self):
        self.root.destroy()

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()

    def run(self):
        self.root = tk.Tk()
        self.root.configure(background = 'white')
        self.root.attributes("-fullscreen",True)

        espaco = tk.Label(self.root, text = '\n\n\n\n\n\n',fg='black',bg='white',font=('Verdana','23','bold'))
        espaco.config(bg = 'white')
        espaco.pack()

        #### Logo BUSPAY
        imagem = tk.PhotoImage(file=path_atual +"/../tela/Camada22.png")
        tk.Label(self.root, image=imagem, bg='white').pack()

        #### GIF aguarde
        anim = AnimatedGif(self.root, path_atual+'/../tela/Spinner-1s-200px.gif', 0.02)
        anim.pack()
        anim.start()

        self.root.mainloop()


HOST = 'localhost'  # The server's hostname or IP address
PORT = 30090        # The port used by the server

funcoes_logs.insere_log("Determinado HOST como " + HOST + " e porta " + str(PORT), local, 2)

### Abrindo jsons
# instalacao.json
try:
    funcoes_logs.insere_log("Abrindo instalacao.json", local, 2)
    with open(path_atual+ "/../../caixa-magica-operacao/instalacao.json", "r") as json_data:
        dados_instalacao = json.load(json_data)
    
        onibus_id = dados_instalacao["veiculo"]

        funcoes_logs.insere_log("Veiculo obtido: " + str(onibus_id), local, 2)
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir 'instalacao.json' em 'telas_init.py': "+ str(e), local, 4)

# Adicionado por Fernando Andre de Almeida em 2021-07-27
def getSerial():
    return funcoes_serial.getSerial()

def getNotIntegrated():
    conn1 = db.Conexao()
    query = conn1.consultar("select count(*) from cobrancas where enviada=false")
    total = query[0][0]
    return total

def inicia_viagem(tipo, id_web_motorista, status):
    funcoes_logs.insere_log("Chamando iniciar viagem .Parametros -> tipo=" + str(tipo) + ", id_motorista = " + str(id_web_motorista) + ", status=" + str(status), local, 2)
    s = sincronismo.iniciar_viagem(tipo, id_web_motorista, status)
    response = s.json()
    funcoes_logs.insere_log("Retorno iniciar viagem: " + str(response), local, 2)

    funcoes_logs.insere_log("Gravando viagem.json com dados: " + str(response), local)
    with open(path_atual +"/../../caixa-magica-operacao/viagem.json", "w+") as json_data:
        json.dump(response, json_data)

    try:
        os.remove(path_atual + "/../../caixa-magica-operacao/passagens_viagem.json")
    except:
        pass
    funcoes_logs.insere_log("chamando inicializar_sistema.sh", local, 2)
    os.system("sudo sh inicializar_sistema.sh &")

# Checa se a viagem exige informe no sentido da linha
def informe_sentido_habilitado():
    return funcoes_viagem.informe_sentido_habilitado()

### Tela Comunicação
def core_init(nome_motorista, id_qrcode_motorista, id_web_motorista):
    funcoes_logs.insere_log("Responsável Detectado: " + nome_motorista, local, 2)

    funcoes_logs.insere_log("Chamando get_viagem_responsavel para o motorista " + nome_motorista + "(id " + str(id_web_motorista) +")", local, 2)
    r = sincronismo.get_viagem_responsavel(id_web_motorista)

    # Mata a tela de aguarde, caso esteja aberta
    funcoes_telas.kill_tela_aguarde()

    # A primeira regra consiste em checar se existem viagens alocadas. Isso eh feito via uma chamada de web service
    # Se essa chamada der retorno, criamos um id de viagem interno e mandamos criar a viagem na sequencia via WS (assincrono)
    # Caso o retorno tenha dado timeout ou deu algum erro, 

    # Se o retorno nao foi ok (seja por timeout ou por falta de rede), iniciamos a tela de informe de linha
    if len(r) <= 0:
        print("Entrei tela digitacao da linha")
        tela_confirmacao(nome_motorista)
        return
    # Caso o web service deu retorno
    else:
        print("Entrei trecho abertura automatica")

        inicializacao = '{"nome_linha":"' + r[2] + '", "linhaId":"' + str(r[0]) + '", "horarioid":"' + str(r[4]) + '","viagemid":"' + str(r[3]) +'", "horario": "' + str(r[4]) + '"}'
        funcoes_logs.insere_log("Removendo inicializacao.json", local, 2)
        os.system("sudo rm -rf " + path_atual + "/../../caixa-magica-operacao/inicializacao.json")

        funcoes_logs.insere_log("Gerando inicializacao.json com conteudo: " + inicializacao, local, 2)
        string_exec = "sudo echo '" + inicializacao + "' | sudo tee -a " + path_atual + "/../../caixa-magica-operacao/inicializacao.json"
        os.system(string_exec)
        funcoes_logs.insere_log("Gerado inicializacao.json", local, 2)

        # Abre automaticamente, passando como argumento o ID da linha
        inicializar_sistema_linha(r[0])
        return

    #### INICIO REMOVIDO POR FERNANDO ###
    #if operacao_on():
    #    funcoes_logs.insere_log("Finalizada checagem 'operacao_on'. Está online.",local)
    #    funcoes_logs.insere_log("inicio GET viagem Responsável",local)
    #    inicio_sync = datetime.datetime.now()

    #    funcoes_logs.insere_log("Chamando get_viagem_responsavel para o motorista " + nome_motorista + "(id " + str(id_web_motorista) +")", local)
    #    r = sincronismo.get_viagem_responsavel(id_web_motorista)
    #    fim_sync = datetime.datetime.now()
    #    tempo_requisicao = fim_sync - inicio_sync 
    #    funcoes_logs.insere_log("Tempo Requisição GET viagem Responsável" + str(tempo_requisicao), local)
        
    #    tipo = 0
    #    status = 1

    #    if r:
    #        inicializacao = r.json()
    #        with open("/home/pi/caixa-magica-operacao/inicializacao.json", "w") as json_data:
    #            json.dump(inicializacao, json_data)
    #        
    #        if informe_sentido_habilitado == False:
    #            
    #            inicia_viagem(tipo, id_web_motorista, status)
    #            
    #        # Se o informe esta habilitado, exibir tela de escolha
    #        else:
    #            tela_informe_sentido_viagem(tipo, id_web_motorista, status, True, "0")
    #    else:
    #        tela_confirmacao(nome_motorista)
    #else:
    #    alert_no_network()
    #    tela_input_offline()
    #    return

    ### TERMINO REMOVIDO POR FERNANDO ####

def json_sentido_linha(SENTIDO):
    funcoes_viagem.json_sentido_linha(SENTIDO)

def tela_informe_sentido_viagem(id_web_motorista,  abre_viagem_final, par_codigo_linha):
   funcoes_tela_corrente.registraTelaAtual("TELA_INFORME_SENTIDO_VIAGEM")
   root2 = Tk()
   style = ttk.Style(root2)
   root2.update()
   root2.deiconify()
   root2.configure(background = "white")
   root2.attributes("-fullscreen",True)
   
   fonte2 = ("Arial 26 bold")

   root2.verif2 = Message(root2, text = "Informe o sentido da viagem", font=fonte2, bg='white')
   root2.verif2['width'] = '420'
   root2.verif2['justify'] = CENTER
   root2.verif2.pack(side = 'top')

   if abre_viagem_final == True:
       root2.butt_yes = Button(root2, command = lambda:[root2.destroy(), root2.quit(), json_sentido_linha('IDA'),inicia_viagem(tipo, id_web_motorista, status)])
   else:
       root2.butt_yes = Button(root2, command = lambda:[root2.destroy(), root2.quit(), json_sentido_linha('IDA'), salvar_linha_id(root2, par_codigo_linha)])
  
   root2.butt_yes['text'] = 'IDA'
   root2.butt_yes['font'] = ('Verdana','23','bold')
   root2.butt_yes['height'] = '5'
   root2.butt_yes['width'] = '6'

   root2.butt_yes.configure(bg='white', activebackground='white')
   root2.butt_yes.pack(side='left', padx = 30)

   if abre_viagem_final == True:
       root2.butt_no = Button(root2,command = lambda:[root2.destroy(), root2.quit(), json_sentido_linha('VOLTA'),inicia_viagem(tipo, id_web_motorista,status)])
   else:
       root2.butt_no = Button(root2,command = lambda:[root2.destroy(), root2.quit(), json_sentido_linha('VOLTA'), salvar_linha_id(root2, par_codigo_linha)])
   
   root2.butt_no['text'] = 'VOLTA'
   root2.butt_no['font'] = ('Verdana','23','bold')
   root2.butt_no['height'] = '5'
   root2.butt_no['width'] = '6'

   root2.butt_no.configure(bg='white', activebackground='white')
   root2.butt_no.pack(side='right',padx = (0,30))

   root2.mainloop()
   return

def remove_frames(root):
    try:
        root.frame_1.pack_forget()
    except:
        pass

    try:
        root.frame_2.pack_forget()
    except:
        pass

    try:
        root.frame_3.pack_forget()
    except:
        pass

    try:
        root.frame_1a.pack_forget()
    except:
        pass

    try:
        root.frame_2a.pack_forget()
    except:
        pass

    try:
        root.frame_3a.pack_forget()
    except:
        pass

    try:
        root.frame_1b.pack_forget()
    except:
        pass

    try:
        root.frame_2b.pack_forget()
    except:
        pass

    try:
        root.frame_3b.pack_forget()
    except:
        pass

    try:
        root.butt_voltar.pack_forget()
    except:
        pass

    try:
        root.frame_espaco.pack_forget()
    except:
        pass

    try:
        root.butt_0_9.pack_forget()
    except:
        pass

    try:
        root.butt_alfa1.pack_forget()
    except:
        pass

    try:
        root.butt_alfa2.pack_forget()
    except:
        pass

# parte da tela com teclado numerico
def tela_input_linha_alfa1(root):
    global fonte_botoes
    remove_frames(root)

    #frame 123
    root.frame_1a = Frame(root)
    root.frame_1a.configure(bg='white')
    root.frame_1a.pack(fill='both', expand=True)

    root.butt_1 = Button(root.frame_1a, command = lambda:key_valor(root,'A'))
    root.butt_1['text'] = 'A'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)
    
    root.butt_2 = Button(root.frame_1a, command = lambda:key_valor(root,'B'))
    root.butt_2['text'] = 'B'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)
    
    ###333
    root.butt_3 = Button(root.frame_1a, command = lambda:key_valor(root,'C'))
    root.butt_3['text'] = 'C'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_1a, command = lambda:key_valor(root,'D'))
    root.butt_4['text'] = 'D'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    #frame 123
    root.frame_2a = Frame(root)
    root.frame_2a.configure(bg='white')
    root.frame_2a.pack(fill='both', expand=True)

    ###111
    root.butt_1 = Button(root.frame_2a, command = lambda:key_valor(root,'E'))
    root.butt_1['text'] = 'E'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)
    
    ###222
    root.butt_2 = Button(root.frame_2a, command = lambda:key_valor(root,'F'))
    root.butt_2['text'] = 'F'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)
    
    ###333
    root.butt_3 = Button(root.frame_2a, command = lambda:key_valor(root,'G'))
    root.butt_3['text'] = 'G'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_2a, command = lambda:key_valor(root,'H'))
    root.butt_4['text'] = 'H'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    root.frame_3a = Frame(root)
    root.frame_3a.configure(bg='white')
    root.frame_3a.pack(fill='both', expand=True)

    root.butt_1 = Button(root.frame_3a, command = lambda:key_valor(root,'I'))
    root.butt_1['text'] = 'I'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)
    
    ###222
    root.butt_2 = Button(root.frame_3a, command = lambda:key_valor(root,'J'))
    root.butt_2['text'] = 'J'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)
    
    ###333
    root.butt_3 = Button(root.frame_3a, command = lambda:key_valor(root,'K'))
    root.butt_3['text'] = 'K'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_3a, command = lambda:key_valor(root,'L'))
    root.butt_4['text'] = 'L'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    root.frame_espaco = Frame(root)
    root.frame_espaco.configure(bg='white')
    root.frame_espaco.pack(fill='both', expand=True)

    ###_backspace
    root.butt_backspace = Button(root.frame_espaco, command = lambda:def_backspace(root))
    root.butt_backspace['text'] = '←'
    root.butt_backspace['font'] = fonte_botoes
    root.butt_backspace['width'] = '2'
    root.butt_backspace.configure(bg='white',
                                    activebackground='white')
    root.butt_backspace.pack(side='left', fill='both', expand=True)


    root.butt_0 = Button(root.frame_espaco, command = lambda:key_valor(root, 'M'))   
    root.butt_0['text'] = 'M'
    root.butt_0['font'] = fonte_botoes
    root.butt_0.configure(bg='white',
                                    activebackground='white')
    root.butt_0.pack(side='left', fill='both', expand=True)

    root.butt_confirmar = Button(root.frame_espaco,command = lambda:[check_linha(root, root.txt_veiculo.get())])

    ##root.butt_confirmar = Button(root.frame_espaco,command = lambda: salvar_linha_id(root))
    root.butt_confirmar['text'] = '✓'
    root.butt_confirmar['font'] = fonte_botoes 

    root.butt_confirmar.configure(bg='white',
                                    activebackground='white')
    root.butt_confirmar.pack(side='left', fill='both', expand=True)

    # Monta rodape
    tela_input_linha_rodape(root)

def tela_input_linha_alfa2(root):
    global fonte_botoes
    remove_frames(root)

    root.frame_1b = Frame(root)
    root.frame_1b.configure(bg='white')
    root.frame_1b.pack(fill='both', expand=True)

    root.butt_1 = Button(root.frame_1b, command = lambda:key_valor(root,'N'))
    root.butt_1['text'] = 'N'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)

    root.butt_2 = Button(root.frame_1b, command = lambda:key_valor(root,'O'))
    root.butt_2['text'] = 'O'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)

    ###333
    root.butt_3 = Button(root.frame_1b, command = lambda:key_valor(root,'P'))
    root.butt_3['text'] = 'P'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_1b, command = lambda:key_valor(root,'Q'))
    root.butt_4['text'] = 'Q'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    root.frame_2b = Frame(root)
    root.frame_2b.configure(bg='white')
    root.frame_2b.pack(fill='both', expand=True)

    ###111
    root.butt_1 = Button(root.frame_2b, command = lambda:key_valor(root,'R'))
    root.butt_1['text'] = 'R'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)

    ###222
    root.butt_2 = Button(root.frame_2b, command = lambda:key_valor(root,'S'))
    root.butt_2['text'] = 'S'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)

    ###333
    root.butt_3 = Button(root.frame_2b, command = lambda:key_valor(root,'T'))
    root.butt_3['text'] = 'T'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_2b, command = lambda:key_valor(root,'U'))
    root.butt_4['text'] = 'U'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    root.frame_3b = Frame(root)
    root.frame_3b.configure(bg='white')
    root.frame_3b.pack(fill='both', expand=True)

    root.butt_1 = Button(root.frame_3b, command = lambda:key_valor(root,'V'))
    root.butt_1['text'] = 'V'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)

    ###222
    root.butt_2 = Button(root.frame_3b, command = lambda:key_valor(root,'W'))
    root.butt_2['text'] = 'W'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)

    ###333
    root.butt_3 = Button(root.frame_3b, command = lambda:key_valor(root,'X'))
    root.butt_3['text'] = 'X'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    root.butt_4 = Button(root.frame_3b, command = lambda:key_valor(root,'Y'))
    root.butt_4['text'] = 'Y'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    root.frame_espaco = Frame(root)
    root.frame_espaco.configure(bg='white')
    root.frame_espaco.pack(fill='both', expand=True)

    ###_backspace
    root.butt_backspace = Button(root.frame_espaco, command = lambda:def_backspace(root))
    root.butt_backspace['text'] = '←'
    root.butt_backspace['font'] = fonte_botoes
    root.butt_backspace['width'] = '2'
    root.butt_backspace.configure(bg='white',
                                    activebackground='white')
    root.butt_backspace.pack(side='left', fill='both', expand=True)


    ###000
    root.butt_0 = Button(root.frame_espaco, command = lambda:key_valor(root, 'Z'))
    root.butt_0['text'] = 'Z'
    root.butt_0['font'] = fonte_botoes
    root.butt_0.configure(bg='white',
                                    activebackground='white')
    root.butt_0.pack(side='left', fill='both', expand=True)

    root.butt_confirmar = Button(root.frame_espaco,command = lambda:[check_linha(root, root.txt_veiculo.get() )])

    ##root.butt_confirmar = Button(root.frame_espaco,command = lambda: salvar_linha_id(root))
    root.butt_confirmar['text'] = '✓'
    root.butt_confirmar['font'] = fonte_botoes

    root.butt_confirmar.configure(bg='white',
                                    activebackground='white')
    root.butt_confirmar.pack(side='left', fill='both', expand=True)

    # Monta rodape
    tela_input_linha_rodape(root)


# parte da tela com teclado numerico
def tela_input_linha_numerico(root):
    global fonte_botoes
    remove_frames(root)

    #frame 123
    root.frame_1 = Frame(root)
    root.frame_1.configure(bg='white')
    root.frame_1.pack(fill='both', expand=True)

    ###111
    root.butt_1 = Button(root.frame_1, command = lambda:key_1(root))
    root.butt_1['text'] = '1'
    root.butt_1['font'] = fonte_botoes
    root.butt_1.configure(bg='white', activebackground='white')
    root.butt_1.pack(side='left', fill='both', expand=True)
    
    ###222
    root.butt_2 = Button(root.frame_1, command = lambda:key_2(root))
    root.butt_2['text'] = '2'
    root.butt_2['font'] = fonte_botoes
    root.butt_2.configure(bg='white', activebackground='white')
    root.butt_2.pack(side='left', fill='both', expand=True)
    
    ###333
    root.butt_3 = Button(root.frame_1, command = lambda:key_3(root))
    root.butt_3['text'] = '3'
    root.butt_3['font'] = fonte_botoes
    root.butt_3.configure(bg='white',
                                    activebackground='white')
    root.butt_3.pack(side='left', fill='both', expand=True)

    # #frame 
    root.frame_2 = Frame(root)
    root.frame_2.configure(bg='white')
    root.frame_2.pack(fill='both', expand=True)

    ###444
    root.butt_4 = Button(root.frame_2, command = lambda:key_4(root))
    root.butt_4['text'] = '4'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    ###555
    root.butt_5 = Button(root.frame_2, command = lambda:key_5(root))
    root.butt_5['text'] = '5'
    root.butt_5['font'] = fonte_botoes
    root.butt_5.configure(bg='white',
                                    activebackground='white')
    root.butt_5.pack(side='left', fill='both', expand=True)

    ###666
    root.butt_6 = Button(root.frame_2, command = lambda:key_6(root))
    root.butt_6['text'] = '6'
    root.butt_6['font'] = fonte_botoes
    root.butt_6.configure(bg='white',
                                    activebackground='white')
    root.butt_6.pack(side='left', fill='both', expand=True)

    #frame 789
    root.frame_3 = Frame(root)
    root.frame_3.configure(bg='white')
    root.frame_3.pack(fill='both', expand=True)
    
    ###777
    root.butt_7 = Button(root.frame_3, command = lambda:key_7(root))
    root.butt_7['text'] = '7'
    root.butt_7['font'] = fonte_botoes
    root.butt_7.configure(bg='white',
                                    activebackground='white')
    root.butt_7.pack(side='left', fill='both', expand=True)

    ###888
    root.butt_8 = Button(root.frame_3, command = lambda:key_8(root))
    root.butt_8['text'] = '8'
    root.butt_8['font'] = fonte_botoes
    root.butt_8.configure(bg='white',
                                    activebackground='white')
    root.butt_8.pack(side='left', fill='both', expand=True)

    ###999
    root.butt_9 = Button(root.frame_3, command = lambda:key_9(root))
    root.butt_9['text'] = '9'
    root.butt_9['font'] = fonte_botoes
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
    root.butt_backspace['font'] = fonte_botoes
    root.butt_backspace['width'] = '2'
    root.butt_backspace.configure(bg='white',
                                    activebackground='white')
    root.butt_backspace.pack(side='left', fill='both', expand=True)


    ###000
    root.butt_0 = Button(root.frame_espaco, command = lambda:key_0(root))   
    root.butt_0['text'] = '0'
    root.butt_0['font'] = fonte_botoes
    root.butt_0.configure(bg='white',
                                    activebackground='white')
    root.butt_0.pack(side='left', fill='both', expand=True)
    
    root.butt_confirmar = Button(root.frame_espaco,command = lambda:[check_linha(root, root.txt_veiculo.get())] )

    root.butt_confirmar['text'] = '✓'
    root.butt_confirmar['font'] = fonte_botoes 

    root.butt_confirmar.configure(bg='white',activebackground='white')
    root.butt_confirmar.pack(side='left', fill='both', expand=True)

    # Monta rodape
    tela_input_linha_rodape(root)

def desativa_confirmar(root):
    root.butt_confirmar['state'] = DISABLED

def tela_input_linha_rodape(root):
    fonte = ("Verdana", "18", "bold")

    root.butt_voltar = Button(root)
    root.butt_voltar["text"] = "Voltar"
    root.butt_voltar["bg"] = "white"
    root.butt_voltar["font"] = fonte
    root.butt_voltar["height"] = "3"
    root.butt_voltar["command"] = lambda: [funcoes_camera.atualiza_lock_tela_viagem(False), root.destroy(), root.quit()]
    root.butt_voltar.pack(side='left',fill='both', expand=True)

    root.butt_0_9 = Button(root)
    root.butt_0_9["text"] = "0-9"
    root.butt_0_9["bg"] = "white"
    root.butt_0_9["font"] = fonte
    root.butt_0_9["height"] = "3"
    root.butt_0_9['command'] = lambda: [tela_input_linha_numerico(root)]
    root.butt_0_9.pack(side='left',fill='both', expand=True)

    root.butt_alfa1 = Button(root)
    root.butt_alfa1["text"] = "A-M"
    root.butt_alfa1["bg"] = "white"
    root.butt_alfa1["font"] = fonte
    root.butt_alfa1["height"] = "3"
    root.butt_alfa1['command'] = lambda: [tela_input_linha_alfa1(root)]
    root.butt_alfa1.pack(side='left',fill='both', expand=True)

    root.butt_alfa2 = Button(root)
    root.butt_alfa2["text"] = "N-Z"
    root.butt_alfa2["bg"] = "white"
    root.butt_alfa2["font"] = fonte
    root.butt_alfa2["height"] = "3"
    root.butt_alfa2['command'] = lambda: [tela_input_linha_alfa2(root)]
    root.butt_alfa2.pack(side='left',fill='both', expand=True)

# Checa se a linha existe
def check_linha(root, linha):
    desativa_confirmar(root)
    conn1 = db.Conexao()
    linha_invalida = False
    
    funcoes_logs.insere_log("Checando se existem linhas na base local", local, 2)
    sql = "select count(*) from linhas where ativa=true"
    result = conn1.consultar(sql)

    for row in result:
        # Se nao tem linhas registradas, deixamos que o usuario informe qualquer valor
        if row[0] <= 0:
            funcoes_logs.insere_log("Sem linhas cadastradas. Permitindo a linha informada " + str(linha), local, 3)
            linha_invalida = False
        # Caso exista ao menos 1 linha, o usuario motorista so pode informar dentro desse intervalo
        else:
            funcoes_logs.insere_log("Checando se a linha informada (" + str(linha) + ") existe no BD local", local, 2)

            dados = (str(linha), )
            sql = "select id from linhas where codigo = %s and ativa=true limit 1"
            result = conn1.consultarComBind(sql, dados)
            
            idLinha = ""
            linha_invalida = True

            for row in result:
                funcoes_logs.insere_log("Linha " + str(linha) + " existe no BD local", local, 2)
                linha_invalida = False
                idLinha = row[0]

    # Se foi uma linha invalida, notificamos
    if linha_invalida:
        funcoes_logs.insere_log("Mostrando tela de linha invalida", local, 3)
        root.destroy()
        root.quit()
        viagem_invalida()
    # Se for linha valida, prosseguimos
    else:
        # Checamos aqui se a empresa exige informe do sentido de viagem
        # Se exige, redirecionamos pra tela de informe. 
        # Apos informar o sentido, ele devera ser redirecionado pra tela de confirmacao pre-abertura
        if informe_sentido_habilitado():
            tela_informe_sentido_viagem(id_web_motorista, False, linha)
        # Caso contrario, abre tela de confirmacao
        else:
            # Por padrao, marca a linha como sempre IDA
            json_sentido_linha('IDA')
            salvar_linha_id(root, linha) 

        try:
            root.destroy()
            root.quit()
        except:
            pass

### Telas Código
def tela_input_linha():
    global fonte_botoes

    funcoes_tela_corrente.registraTelaAtual("TELA_INFORME_LINHA")

    root = Tk()
    style = ttk.Style(root)
    root.attributes("-fullscreen",True)
    
    fonte = ("Arial 50 bold")
    fonte2 = ("Arial 26 bold")
    root.dados_onibus = StringVar()
    root.title('Insira Código Linha')
    root.frame_dados_onibus = Frame(root, borderwidth=10)
    root.frame_dados_onibus.pack(fill='x')
    
    root.lbl_onibus = Label(root.frame_dados_onibus, text="Código\nLinha: ", font=fonte2)
    root.lbl_onibus.pack(side='left')

    root.txt_veiculo = Entry(root.frame_dados_onibus, textvariable=root.dados_onibus)
    root.txt_veiculo["font"] = fonte
    root.txt_veiculo.delete(0, END)
    root.txt_veiculo.focus_set()
    root.txt_veiculo.pack(side='left', fill='x', expand=True)
   
    # apresenta tela inicial com teclado numerico
    tela_input_linha_numerico(root)

    root.mainloop()

### Salvando Viagem
def salvar_linha_id(root, par_codigo_linha):
        global codigo_linha

        codigo_linha = par_codigo_linha

        funcoes_logs.insere_log("Código Linha ID: " + str(codigo_linha), local, 2)
        funcoes_logs.insere_log("Inicio GET Linha ID: " + str(codigo_linha), local, 2)    
        inicio_sync = datetime.datetime.now()

        funcoes_logs.insere_log("Chamando get_linha_id", local, 2)
        r = sincronismo.get_linha_id(codigo_linha) # era get_viagem_id
        fim_sync = datetime.datetime.now()
        tempo_requisicao = fim_sync - inicio_sync 
        funcoes_logs.insere_log("Tempo Requisição GET linha ID: " + str(tempo_requisicao), local, 2) 
 
        if r == None:
            funcoes_logs.insere_log("Viagem invalida, mostrando tela ao operador", local, 3)
            root.destroy()
            root.quit()
            viagem_invalida()
        else:
            inicializacao = '{"nome_linha":"' + r[1] + '", "linhaId":"' + str(r[0]) + '", "horarioid":"' + str(r[3]) + '","viagemid":"' + str(r[2]) +'", "horario": "' + str(r[4]) + '"}'
            funcoes_logs.insere_log("Removendo inicializacao.json", local, 2)
            os.system("sudo rm -rf " + path_atual + "/../../caixa-magica-operacao/inicializacao.json")

            funcoes_logs.insere_log("Gerando inicializacao.json com conteudo: " + inicializacao, local, 2)
            string_exec = "sudo echo '" + inicializacao + "' | sudo tee -a " + path_atual + "/../../caixa-magica-operacao/inicializacao.json"
            os.system(string_exec)
            funcoes_logs.insere_log("Gerado inicializacao.json", local, 2)

            funcoes_logs.insere_log("Abrindo inicializacao.json para validacao da viagem", local, 2)
            with open(path_atual +"/../../caixa-magica-operacao/inicializacao.json") as json_data:
                try:
                    dados_viagem = json.load(json_data)

                    codigo_linha = dados_viagem['linhaId']
                    dia_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                    nome_linha = dados_viagem['nome_linha']
                    num_dia = datetime.datetime.today().weekday()
                    dia = dia_semana[num_dia]  
                    horario = dados_viagem['horario']
                    id_viagem = dados_viagem['viagemid']

                    try:
                        with open(path_atual + "/../../caixa-magica-operacao/sentido_informado_motorista.json") as json_data_sentido:
                            dados_sentido = json.load(json_data_sentido)
                            sentido_volta = dados_sentido['sentido']
                    except:
                        sentido_volta = "IDA"

                    funcoes_logs.insere_log("Abrindo tela validacao da linha", local, 2)
                    # redireciona para tela de validacao da linha
                    root.destroy()
                    root.quit()
                    tela_validacao_linha(nome_linha, dia, sentido_volta, horario, id_viagem, codigo_linha)

                except Exception as e:
                    print("Except**************:" + str(e) )
                    
### Alertas
def tela_confirmacao(nome_motorista):
   funcoes_tela_corrente.registraTelaAtual("TELA_MOTORISTA_PRE_INFORME_LINHA")

   # Efetuamos o lock da camera
   funcoes_camera.atualiza_lock_tela_viagem(True)

   #funcoes_telas.inicia_tela_aguarde()
   #time.sleep(1)

   root2 = Tk()
   style = ttk.Style(root2)
   root2.update()
   root2.deiconify()
   root2.configure(background = "white")
   root2.attributes("-fullscreen",True)

   root2.verif2 = Message(root2, text = nome_motorista + ", não existem viagens programadas nesse ônibus para você. Deseja programar uma nova viagem para este veículo?",fg='black',bg='white',font=('Verdana','23','bold'))
   root2.verif2['width'] = '420'
   root2.verif2['justify'] = CENTER
   root2.verif2.pack(side = 'top')
     
   root2.butt_yes = Button(root2, command = lambda:[funcoes_camera.atualiza_lock_tela_viagem(True), funcoes_telas.kill_tela_aguarde(), root2.destroy(), root2.quit(), tela_input_linha()])
   root2.butt_yes['text'] = 'SIM'
   root2.butt_yes['font'] = ('Verdana','23','bold')
   root2.butt_yes['height'] = '3'
   root2.butt_yes['width'] = '6'

   root2.butt_yes.configure(bg='pale green', activebackground='white')
   root2.butt_yes.pack(side='left', padx = 40)

   root2.butt_no = Button(root2,command = lambda:[funcoes_camera.atualiza_lock_tela_viagem(False), funcoes_telas.kill_tela_aguarde(), root2.destroy(), root2.quit()])
   root2.butt_no['text'] = 'NÃO'
   root2.butt_no['font'] = ('Verdana','23','bold')
   root2.butt_no['height'] = '3'
   root2.butt_no['width'] = '6'

   root2.butt_no.configure(bg='tomato3', activebackground='white')
   root2.butt_no.pack(side='right',padx = (0,40))

   root2.mainloop()
   return

def viagem_invalida():
    funcoes_tela_corrente.registraTelaAtual("TELA_LINHA_INVALIDA")
    root3 = Tk()
    root3.deiconify()
    root3.configure(background = "orange red")
    root3.attributes("-fullscreen", True)

    root3.aviso = Message(root3)
    root3.aviso["text"] = 'LINHA INVÁLIDA!!! \n\n\n Por favor, insira outro código\n\n\n'
    root3.aviso["bg"] = "orange red"
    root3.aviso["font"] = ("Verdana", "26", "bold")
    root3.aviso["width"] = "420"
    root3.aviso["justify"] = CENTER
    root3.aviso.pack()
    
    root3.button = Button(root3,command = lambda:[root3.destroy(), root3.quit(),tela_input_linha()])
    root3.button['text'] = 'OK'
    root3.button['font'] = ('Verdana','30','bold')
    root3.button['height'] = '3'
    root3.button['width'] = '6'
    root3.button.pack()

    root3.mainloop()
    return False

def alert_no_network():
   global root1
   root1 = Tk()
   style = ttk.Style(root1)
   root1.update()
   root1.deiconify()
   root1.configure(background = "red")
   root1.attributes("-fullscreen",True)

   verif2 = Label(root1, text = "\n\n\n\n\n\n\n\nSem Conexão\ncom Internet",fg='black',bg='red',font=('Verdana','23','bold'))
   verif2.pack(side = 'top',fill = X)

   root1.after(3000, lambda: [root1.quit(), root1.destroy()])

   root1.mainloop()
   return

def alerta_fail_operadores():
   global root1
   root1 = Tk()
   style = ttk.Style(root1)
   root1.update()
   root1.deiconify()
   root1.configure(background = "red")
   root1.attributes("-fullscreen",True)

   verif2 = Label(root1, text = "\n\n\n\n\n\nSem operadores\nna base local.\n\nEfetuando reboot\naplicação.",fg='white',bg='red',font=('Verdana','23','bold'))
   verif2.pack(side = 'top',fill = X)

   root1.after(3000, lambda: [root1.quit(), root1.destroy()])

   root1.mainloop()
   return

#def alerta_fail_tela():
#   global root1
#   root1 = Tk()
#   style = ttk.Style(root1)
#   root1.update()
#   root1.deiconify()
#   root1.configure(background = "red")
#   root1.attributes("-fullscreen",True)

#   verif2 = Label(root1, text = "\n\n\n\n\n\nFalha inicializaçao\ndo video.\n\nEfetuando reboot\naplicação.",fg='white',bg='red',font=('Verdana','23','bold'))
#   verif2.pack(side = 'top',fill = X)

#   root1.after(3000, lambda: [root1.quit(), root1.destroy()])

#   root1.mainloop()
#   return

def alerta():
   root1 = Tk()
   style = ttk.Style(root1)
   root1.update()
   root1.deiconify()
   root1.configure(background = "white")
   root1.attributes("-fullscreen",True)

   verif2 = Message(root1, text = "\n\n\n\n\n\nVocê solicitou cadastrar uma nova viagem por código de linha.\nVocê será direcionado para a tela no qual será solicitado o código da linha que deseja realizar",fg='black',bg='white',font=('Verdana','20','bold'))
   verif2['width'] = '420'
   verif2['justify'] = CENTER
   verif2.pack(side = 'top',fill = X)

   root1.after(6000, lambda: [root1.destroy(), root1.quit(), tela_input_linha()])

   root1.mainloop()
   return

### Telas Validação
def tela_validacao_linha(nome_linha, dia, sentido, horario, id, codigo_linha):
    funcoes_tela_corrente.registraTelaAtual("TELA_CONFIRMA_LINHA")
    root3 = Tk()
    root3.update()
    root3.deiconify()
    root3.configure(background = "white")
    root3.attributes("-fullscreen", True)

    root3.aviso = Message(root3)
    root3.aviso["text"] = nome_motorista + ", você confirma os dados para a abertura da LINHA?"
    root3.aviso["bg"] = "white"
    root3.aviso["font"] = ("Verdana", "23", "bold")
    root3.aviso["width"] = "420"
    root3.aviso["justify"] = CENTER
    root3.aviso.pack(pady=(20, 50))

    root3.nome_linha = Label(root3)
    root3.nome_linha["text"] = "Linha:\n" + nome_linha
    root3.nome_linha["bg"] = "white"
    root3.nome_linha["width"] = '420'
    root3.nome_linha['wraplength'] = '420'
    root3.nome_linha["justify"] = CENTER
    root3.nome_linha["font"] = ('Verdana','23','bold')
    root3.nome_linha.pack()

    root3.dia = Label(root3)
    root3.dia["text"] = "Dia: " + str(dia)
    root3.dia["bg"] = "white"
    root3.dia["font"] = ('Verdana','23','bold')
    root3.dia.pack()

    root3.sentido = Label(root3)
    root3.sentido["text"] = "Sentido: " + str(sentido)
    root3.sentido["bg"] = "white"
    root3.sentido["font"] = ('Verdana','23','bold')
    root3.sentido.pack()

    root3.horario = Label(root3)
    root3.horario["text"] = "Horário: " + str(horario)
    root3.horario["bg"] = "white"
    root3.horario["font"] = ('Verdana','23','bold')
    root3.horario.pack()

    root3.butt_yes = Button(root3)
    root3.butt_yes["height"] = "3"
    root3.butt_yes["width"] = "6"
    root3.butt_yes["text"] = "SIM"
    root3.butt_yes["bg"] = "pale green"
    root3.butt_yes["activebackground"] = "white"
    root3.butt_yes["font"] = ('Verdana','23','bold')
    root3.butt_yes["command"] = lambda: [root3.destroy(),  inicializar_sistema_linha(codigo_linha)] # Ir pra tela de inicialização normal
    root3.butt_yes.pack(padx=(50, 10), side = LEFT)

    root3.butt_no = Button(root3)
    root3.butt_no["height"] = "3"
    root3.butt_no["width"] = "6"
    root3.butt_no["text"] = "NÃO"
    root3.butt_no["bg"] = "tomato3"
    root3.butt_no["activebackground"] = "white"
    root3.butt_no["font"] = ('Verdana','23','bold')
    root3.butt_no["command"] = lambda: [root3.destroy(), root3.quit(), tela_input_linha()]
    root3.butt_no.pack(padx=(10, 50), side = RIGHT)
    root3.mainloop()
    return

### Inicialização Sistema
def inicializar_sistema_linha(codigo_linha):
    # Carrega tela de aguarde
    funcoes_telas.inicia_tela_aguarde()

    '''
    tipo 0 -> normal
    tipo 1 -> linha
    tipo 2 -> especial (caixa tem)
    tipo 3 -> offline
    '''
    tipo = 1
    status = 3
    inicio_sync = datetime.datetime.now()
    
    r = sincronismo.iniciar_viagem(tipo, id_web_motorista, status, codigo_linha)
    fim_sync = datetime.datetime.now()
    tempo_requisicao = fim_sync - inicio_sync
    funcoes_logs.insere_log("Tempo Requisição INICIAR VIAGEM: " + str(tempo_requisicao), local)
    ### tirar essa parte e colocar em 'iniciar_viagem'
    if not r:
        return False
    else:
        funcoes_logs.insere_log("Inicializando Operacao (inicializar_sistema.sh)", local, 2)
        os.system("sudo sh " + path_atual + "/inicializar_sistema.sh")

def redireciona_set_val(param):
    os.system("sudo python3 " + path_atual + "/../tela/set_val.py " + param)

def config_rec_facial():
    funcoes_tela_corrente.registraTelaAtual("TELA_CONFIG_REC_FACIAL")
    root1 = Tk()
    root1.update()
    root1.deiconify()
    root1.configure(background="white")
    root1.attributes("-fullscreen", True)

    fonte_botoes = ('Arial', '90', 'bold')

    root1.btn1 = Button(root1)
    root1.btn1["text"] = "Dist min. sonar"
    root1.btn1["width"] = "14"
    root1.btn1["height"] = "2"
    root1.btn1["font"] = ('Arial', '18')
    root1.btn1['command'] = lambda: [redireciona_set_val('min_dist_sonar')]
    root1.btn1.pack(pady=12)

    root1.btn2 = Button(root1)
    root1.btn2["text"] = "Dist max. sonar"
    root1.btn2["width"] = "14"
    root1.btn2["height"] = "2"
    root1.btn2["font"] = ('Arial', '18')
    root1.btn2['command'] = lambda: [redireciona_set_val('max_dist_sonar')]
    root1.btn2.pack(pady=12)

    root1.btn3 = Button(root1)
    root1.btn3["text"] = "Altura min facial"
    root1.btn3["width"] = "14"
    root1.btn3["height"] = "2"
    root1.btn3["font"] = ('Arial', '18')
    root1.btn3['command'] = lambda: [redireciona_set_val('min_height_face')]
    root1.btn3.pack(pady=12)

    root1.btn4 = Button(root1)
    root1.btn4["text"] = "Largura min facial"
    root1.btn4["width"] = "14"
    root1.btn4["height"] = "2"
    root1.btn4["font"] = ('Arial', '18')
    root1.btn4['command'] = lambda: [redireciona_set_val('min_width_face')]
    root1.btn4.pack(pady=12)

    root1.btnv = Button(root1)
    root1.btnv["text"] = "Voltar"
    root1.btnv["width"] = "14"
    root1.btnv["height"] = "2"
    root1.btnv["font"] = ('Arial', '18')
    root1.btnv['command'] = lambda: [root1.destroy()]
    root1.btnv.pack(pady=12)

    root1.mainloop()

### Função Manutenção
def fiscal_manutencao():
    funcoes_tela_corrente.registraTelaAtual("TELA_MANUTENCAO")
    print("inicio fiscal_manutencao")
    root = Tk()
    root.update()
    root.deiconify()
    root.configure(background = "white")
    root.attributes("-fullscreen", True)

    root.label = Label(root)
    root.label["text"] = "MANUTENCAO"
    root.label["bg"] = "white"
    root.label["font"] = ("Arial", "22", "bold")
    root.label["justify"] = CENTER
    root.label.pack(pady=(30, 12))

    if getNotIntegrated() == 0: 
        root.zerar = Button(root)
        root.zerar["text"] = "Zerar"
        root.zerar["width"] = "14"
        root.zerar["height"] = "2"
        root.zerar["font"] = ('Arial', '16')
        root.zerar["command"] = lambda: [zerar()]
        root.zerar.pack(pady=12)

    root.configsonar = Button(root)
    root.configsonar["text"] = "Config rec facial"
    root.configsonar["width"] = "14"
    root.configsonar["height"] = "2"
    root.configsonar["font"] = ('Arial', '16')
    root.configsonar['command'] = lambda: [config_rec_facial()]
    root.configsonar.pack(pady=12)

    root.teste = Button(root)
    root.teste["text"] = "Teste hardware"
    root.teste["width"] = "14"
    root.teste["height"] = "2"
    root.teste["font"] = ('Arial', '16')
    root.teste["command"] = lambda: [sw_teste()]
    root.teste.pack(pady=12)

    root.botaoping = Button(root)
    root.botaoping["text"] = "Ping"
    root.botaoping["height"] = "2"
    root.botaoping["width"] ="14"
    root.botaoping["font"] = ('Arial', '16')
    root.botaoping["command"] = lambda: [efetua_ping()]
    root.botaoping.pack(pady=12)

    root.labelserial = Label(root)
    root.labelserial["text"] = "Serial: " +  getSerial()
    root.labelserial["bg"] = "white"
    root.labelserial["font"] = ("Arial", 14, "bold")
    root.labelserial["justify"] = CENTER
    root.labelserial.pack(pady=12)   

    root.labelpendentes = Label(root)
    root.labelpendentes["text"] ="Pendentes integr: " + str(getNotIntegrated())
    root.labelpendentes["font"] = ("Arial", 14, "bold")
    root.labelpendentes["justify"] = CENTER
    root.labelpendentes.pack(pady=12)

    root.voltar = Button(root)
    root.voltar["text"] = "Reboot"
    root.voltar["width"] = "14"
    root.voltar["height"] = "2"
    root.voltar["font"] = ('Arial', '16')
    root.voltar["command"] = lambda: [reboot()]
    root.voltar.pack(pady=(12))  # 325

    root.atualizar = Button(root)
    root.atualizar["text"] = "Atualizar"
    root.atualizar["width"] = "14"
    root.atualizar["height"] = "2"
    root.atualizar["font"] = ('Arial', '16')
    root.atualizar["command"] = lambda: [atualizar()]
    root.atualizar.pack(pady=(12))  # 325

    root.voltar = Button(root)
    root.voltar["text"] = "Sair"
    root.voltar["width"] = "14"
    root.voltar["height"] = "2"
    root.voltar["font"] = ('Arial', '18')
    root.voltar["command"] = lambda: [root.destroy(), root.quit()]
    root.voltar.pack(pady=(12)) #325

    root.ctr = 0
    root.mainloop()

def atualizar():
    funcoes_tela_corrente.registraTelaAtual("TELA_ATUALIZACAO_VERSAO")
    ret = funcoes_atualiza.checa_permite_update("VERSAO")
    titulo = "Info Atualizador"

    try:
        if ret[0] == False:
            tkinter.messagebox.showinfo(titulo, "Ação negada:\n\n" + str(ret[1]))
        else:
            # Chama tela de aguarde
            funcoes_telas.TelaAguardeAtualiza()
            
            # Chama rotina de execucao da atualizacao
            funcoes_atualiza.executa_atualiza(str(ret[2]))

            # Forca o reboot, caso o script anterior nao tenha feito isso
            os.system("sudo reboot -f")
    except Exception as e:
        tkinter.messagebox.showinfo(titulo, "Atualizacao não permitida: " + str(e))

    return

def reboot():
    os.system("sudo reboot -f")

def efetua_ping():
    funcoes_tela_corrente.registraTelaAtual("TELA_PING")
    output = sp.getoutput('ping -c 5 www.google.com')
    tkinter.messagebox.showinfo("Ping", output)

def sw_teste():
    os.system('sudo sh /home/pi/caixa-magica/teste_hw/start.sh')
    return

def reiniciar():
    os.system('sudo sh /home/pi/caixa-magica/reboot.sh')

def zerar():
    os.system('sudo sh /home/pi/caixa-magica/botar_em_prod.sh')

### Funções Diversas
def operacao_on():
    return sincronismo.operacao_on()

def key_valor(root, valor):
    insert_text(root, valor)

def key_1(root):
    insert_text(root,'1')  
    
def key_2(root):
    insert_text(root,'2')
    
def key_3(root):
    insert_text(root,'3')

def key_4(root):
    insert_text(root,'4')

def key_5(root):
    insert_text(root,'5')

def key_6(root):
    insert_text(root,'6')

def key_7(root):
    insert_text(root,'7')

def key_8(root):
    insert_text(root,'8')

def key_9(root):
    insert_text(root,'9')

def key_0(root):
    insert_text(root,'0')

#espaco
def def_espaco(root):
    root.insert_text(root,' ')

#apagar
def def_backspace(root):
    if root.focus_get()==root.txt_veiculo:
        pos_fin = len(root.txt_veiculo.get()) -1
        root.txt_veiculo.delete(int(pos_fin))

def insert_text(root, value):
    if root.focus_get()==root.txt_veiculo:
        root.txt_veiculo.insert(END, value.upper())
while True:
    while True:
        string_erro = ""

        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.bind((HOST,PORT))
                s.listen(1)
                conn ,addr = s.accept()
                with conn:
                    while True:
                        CNT_TENTATIVAS_TELA = 0
                        try:
                            pkg = conn.recv(512)
                            if pkg:
                                data = json.loads(pkg.decode('utf-8'))
                                if data['tela'] == 1:
                                    funcoes_telas.inicia_tela_aguarde()

                                    global nome_motorista
                                    global id_qrcode_motorista
                                    global id_web_motorista
                                    nome_motorista = data["nome_motorista"]
                                    id_qrcode_motorista = data["id_qrcode_motorista"]
                                    id_web_motorista = data["id_web_motorista"]
                                    core_init(nome_motorista, id_qrcode_motorista, id_web_motorista)
                                elif data['tela'] == 2:
                                    fiscal_manutencao()
                            else:
                                break 
                            conn.sendall(pkg)

                        except Exception as e:
                            exception_identificada = True
                            funcoes_logs.insere_log("Erro rcv - " + str(e), local, 3)
                            string_erro = str(e)
        except Exception as e:
            funcoes_logs.insere_log("Erro video: " + str(e), local, 4)
            string_erro = str(e)
