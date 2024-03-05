import os
import time
from datetime import datetime

while 1:
    print("Iniciando placa " + str(datetime.utcnow()))
    os.system("sudo python3 /home/pi/caixa-magica/core/central_placa_serial.py")
