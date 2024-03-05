""" AnimatedGIF - a class to show an animated gif without blocking the tkinter mainloop()
Copyright (c) 2016 Ole Jakob Skjelten <olesk@pvv.org>
Released under the terms of the MIT license (https://opensource.org/licenses/MIT) as described in LICENSE.md
"""
# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "time" (operacoes relacionadas a tempo e horarios).
import time

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
        # Importa a biblioteca padrao do Python "Tkinter" (interface grafica do Python). Atribui o alias "tk" a biblioteca
        # para facilitar a referencia a ela nas instrucoes abaixo.
        import Tkinter as tk  # for Python2
# Se houver erro na importacao da biblioteca "Tkinter" (se a versao do Python nao for a 2)...
except ImportError:
        # Importa a biblioteca padrao do Python "tkinter" (interface grafica do Python). Atribui o alias "tk" a biblioteca
        # para facilitar a referencia a ela nas instrucoes abaixo.
        import tkinter as tk  # for Python3

# Classe para manipulacao de imagens no formato GIF animado. Recebe como parametro uma referencia ao
# label do tkinter no qual a imagem sera inserida.
class AnimatedGif(tk.Label):
        """
        Class to show animated GIF file in a label
        Use start() method to begin animation, and set the stop flag to stop it
        """

        # Metodo construtor da classe, chamado pelo metodo "__start__" quando a classe e instanciada.
        # (metodos com "__" no inicio e fim do nome sao os metodos especiais da classe e sao chamados automaticamente quando necessarios,
        # nao podendo ser chamados explicitamente pelo usuario).
        # O parametro "self" e uma referencia a instancia da classe (objeto), a qual permite acessar as variaveis da classe.
        # O nome do parametro nao precisa ser "self", mas e sempre o primeiro parametro dos metodos da classe.
        def __init__(self, root, gif_file, delay=0.04):
                """
                :param root: tk.parent
                :param gif_file: filename (and path) of animated gif
                :param delay: delay between frames in the gif animation (float)
                """
		
                # Chama o metodo "__init__" do label passado como parametro.
                tk.Label.__init__(self, root)

                # Cria uma variavel "root" em nivel de classe e atribui o valor do parametro "root" recebido.
                self.root = root

                # Cria uma variavel "gif_file" em nivel de classe e atribui o valor do parametro "gif_file" recebido.
                self.gif_file = gif_file

                # Cria uma variavel "delay" em nivel de classe e atribui o valor do parametro "delay" recebido.
                self.delay = delay  # Animation delay - try low floats, like 0.04 (depends on the gif in question)

                # Cria uma variavel "stop" em nivel de classe e atribui a ela o valor "false" (indica que
                # a animacao da imagem nao sera pausada apos a execucao do loop).
                self.stop = False  # Thread exit request flag

                # Cria uma variavel "_num" em nivel de classe e a inicializa com valor zero.
                # Utilizada para controlar o looping pelos frames do GIF.
                # O "underline" no inicio do nome da variavel e uma convencao para indicar que a variavel deve ser
                # utilizada apenas internamente, ou seja, nao deve ser acessada ou modificada diretamente pelo usuario.
                self._num = 0

        # Metodo de inicializacao da classe (sem o uso de threads).
        def start(self):
                """ Starts non-threaded version that we need to manually update() """

                # Cria uma variavel "start_time" em nivel de classe e atribui a ela o numero de segundos desde o
                # inicio dos tempos (1970-01-01) ate a data/hora atuais.
                self.start_time = time.time()  # Starting timer

                # Chama o metodo interno "_animate".
                self._animate()

        def stop(self):
                """ This stops the after loop that runs the animation, if we are using the after() approach """
                self.stop = True

        # Metodo principal da classe, o qual executa a animacao da imagem em si.
        def _animate(self):
                # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
                try:
                        # Cria uma variavel "gif" em nivel de classe e atribui a ela um widget "PhotoImage" com o GIF a ser animado.
                        # O parametro "format" recebe valor de "_num" e o utiliza como indice do frame do GIF a ser exibido.
                        self.gif = tk.PhotoImage(file=self.gif_file, format='gif -index {}'.format(self._num))  # Looping through the frames

                        # Define a cor de fundo da imagem como branca.
                        self.configure(image=self.gif, bg='white')

                        #self.configure(bg='white')

                        # Soma um ao valor da variavel "_num".
                        self._num += 1
                # Se ocorrer algum erro nas instrucoes acima...
                except tk.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
                        # Atribui o valor zero a variavel "_num" (ou seja, retorna ao primeiro frame da imagem GIF).
                        self._num = 0
                # Se a variavel "stop" estiver setada com valor "false"...
                if not self.stop:    # If the stop flag is set, we don't repeat
                        # Apos o periodo de delay (valor padrao 0.04 * 1000 = 40 milissegundos), chama novamente o metodo "_animate"
                        # (ou seja, exibe o proximo frame da imagem GIF).
                        self.root.after(int(self.delay*1000), self._animate)

        def start_thread(self):
                """ This starts the thread that runs the animation, if we are using a threaded approach """
                from threading import Thread  # We only import the module if we need it
                self._animation_thread = Thread()
                self._animation_thread = Thread(target=self._animate_thread).start()  # Forks a thread for the animation

        def stop_thread(self):
                """ This stops the thread that runs the animation, if we are using a threaded approach """
                self.stop = True

        def _animate_thread(self):
                """ Updates animation, if it is running as a separate thread """
                while self.stop is False:  # Normally this would block mainloop(), but not here, as this runs in separate thread
                        try:
                                time.sleep(self.delay)
                                self.gif = tk.PhotoImage(file=self.gif_file, format='gif -index {}'.format(self._num))  # Looping through the frames
                                self.configure(image=self.gif)
                                self._num += 1
                        except tk.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
                                self._num = 0
                        except RuntimeError:
                                sys.exit()
