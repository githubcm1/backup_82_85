import json
import sys
import smtplib, ssl
from datetime import datetime

from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_serial
import db
import os
from time import sleep

SERIAL = funcoes_serial.getSerial()

try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        SMTP = aux['smtp_address']
        SENDER = aux['mail_alerts_from']
        TO = aux['mail_alerts_to']
        SMTP_PORT = aux['smtp_port']
        SENDER_PWD = aux['mail_alerts_from_pwd']
        ENVIA_NOTIF = aux['envia_notif']
except Exception as e:
    SMTP = ""
    SENDER = ""
    TO = ""
    SMTP_PORT = ""
    SENDER_PWD = ""
    ENVIA_NOTIF = False

try:
    with open(path_atual + "/../../caixa-magica-operacao/instalacao.json") as json_data:
        aux = json.load(json_data)
        OPERADORA = aux['operadora']
except:
    OPERADORA = "INDEFINIDA"

# Rotina para notificacao por email
def send_mail_notif(subject, mensagem, attachment_path):
    if ENVIA_NOTIF == False:
        return
    
    if SMTP == "" or SMTP == None:
        return False

    try:
        subject = "OPERADORA ID " + str(OPERADORA) + " - "+ subject + " - Serial ID " + str(SERIAL)
        now = datetime.utcnow()

        mensagem = "-- Acao efetuada em " + str(now) + "--" + "\n\n" + str(mensagem)
        mensagem = 'Subject: {}\n\n{}'.format(subject, mensagem)

        if attachment_path == None or attachment_path == "":
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP, SMTP_PORT, context=context, timeout=5) as server:
                server.login(SENDER, SENDER_PWD)
                server.sendmail(SENDER, TO, mensagem)
                return True
        # Mas se temos anexo, usamos Mimetype multipart
        else:
            msg = MIMEMultipart()
            msg['From'] = SENDER
            msg['To'] = TO
            msg['Subject'] = subject
            msg.attach(MIMEText(mensagem))

            with open(attachment_path, "rb") as arq:
                part = MIMEApplication(arq.read(), Name=basename(attachment_path))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment_path)
            msg.attach(part)
           
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP, SMTP_PORT, context=context, timeout=5) as server:
                server.login(SENDER, SENDER_PWD)
                server.sendmail(SENDER, TO, msg.as_string())
                return True

        return False
    except Exception as e:
        print(str(e))
        return False

# teste envio
#send_mail_notif("Teste subject", "teste mensagem", "/home/pi/caixa-magica-logs/20220507_logs.tar.gz" )
#quit()

# coloca o email de notificacao na fila
def insere_fila_notif(subject, message, attach = None, drop_attach = True):
    if ENVIA_NOTIF == False:
        return

    conn = db.Conexao()

    now = datetime.utcnow()

    if attach == None:
        attach = ""

    dados = (now, subject, message, attach, drop_attach, )
    sql = """insert into notif_email (dateinsert, subject, message, attachment_path, drop_attachment)
              values (%s, %s, %s, %s, %s)"""
    conn.manipularComBind(sql, dados)
    del conn

# Processa fila de envios
def processa_fila():
    if ENVIA_NOTIF == False:
        return

    conn_fila = db.Conexao()

    sql = "delete from notif_email where datemailsent is not null or dateinsert < now() - Interval '2 days'"
    conn_fila.manipular(sql)

    sql = """select id, subject, replace(message,'''', '') message, attachment_path, drop_attachment
             from notif_email
             where datemailsent is null
             order by 1 limit 100
          """
    result = conn_fila.consultar(sql)

    for row in result:
        try:
            msg = str(row[2])
            sent = send_mail_notif(row[1], msg, row[3])

            if sent:
                now = datetime.utcnow()
                sql = """update notif_email
                     set datemailsent=%s, smtp=%s, mail_from=%s, mail_to=%s, smtp_port=%s
                     where id = %s
                  """
                dados = (now, SMTP, SENDER, TO, SMTP_PORT, row[0], )
                conn_fila.manipularComBind(sql, dados)

                # se a opcao foi remover o anexo da maquina local
                if row[4] == True:
                    try:
                        os.system("sudo rm -f " + str(row[3]))
                    except Exception as e:
                        print(str(e))
                        pass

                sleep(0.2)
        except Exception as e:
            print(str(e))
            pass
    del conn_fila

