import os
from time import sleep
import json
from tkinter import *
from tkinter import ttk
import tkinter as tk

def alerta_fail_db():
    global root1
    root1 = Tk()
    style = ttk.Style(root1)
    root1.update()
    root1.deiconify()
    root1.configure(background="blue")
    root1.attributes("-fullscreen",True)
    verif = Label(root1, text="\n\n\n\nBD local indisponivel.\n\n\n\nReiniciando aplicação.\n\n\n\nContate o admin.",fg="white", bg="blue", font=('Verdana',24,'bold'))
    verif.pack(side='top',fill=X)
    root1.after(5000,lambda:[root1.quit(), root1.destroy()])
    root1.mainloop()
    return


while True:
    try:
        # obtem espaco em disco atual
        os.system("sudo rm -f /home/pi/caixa-magica/check_database_alive.txt")
        os.system("sudo touch /home/pi/caixa-magica/check_database_alive.txt")
        os.system("sudo ps -aux | grep /usr/local/pgsql/ | sudo tee -a /home/pi/caixa-magica/check_database_alive.txt > /dev/null")

        f = open("/home/pi/caixa-magica/check_database_alive.txt")
        aux = f.read() 
        pos_pct = aux.find("postgres")

        # Se encontrou, então o processo está rodando
        # caso contrário, está com falha e a aplicação precisa ser reiniciada
        if pos_pct < 0:
            alerta_fail_db()
            sleep(5)
            os.system("sudo reboot -f")

    except Exception as e:
        print("Efetuando nova leitura: ", e)
    sleep(120)

