import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
import threading

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


class TelaAguarde(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

    # def callback(self):
    #     threading.Thread(target=self.root.destroy).start()
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

        espaco = tk.Label(self.root, text = '\n\n\n\n',fg='black',bg='white',font=('Verdana','25','bold'))
        espaco.config(bg = 'white')
        espaco.pack()

        #### Logo BUSPAY
        imagem = ImageLabel(self.root)
        imagem.config(bg ='white')
        imagem.load('/home/pi/caixa-magica/tela/Camada22.png')
        imagem.pack()

        #### GIF aguarde
        anim = ImageLabel(self.root)
        anim.config(bg ='white')
        anim.pack()
        anim.load('/home/pi/caixa-magica/tela/Spinner-1s-200px.gif')
       
        self.root.mainloop()
