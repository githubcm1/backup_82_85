import sys
import json
import os
sys.path.insert(1,'/home/pi/caixa-magica/core')
import funcoes_atualiza
import endpoints
import subprocess



folder = "/home/pi/releases/"
json_token = '/home/pi/caixa-magica-updates/token_update.json'

try:
    param = sys.argv[1]
except:
    quit()

ret = funcoes_atualiza.checa_permite_update(param)
if ret[0] == True:
    funcoes_atualiza.executa_atualiza(ret[2])
else:
    print(ret[1])
