import sys
import os
from time import sleep

import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

def restart_cm():
    os.system("sudo sh " + path_atual + "/../restart.sh")
