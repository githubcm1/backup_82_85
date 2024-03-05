path = "/home/pi/caixa-magica/sincronismo"
import sync
from time import sleep
import json

TEMPO = 60

try:
    with open(path + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        TEMPO = aux['intervalo_update_facial_linhas']
except:
    pass

while 1:
    sleep(TEMPO)
    try:
        sync.processa_update_facial_favoritos()
    except Exception as e:
        print(str(e))
