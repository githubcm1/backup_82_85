path = "/home/pi/caixa-magica/tela"

import sys
sys.path.insert(1, path)
import sonar

sys.path.insert(2, path + "/../central_serial")
import vars_serial

while 1:
    distancia = sonar.distance()
    print(distancia)

    if distancia < 60:
        vars_serial.grava_mensagem("CA010EZ")
    else:
        vars_serial.grava_mensagem("CA000EZ")
