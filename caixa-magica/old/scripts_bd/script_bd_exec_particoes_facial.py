import sys
import pathlib
path_atual = str(pathlib.Path(__file__).parent.absolute())

import script_bd_cria_particoes_facial

# Executa chamada criacao particoes
script_bd_cria_particoes_facial.cria_facial()

