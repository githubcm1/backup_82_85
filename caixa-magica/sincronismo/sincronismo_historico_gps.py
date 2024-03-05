import sys
sys.path.insert(1,'/home/pi/caixa-magica/sincronismo')
import syncGPS
sys.path.insert(2,'/home/pi/caixa-magica/core')
import funcoes_geo_hist

import time

while True:
    try:
        funcoes_geo_hist.calculaDistanciaHistoricoGeoloc()
    except:
        pass
    time.sleep(10)

