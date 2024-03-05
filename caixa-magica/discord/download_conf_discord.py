import sys

sys.path.insert(1, '/home/pi/caixa-magica/core/')
import endpoints

import credencial_token_discord
import os
import time
import json

authorization_token = credencial_token_discord.credencial

ambiente = endpoints.getEnv()

if ambiente == "PROD":
    ambiente_prefix = "prod"
elif ambiente == "HOMOLOG":
    ambiente_prefix = "homol"
elif ambiente == "DEV":
    ambiente_prefix = "dev"

while 1:
    try:
        # Buscamos em qual empresa o validador foi instalado
        with open('/home/pi/caixa-magica-operacao/instalacao.json') as f:
            aux = json.load(f)
            operadora = aux['operadora']
        f.close()

        # Primeiro, baixamos o conteudo do discord
        comando = "sudo mkdir -p /home/pi/caixa-magica-discord-conf/"
        os.system(comando)

        comando = "sudo rm -rf /home/pi/caixa-magica-discord-conf-temp/"
        os.system(comando)

        comando = "sudo mkdir -p /home/pi/caixa-magica-discord-conf-temp/"
        os.system(comando)

        comando = "cd /home/pi/caixa-magica-discord-conf-temp/"
        os.system(comando)

        comando = "sudo git clone https://"+authorization_token+"@github.com/githubcm1/caixa-magica-discord.git /home/pi/caixa-magica-discord-conf-temp/"
        os.system(comando)

        # do diretorio em questao, garantimos que o 
        json_download = ambiente_prefix + "_credenciais_empresa_" + str(operadora) + ".json"

        if os.path.exists('/home/pi/caixa-magica-discord-conf-temp/'+json_download):
            comando = "sudo rm -rf /home/pi/caixa-magica-discord-conf/*"
            os.system(comando)

            comando = "sudo mv /home/pi/caixa-magica-discord-conf-temp/" + json_download + " /home/pi/caixa-magica-discord-conf/credencial.json"
            os.system(comando)

        comando = "sudo rm -rf /home/pi/caixa-magica-discord-conf-temp/"
        os.system(comando)
        
    except:
        pass
    time.sleep(60 * 60) # a cada 1h
