from tkinter import *
import time


def cfgTelas(background,foreground,texto1, texto2):                            
    root = Tk()
    widget = Frame(root)
    root.configure(background = "red")
    root.attributes("-fullscreen",True)
    widget.pack()
    #msg = Label(widget, text= texto1 + '\n ' + texto2 ,fg=foreground,bg=background,font=('Verdana','36','bold'))
    localString = texto1
    
    if (len(texto2)>0):
        localString +=  '\n ' + texto2
        
    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana','34','bold'))
    
    msg.grid(row=0,column=1,ipady=350)
    root.after(20000, lambda: root.destroy())
    root.mainloop()
while True:
    cfgTelas("red","white","Saldo Insuficiente","")
   