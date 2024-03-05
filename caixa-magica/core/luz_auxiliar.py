import os
import time
import sys
import json

path_atual = "/home/pi/caixa-magica/core/"
sys.path.insert(1, path_atual)
import funcoes_placa_serial

path_atual = "/home/pi/caixa-magica/tela/"
sys.path.insert(2, path_atual)
#import sonar

with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    try:
        GLOBAL_MIN_LUMINOSIDADE = config['min_luminosidade_sensor']
    except:
        GLOBAL_MIN_LUMINOSIDADE = 100

while 1:
    time.sleep(0.1)
    liga_luz = False
    try:
        # Abre o arquivo de variaveis
        vars_retorno = funcoes_placa_serial.obtem_variaveis_retorno()
    
        # Em caso de baixa luminosidade
        if vars_retorno['luz_ambiente'] <= GLOBAL_MIN_LUMINOSIDADE:
            # Pegamos o valor do sonar
            #dist = sonar.distance()

            # Se esta proximo do sonar
            #if dist < config['rec_facial']['max_dist_sonar'] and dist > config['rec_facial']['min_dist_sonar']:
            if 1==1:
                liga_luz = True
    except Exception as e:
        liga_luz = False

    if liga_luz:
        funcoes_placa_serial.liga_luz()
        time.sleep(5)
    else:
        funcoes_placa_serial.desliga_luz()
