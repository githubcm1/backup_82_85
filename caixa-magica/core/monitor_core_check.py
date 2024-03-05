import os
import time
from datetime import datetime
import sys

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_core

while 1:
    funcoes_core.zera_status_core()
    print("Iniciando core " + str(datetime.utcnow()))
    time.sleep(1)
    os.system("sudo taskset -c 3,1,2 python3 /home/pi/caixa-magica/core/core.py")
