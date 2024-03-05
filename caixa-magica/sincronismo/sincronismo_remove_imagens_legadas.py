import os
import time
from datetime import datetime
import sys

path_atual = "/home/pi/caixa-magica/sincronismo"
sys.path.insert(1, path_atual + "/../core/")
import funcoes_logs
import funcoes_temperatura

local = 'sincronismo_remove_imagens_legadas.py'

DIR_IMG = "/home/pi/caixa-magica-img/"

arr = os.listdir(DIR_IMG)

while True:
    funcoes_temperatura.holdProcessTemperature(local)

    try:
        dataatual = (datetime.utcnow().strftime("%Y%m%d"))
        horaatual = int((datetime.utcnow().strftime("%H")))

        if horaatual >= 5 and horaatual <= 8:
            for x in arr:
                statement = ""
                path_file = DIR_IMG + x
                timestamp_file = os.path.getctime(path_file)
                ts = int(timestamp_file)

                # if you encounter a "year is out of range" error the timestamp
                # may be in milliseconds, try `ts /= 1000` in that case
                dataarquivo = (datetime.utcfromtimestamp(ts).strftime('%Y%m%d'))

                # Se o arquivo foi gerado no dia anterior
                if int(dataarquivo) < int(dataatual):
                    statement = "sudo rm -f " + path_file
                    os.system(statement)
                    print(statement)
        else:
            print("Fora do intervalo de execução.")
    except:
        time.sleep(60)

    # Executa a cada 1h
    time.sleep(600)
