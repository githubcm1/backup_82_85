import time
from core import db
import os
import sys
from datetime import datetime

reinicia = False
conn =db.Conexao()

sql = """select distinct 1 from keep_alive
             where now() - tmst >= '00:01:00'
          """
result = conn.consultar(sql)
    
for row in result:
    print("Nao executando")
    reinicia = True

sql = """select count(*) from keep_alive"""
result = conn.consultar(sql)
for row in result:
    if row[0] == 0:
        print("Nao executando")
        reinicia = True

if reinicia:

    os.system("sudo pkill -9 -f start.sh")
    os.system("sudo sh /home/pi/caixa-magica/start.sh")
