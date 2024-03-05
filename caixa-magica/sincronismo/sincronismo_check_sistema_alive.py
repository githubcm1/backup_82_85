from datetime import datetime
from time import sleep

path_file = '/home/pi/caixa-magica/alive.txt'

sleep_seconds = 10

while True:
    try:
        atual = str(datetime.now())

        with open(path_file, 'w') as f:
            f.write(atual)
        sleep(sleep_seconds)
    except:
        sleep(sleep_seconds)

