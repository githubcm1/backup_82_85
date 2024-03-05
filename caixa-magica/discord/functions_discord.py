import credencial_token_discord
import json
from datetime import datetime
import sys
import requests

sys.path.insert(1,'/home/pi/caixa-magica/core/')
import funcoes_serial
import db
import threading
import time

SERIAL = funcoes_serial.getSerial()

conn = db.Conexao()

# Rotina que enfileira as mensagens a serem enviadas no validador
def insere_notificacao_fila(mensagem, tipo):
    try:
        serial = SERIAL
        
        with open("/home/pi/caixa-magica-operacao/instalacao.json") as f:
            aux = json.load(f)
            veiculo = str(aux['numeroVeiculo'])
        f.close()

        mensagem = str(datetime.utcnow()) + " - Veiculo " + str(veiculo) + " - Serial " + str(serial) + ": " + str(mensagem)

        sql = "insert into discord_notificacoes (mensagem, tipo) values ('" + str(mensagem).strip() + "', '"+str(tipo).strip()+"')"
        conn.manipular(sql)
    except Exception as e:
        print(str(e))
        pass

# Envia notificacao via discord
def envia_notificacao(mensagem, tipo):
    retorno = []
    try:
        # Pega a configuracao do token
        with open('/home/pi/caixa-magica-discord-conf/credencial.json') as f:
            aux = json.load(f)
            auth_token = aux['authorization_token']

            if tipo == "eventos":
                canal = aux['canal_eventos']
            elif tipo == "erros":
                canal = aux['canal_erros']

        url = "https://discordapp.com/api/channels/"+str(canal)+"/messages"
        headers = {"Authorization": "{}".format(auth_token),
                   "User-Agent": "myBotThing (http://some.url, v0.1)",
                   "Content-Type": "application/json"}
        content = json.dumps({"content": mensagem})

        r = requests.post(url, headers=headers, data=content)

        if r.ok:
            retorno.append(True)
            retorno.append(r.text)
        else:
            retorno.append(False)
            retorno.append(r.text)
        return retorno
    except Exception as e:
        retorno = []
        retorno.append(False)
        retorno.append(str(e))
        return retorno

# Processa fila de envio das mensagens
def processa_fila():
    try:
        sql = "select id, mensagem, tipo from discord_notificacoes where enviada=false order by 1 limit 5"
        ret = conn.consultar(sql)
        
        for row in ret:
            retornoEnvio = envia_notificacao(row[1], row[2])
            print(retornoEnvio)
            
            if retornoEnvio[0] == True:
                sql = "update discord_notificacoes set enviada=true where id = " + str(row[0])
                conn.manipular(sql)
            else:
                sql = "update discord_notificacoes set retorno_enviada = " + str(row[1]) + " where id = " + str(row[0])
                conn.manipular(sql)
    except:
        pass

def processa_fila_loop():
    while 1:
        processa_fila()
        time.sleep(10)

#print(envia_notificacao('teste de mensagem', 'erros'))
