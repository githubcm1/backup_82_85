import os
import sys
sys.path.insert(1,"/home/pi/caixa-magica/core")
import db

MANTER_ABERTA = False
conn = db.Conexao()

# Checa se tem viagem aberta
try:
    sql = "select distinct 1 from viagem where viagem_atual=true"
    result = conn.consultar(sql)

    for row in result:
        MANTER_ABERTA = True
except:
    pass

if MANTER_ABERTA:
    os.system("sudo touch /home/pi/caixa-magica-operacao/aberto.txt")
