import db
import json

# Abre arquivo de configuracao do sistema, para obter o valor limite de passagens dentro da mesma viagem
GLOBAL_LIMITE_PASSAGENS_OFFLINE = 99999

with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    try:
        GLOBAL_LIMITE_PASSAGENS_OFFLINE = config['num_limite_passagens_offline']
    except:
        print("")

def checkLimitePassagensOffViagem(p_contaid):
    global GLOBAL_LIMITE_PASSAGENS_OFFLINE

    try:
        with open("/home/pi/caixa-magica-operacao/viagem.json") as json_data:
            viagem = json.load(json_data)
            p_registroviagemid = viagem['id']
    except:
        p_registroviagemid = -9999


    if p_registroviagemid == -9999:
        return False

    conn = db.Conexao()
    sql = """select count(*) total 
from cobrancas c
where 1=1
  and c.status_internet ='OFFLINE'
  and exists
  	(
  	  select 1
  	  from saldo s 
  	  where s.id_web = c.saldo 
  	    and s.conta =""" + str(p_contaid) + """
  	)
 and c.viagemid ='""" + str(p_registroviagemid) + """'"""
    retorno = conn.consultar(sql)

    for row in retorno:
        num_registros = row[0]

        if num_registros >= GLOBAL_LIMITE_PASSAGENS_OFFLINE:
            return True

    return False
