import sync
import syncGPS
import time
import threading
import sys

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_logs
import funcoes_temperatura

local = 'sincronismo_gps.py'

def geolocalizacao():
    while True:
        funcoes_temperatura.holdProcessTemperature(local)
        try:
            enviar = syncGPS.enviar_localizacao()
        except Exception as e:
            print("Erro no sincronismo, no envio da localizacao. Esperando 30 segundos", e)

        time.sleep(5)

a = threading.Thread(target=geolocalizacao)
a.start()
