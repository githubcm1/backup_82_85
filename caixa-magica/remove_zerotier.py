import os
import sys

file_rede ="/home/pi/caixa-magica-operacao/rede_zerotier.txt"

try:
    with open(file_rede) as fil:
        lines = fil.readlines()
        lines = [line.strip() for line in lines]
        
        for line in lines:
            comando = "sudo zerotier-cli leave " + str(line)
            os.system(comando)
except Exception as e:
    print(str(e))


