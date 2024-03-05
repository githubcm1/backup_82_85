import pathlib
import time
from datetime import datetime
import os

INTERVALO = 5
pathfile = "/home/pi/caixa-magica/video_alive.txt"
DIFF_LIMITE = 45

time.sleep(10)

while 1:
    path = pathlib.Path(pathfile)
    last_modified = path.stat().st_mtime
    now = time.time()
    diff = now - last_modified

    if diff > DIFF_LIMITE:
        os.system("sudo sh /home/pi/caixa-magica/start.sh &")

    time.sleep(INTERVALO)
