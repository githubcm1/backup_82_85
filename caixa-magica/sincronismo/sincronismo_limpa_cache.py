from time import sleep
import os

TEMPO = 60 * 60 * 4

while 1:
    print("Rodando drop cache")
    os.system("sudo bash /home/pi/caixa-magica/drop_caches.sh")
    print("Drop cache executado")
    sleep(TEMPO)

