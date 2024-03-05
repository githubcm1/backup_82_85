import json

path_atual = "/home/pi/caixa-magica/"
path_botoes = path_atual + "/../caixa-magica-operacao/vars_serial.json"

def distance():
    distancia = 0
    try:
        # Abre o arquivo com os sinais dos botoes
        with open(path_botoes) as json_data:
            aux = json.load(json_data)
            distancia= aux['sonar']
    except:
        distancia = 0

    return distancia

