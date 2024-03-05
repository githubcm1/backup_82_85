import sys
from time import sleep

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

import funcoes_elastic

INTERVALO_ATUALIZACAO = 60

while 1:
    try:
        funcoes_elastic.define_lista_indices()
    except:
        pass

    sleep(INTERVALO_ATUALIZACAO)
