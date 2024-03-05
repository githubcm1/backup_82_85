from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from functools import partial
import sys
import os
import time
import json

import pathlib
path_atual = "/home/pi/caixa-magica"
sys.path.insert(1, path_atual)

sys.path.insert(1, path_atual + '/core/')
import funcoes_serial
import funcoes_logs

import tkinter as tk
from itertools import count
from PIL import Image, ImageTk

sys.path.insert(3, path_atual + '/tela/')
import funcoes_telas

local = 'set_val.py'

global PARAM
PARAM = ""
try:
    PARAM = sys.argv[1]
except:
    PARAM = None

if PARAM == "" or PARAM == None:
    quit()

global CONFIG
with open(path_atual + "/../caixa-magica-vars/config.json") as json_data:
    aux = json.load(json_data)
    CONFIG = aux

def iniciar_salvar(valor):
    global CONFIG

    CONFIG['rec_facial'][PARAM] = int(valor)

    with open(path_atual+"/../caixa-magica-vars/config.json", "w") as json_data:
        json.dump(CONFIG, json_data)
    return

def salvar_novos_valores(root):
    valor = root.txt_distancia.get()
    root.destroy()  
    # root.quit()
    if valor != '':
        iniciar_salvar(valor)
    else:
        tela_valor_invalida()
    return False

def tela_valor_invalida():
    root3 = Tk()
    root3.deiconify()
    root3.configure(background = "orange red")
    root3.attributes("-fullscreen", True)

    root3.aviso = Message(root3)
    root3.aviso["text"] = '\n\n\n\nVALOR INVÁLIDO\n\nTENTE NOVAMENTE!!!\n\n'
    root3.aviso["bg"] = "orange red"
    root3.aviso["font"] = ("Verdana", "26", "bold")
    root3.aviso["width"] = "420"
    root3.aviso["justify"] = CENTER
    root3.aviso.pack()

    root3.after(2000, lambda: [root3.destroy(), input_tela()])

    root3.mainloop()
    return False

def input_tela():
    global PARAM
    global CONFIG
    print("PARAM: " + str(PARAM))
    print(CONFIG['rec_facial'])

    try:
        valor_padrao = str(CONFIG['rec_facial'][PARAM])
    except Exception as e:
        valor_padrao = ""
        print(str(e))
    print("Valor: " + str(valor_padrao))

    root = Tk()
    root.focus_force()
    root.attributes('-fullscreen',True)
    style = ttk.Style(root)
    fonte = ("Arial 50 bold")
    fonte2 = ("Arial 20 bold")
    root.dados_onibus = StringVar()
    root.title('Valor (em cm):')
    root.frame_dados = Frame(root, borderwidth=10)
    root.frame_dados.pack(fill='x')
    
    root.lbl_distancia = Label(root.frame_dados, text="Valor (em cm): ", font=fonte2)
    root.lbl_distancia.pack(side='left')


    v = StringVar(root, value= valor_padrao)
    root.txt_distancia = Entry(root.frame_dados, textvariable=v)
    root.txt_distancia["font"] = fonte
    #root.txt_distancia.select_range(0, tk.END)
    root.txt_distancia.focus_set()
    root.txt_distancia.pack(side='left', fill='x', expand=True)

    fonte_botoes = ('Courier', '64', 'bold')

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
    root.frame_4 = Frame(root)
    root.frame_4.configure(bg='white')
    root.frame_4.pack(fill='both', expand=True)

    ###444
    root.butt_4 = Button(root.frame_4, command = lambda:key_4(root))
    root.butt_4['text'] = '4'
    root.butt_4['font'] = fonte_botoes
    root.butt_4.configure(bg='white',
                                    activebackground='white')
    root.butt_4.pack(side='left', fill='both', expand=True)

    ###555
    root.butt_5 = Button(root.frame_4, command = lambda:key_5(root))
    root.butt_5['text'] = '5'
    root.butt_5['font'] = fonte_botoes
    root.butt_5.configure(bg='white',
                                    activebackground='white')
    root.butt_5.pack(side='left', fill='both', expand=True)

    ###666
    root.butt_6 = Button(root.frame_4, command = lambda:key_6(root))
    root.butt_6['text'] = '6'
    root.butt_6['font'] = fonte_botoes
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
    root.butt_7.configure(bg='white',
                                    activebackground='white')
    root.butt_7.pack(side='left', fill='both', expand=True)

    ###888
    root.butt_8 = Button(root.frame_7, command = lambda:key_8(root))
    root.butt_8['text'] = '8'
    root.butt_8['font'] = fonte_botoes
    root.butt_8.configure(bg='white',
                                    activebackground='white')
    root.butt_8.pack(side='left', fill='both', expand=True)

    ###999
    root.butt_9 = Button(root.frame_7, command = lambda:key_9(root))
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
    #root.butt_backspace['width'] = '2'
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

    ###aceitar
    root.butt_confirmar = Button(root.frame_espaco)
    root.butt_confirmar['text'] = '✓'
    root.butt_confirmar['font'] = fonte_botoes
    root.butt_confirmar["command"] = lambda: salvar_novos_valores(root)
    root.butt_confirmar.configure(bg='white',
                                    activebackground='white')
    root.butt_confirmar.pack(side='left', fill='both', expand=True)

    #frame espaco
    root.frame_canc = Frame(root)
    root.frame_canc.configure(bg='white')
    root.frame_canc.pack(fill='both', expand=True)

    # ###cancelar
    root.butt_cancelar = Button(root.frame_canc)
    root.butt_cancelar['text'] = 'Cancelar'
    root.butt_cancelar['font'] = fonte_botoes
    root.butt_cancelar["command"] = lambda: root.destroy()
    root.butt_cancelar.configure(bg='white',activebackground='white')
    root.butt_cancelar.pack(side='left', fill='both', expand=True)

    root.mainloop()
    return

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
    if root.focus_get()==root.txt_distancia:
        pos_fin = len(root.txt_distancia.get()) -1
        root.txt_distancia.delete(int(pos_fin))

def insert_text(root, value):
    if root.focus_get() == root.txt_distancia:
        root.txt_distancia.insert(END, value.upper())

input_tela()


