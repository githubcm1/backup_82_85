import json
import smtplib, ssl 
import funcoes_serial

def getSerial():
   return funcoes_serial.getSerial()

def getVeiculoID():
    try:
        with open('/home/pi/caixa-magica-operacao/instalacao.json') as dados_json:
            data_init = json.load(dados_json)
            veiculo = data_init['veiculo']
        return veiculo
    except Exception as e:
        print("Erro para ler arquivo instalacao"+ str(e))
        return Null

def getAmbiente():
    try:
        with open('/home/pi/caixa-magica-operacao/sincronismo.json') as dados_json:
            data_init = json.load(dados_json)
            caminho = data_init['url']
        start = caminho.find('operacao.')
        stop = caminho.find('.buspay')
        ambiente = caminho[start+9:stop]
        return ambiente.upper()
    except Exception as e:
        print("Erro para ler arquivo sincronismo"+ str(e))
        return Null

def notificar_por_email(tela):
    #Vindo da tela inicialização
    if tela == 1:  
        msg_log = 'Reboot na tela de Inicializacao'    

    #Vindo da tela Principal
    elif tela == 2:
        try:
            with open('/home/pi/caixa-magica-operacao/passagens_viagem.json') as json_passagens:
                giros = json.load(json_passagens)
                print(giros)
        except:
            giros = 'Nao houve giros (Nao foi possivel pegar passagens_viagem json)'
        msg_log = 'Reboot no TelaPrincipal \n' + str(giros)

    #Vindo de nenhum dos dois
    else: 
        print('erro')
        return
    
    mensagem = """\
Subject: """ + getAmbiente() + """ - Reboot de CM por FailOver - VeiculoId: """ + getVeiculoID() + """

""" + msg_log + "\n Serial:" + getSerial()

    port = 465  # Para padrão SSL
    smtp_server = "smtp.gmail.com"
    remetente = "cm.alertas@b2mlportal.com.br"
    password = 'C0n1ss1m0'
    destinatario = ['mateus.prado@b2ml.com.br','guilherme.luz@b2ml.com.br','filipe.soares@b2ml.com.br ','otavio@b2ml.com.br','pedro.bonafe@b2ml.com.br','rodrigo.santos@b2ml.com.br']
    # destinatario = ['mateus.prado@b2ml.com.br']
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context, timeout=5) as server: 
        server.login(remetente, password)
        server.sendmail(remetente, destinatario, mensagem)
        print('Email enviado')
    return
