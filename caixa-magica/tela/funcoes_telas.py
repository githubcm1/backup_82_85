# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "pathlib" (conjunto de classes que representam os paths do filesystem).
# import pathlib

# Define o path deste script Python.
path_atual = "/home/pi/caixa-magica/tela"

# Insere nos paths do sistema o path deste script Python.
sys.path.insert(1, str(path_atual))

# Executa o script Python que mantem a aplicacao ativa atualizando a tabela "keep_alive" do banco de dados
# PostgreSQL local com a data e hora atuais.
# O caractere "&" no final do comando indica que a execucao dos proximos comandos nao aguardara este comando 
# finalizar sua execucao (execucao assincrona).
# Caminho do script: /home/pi/caixa-magica/keep_alive.py
os.system("sudo python3 " + path_atual + "/../keep_alive.py &")

# Da biblioteca do PyPI "PIL - Python Imaging Library" (manipulacao de imagens), importa apenas as classes Image e ImageTk
# Classe Image: classe principal da biblioteca, permite ler, editar e gravar arquivos de imagem.
# Classe ImageTk: permite criar e alterar objetos do Tkinter (interface grafica do Python).
from PIL import Image, ImageTk

# Importa a biblioteca padrao do Python "tkinter" (interface grafica do Python). Atribui o alias "tk" a biblioteca
# para facilitar a referencia a ela nas instrucoes abaixo.
import tkinter as tk

# Importa a biblioteca padrao do Python "threading" (manipulacao de threads para execucao de multiplas tarefas em paralelo).
import threading

# from tkinter import *
# from tkinter import ttk

# Do diretorio local "tela" importa o arquivo "AnimatedGIF.py".
# Caminho do arquivo: /home/pi/caixa-magica/tela/AnimatedGIF.py
# from AnimatedGIF import *
from AnimatedGIF import AnimatedGif

# Insere nos paths do sistema o path do diretorio "core" local.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(2, path_atual + '/../core/')

# Do diretorio local "core" importa o arquivo "funcoes_viagem.py".
# Caminho do arquivo: /home/pi/caixa-magica/core/funcoes_viagem.py
import funcoes_viagem

class ImageLabel(tk.Label):
    """a label that displays images, and plays them if they are gifs"""
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
            # im = im.resize((430, 100), Image.ANTIALIAS)
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

class TelaPropaganda(threading.Thread):
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
        
        imagem = tk.PhotoImage(file=path_atual + "/Camada22.png")
        tk.Label(self.root, image=imagem, bg='white').pack()

        #### GIF aguarde
        #anim = AnimatedGif(self.root,path_atual + '/Spinner-1s-200px.gif', 0.02)
        #anim.pack()
        #anim.start()

        self.root.after(20000, lambda:[self.root.quit(), self.root.destroy()])
        self.root.mainloop()

# Classe que define o layout da tela de "aguarde".
# A classe Thread passada como parametro representa a atividade que sera executada na thread a ser criada.
class TelaAguarde(threading.Thread):
    
    # Metodo construtor da classe, chamado pelo metodo "__start__" quando a classe e instanciada.
    # (metodos com "__" no inicio e fim do nome sao os metodos especiais da classe e sao chamados automaticamente quando necessarios,
    # nao podendo ser chamados explicitamente pelo usuario).
    # O parametro "self" e uma referencia a instancia da classe (objeto), a qual permite acessar as variaveis da classe.
    # O nome do parametro nao precisa ser "self", mas e sempre o primeiro parametro dos metodos da classe.
    def __init__(self):
        # Chama o metodo construtor da classe Thread. Automaticamente, executa o metodo "run()" da classe.
        threading.Thread.__init__(self)

        # Inicializa o thread criado.
        self.start()

    def destroy(self):
        self.root.destroy()

    def hide(self):
        self.root.withdraw()

    def show(self):
        self.root.update()
        self.root.deiconify()

    # Metodo que executa as instrucoes principais da classe.
    def run(self):
        # Cria uma variavel "root" em nivel de classe e atribui a ela um "Tk widget" (janela principal da aplicacao).
        self.root = tk.Tk()

        # Define o fundo da janela principal com cor branca.
        self.root.configure(background = 'white')

        # Abre a janela principal da aplicacao em fullscreen.
        self.root.attributes("-fullscreen",True)

        # Define uma label (caixa de texto) apenas com quebras de linha para deixar um espaco em branco no topo
        # da janela.
        espaco = tk.Label(self.root, text = '\n\n\n\n',fg='black',bg='white',font=('Verdana','25','bold'))

        # Define a cor de fundo da label como branca.
        espaco.config(bg = 'white')

        # Insere a label na janela principal da aplicacao.
        espaco.pack()

        # Cria uma referencia chamada "imagem" para o logo da Buspay.
        imagem = tk.PhotoImage(file=path_atual + "/Camada22.png")

        # Define uma label com o logo da Buspay e insere na janela principal da aplicacao.
        tk.Label(self.root, image=imagem, bg='white').pack()

        # Define uma label com o GIF animado "spinner". O parametro "0.02" informado e o delay considerado para troca
        # de frames da imagem GIF.
        anim = AnimatedGif(self.root,path_atual + '/Spinner-1s-200px.gif', 0.02)

        # Insere a label com o GIF animado na janela principal da aplicacao
        anim.pack()

        # Inicializa a animacao do GIF.
        anim.start()

        # Apos 20000 milissegundos (20seg), encerra e destroi todos os widgets presentes na janela principal da aplicacao.
        self.root.after(20000, lambda:[self.root.quit(), self.root.destroy()])

        # Trava a execucao da janela principal da aplicacao, nao permitindo a execucao de instrucoes posteriores ate o fechamento
        # desta janela.
        self.root.mainloop()

# tela de aguarde da atualizacao
class TelaAguardeAtualiza(threading.Thread):
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

        espaco = tk.Label(self.root, text = '\n\n\n\n\n\nAtualizando\n\n\nAguarde...',fg='black',bg='white',font=('Verdana','25','bold'))
        espaco.config(bg = 'white')
        espaco.pack()

        self.root.mainloop()

def tela_alerta(mensagem, miliseconds, bground):
    global root1
    root1 = tk.Tk()
    style = ttk.Style(root1)
    root1.update()
    root1.deiconify()
    #root1.configure(background = "red")
    root1.configure(background= bground)
    root1.attributes("-fullscreen",True)
    #verif2 = Label(root1, text="\n\n\n\n\n\nDriver QR Code\nnão iniciado.\n\nReiniciando aplicacao.", fg="white", bg="red",font=('verdana','25','bold'))
    verif2 = tk.Label(root1, text=mensagem, fg="white", bg=bground, font=('verdana','25','bold'))
    verif2.pack(side='top') #,fill=X)
    root1.after(miliseconds, lambda:[root1.quit(), root1.destroy()]) #3000
    root1.mainloop()
    return


def tela_confirma_encerramento_viagem():
   root2 = tk.Tk()
   style = ttk.Style(root2)
   root2.update()
   root2.deiconify()
   root2.configure(background = "white")
   root2.attributes("-fullscreen",True)
   fonte = ('Courier','32','bold')
   width_botao = 22

   fonte2 = ("Arial 26 bold")
   root2.verif2 = Message(root2, text = "\nInforme a ação a realizar nesta viagem:\n", font=fonte2, bg='white')
   root2.verif2['width'] = '420'
   root2.verif2['justify'] = CENTER
   root2.verif2.pack(side = 'top')
   root2.l0 = Label(root2)
   root2.l0['text'] = ''
   root2.l0.configure(bg='white', activebackground='white')
   root2.l0.pack(side='top', padx=30)

   root2.butt_1 = Button(root2)#, command = lambda:[root2.destroy(), root2.quit(), json_sentido_linha('IDA'),inicia_viagem(tipo, id_web_motorista, status)])
   root2.butt_1['text'] = 'ENCERRAR'
   root2.butt_1['font'] = fonte
   root2.butt_1['height'] = '2'
   root2.butt_1['width'] = width_botao
   root2.butt_1.configure(bg='white', activebackground='white')
   root2.butt_1.pack(side='top', padx = 20)
   root2.l1 = Label(root2)
   root2.l1['text'] = ''
   root2.l1.configure(bg='white', activebackground='white')
   root2.l1.pack(side='top', padx=30)

   root2.butt_2 = Button(root2, command = lambda:[funcoes_viagem.json_sentido_linha('IDA'), root2.destroy(), root2.quit()])
   root2.butt_2['text'] = 'SENTIDO IDA'
   root2.butt_2['font'] = fonte
   root2.butt_2['height'] = '2'
   root2.butt_2['width'] = width_botao
   root2.butt_2.configure(bg='white', activebackground='white')
   root2.butt_2.pack(side='top', padx = 20)
   root2.l2 = Label(root2)
   root2.l2['text'] = ''
   root2.l2.configure(bg='white', activebackground='white')
   root2.l2.pack(side='top', padx=20)

   root2.butt_3 = Button(root2, command = lambda:[funcoes_viagem.json_sentido_linha('VOLTA'), root2.destroy(), root2.quit()])
   root2.butt_3['text'] = 'SENTIDO VOLTA'
   root2.butt_3['font'] = fonte
   root2.butt_3['height'] = '2'
   root2.butt_3['width'] = width_botao
   root2.butt_3.configure(bg='white', activebackground='white')
   root2.butt_3.pack(side='top', padx = 20)
   root2.l3 = Label(root2)
   root2.l3['text'] = ''
   root2.l3.configure(bg='white', activebackground='white')
   root2.l3.pack(side='top', padx=20)

   root2.butt_4 = Button(root2, command = lambda:[root2.destroy(), root2.quit()])
   root2.butt_4['text'] = 'VOLTAR'
   root2.butt_4['font'] = fonte
   root2.butt_4['height'] = '2'
   root2.butt_4['width'] = width_botao
   root2.butt_4.configure(bg='white', activebackground='white')
   root2.butt_4.pack(side='top', padx = 20)
   root2.l3 = Label(root2)
   root2.l3['text'] = ''
   root2.l3.configure(bg='white', activebackground='white')
   root2.l3.pack(side='top', padx=20)

   root2.mainloop()
   return

class TelaAguardeInstala(threading.Thread):
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

        espaco = tk.Label(self.root, text = '\n\n\n\n\n\n',fg='black',bg='white',font=('Verdana','25','bold'))
        espaco.config(bg = 'white')
        espaco.pack()

        #### Logo BUSPAY
        #print(path_atual)
        imagem = tk.PhotoImage(file=path_atual + "/Camada22.png")
        tk.Label(self.root, image=imagem, bg='white').pack()

        anim = AnimatedGif(self.root,path_atual + '/Spinner-1s-200px.gif', 0.02)
        anim.pack()
        anim.start()

        espaco = tk.Label(self.root, text='\n\n\nAtualizando, aguarde...',fg='black',bg='black',font=('Verdana','25','bold'))
        espaco.config(bg = 'white')
        espaco.pack()

        #self.root.after(20000, lambda:[self.root.quit(), self.root.destroy()])
        self.root.mainloop()

# Mata o processo de tela aguarde
def kill_tela_aguarde():
    os.system("sudo pkill -9 -f tela_aguarde.py")

# Reinicia tela de aguarde
def inicia_tela_aguarde():
    kill_tela_aguarde()
    os.system("sudo python3 " + path_atual + "/../tela_aguarde.py &")

