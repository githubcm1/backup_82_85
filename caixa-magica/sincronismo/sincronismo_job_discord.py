import sys
import threading

sys.path.insert(1, '/home/pi/caixa-magica/discord')
import functions_discord

#t1 = threading.Thread(target=functions_discord.processa_fila_loop)
#t1.start()
functions_discord.processa_fila_loop()
