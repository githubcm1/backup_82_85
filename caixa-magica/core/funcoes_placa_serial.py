import time
import serial
import os
import json

path = "/home/pi/caixa-magica-operacao/"
path_mensagem = path + "mensagem_serial.json"
path_json = path+ "vars_serial.json"

global MENSAGEM_PADRAO
MENSAGEM_PADRAO = "CA0001EZ"

# Reinicia a placa
def reinicia_placa():
    mensagem = "CAR001EZ"
    string_file = '{"mensagem": "' + str(mensagem) + '"}'

    with open(path_mensagem, "w") as f:
        f.write(string_file)


# Grava o arquivo de mensagem alterando o conteudo do pacote a ser enviado
def atualiza_mensagem_serial(mensagem):
    string_file = '{"mensagem": "' + str(mensagem) + '"}'
    
    with open(path_mensagem, "w") as f:
        f.write(string_file)

# Inicializa a mensagem (estado inicial)
def inicia_mensagem_placa():
    global MENSAGEM_PADRAO
    mensagem = MENSAGEM_PADRAO

    atualiza_mensagem_serial(mensagem)

# Le o valor corrente da mensagem
def obtem_mensagem_serial():
    global MENSAGEM_PADRAO
    try:
        with open(path_mensagem) as json_data:
            aux = json.load(json_data)
            return aux['mensagem']
    except:
        pass
    
    return MENSAGEM_PADRAO

# Efetuamos o procedimento de ativacao da luz auxiliar
def liga_luz():
    valor = 1
    muda_valor_posicao(valor,3)

# Efetuamos o procedimento de ligar a luz
def desliga_luz():
    valor = 0
    muda_valor_posicao(valor,3)

# Efetuamos o procedimento de ligar o buzzer
def liga_buzzer():
    valor = 1
    muda_valor_posicao(valor, 4)

# Efetuamos o procedimento de desligar o buzzer
def desliga_buzzer():
    valor = 0
    muda_valor_posicao(valor,4)

# Efetuamos o procedimento de ligar o modem
def liga_modem():
    valor = 1
    muda_valor_posicao(valor, 5)

# Efetuamos o procedimento de desligar o modem
def desliga_modem():
    valor = 0
    muda_valor_posicao(valor,5)

# Efetuamos o procedimento de liberacao da catraca
def libera_catraca():
    valor = 1
    muda_valor_posicao(valor,2)

# Efetuamos o procedimento de ligar a luz
def trava_catraca():
    while 1:
        valor = 0
        muda_valor_posicao(valor,2)
        return

        valor_novo = pega_valor_var(2)
        if valor_novo == valor:
            return

# Pega valor corrente da variavel
def pega_valor_var(posicao):
    try:
        mensagem = obtem_mensagem_serial()
        valor = mensagem[posicao:posicao+1]
    except:
        valor = 0
    return valor


# Mudamos a posicao da mensagem
def muda_valor_posicao(valor, posicao):
    try:
        mensagem = obtem_mensagem_serial()

        s = list(mensagem)
    
        try:
            s[posicao] = str(valor)
        except:
            pass
        mensagem = "".join(s)

        atualiza_mensagem_serial(mensagem)
    except Exception as e:
        print("Erro muda_valor_posicao: " + str(valor) + " " + str(posicao))
        pass

# Obtemos variaveis atuais de retorno
def obtem_variaveis_retorno():
    retorno = []
    try:
        with open(path_json) as json_data:
            retorno = json.load(json_data)
    except:
        pass

    return retorno


