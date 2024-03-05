import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import db
import funcoes_viagem

import base64
from datetime import datetime, timedelta
import hashlib
import threading
import os
import json
import serial
import time

path_json_saida = "/home/pi/caixa-magica-operacao/qrcode.json"
path_indicador_status = '/home/pi/caixa-magica-operacao/status_leitorqr.json'
path_json_instalacao = '/home/pi/caixa-magica-operacao/instalacao.json'
path_json_mensagens = "/home/pi/caixa-magica-vars/mensagens.json"

global GLOBAL_OPERADORA
global GLOBAL_BILHETADORA
global GLOBAL_MENSAGEM_SEM_SALDO

# Obtemos os codigos de bilhetadora e operadora, para uso em determinadas situacoes
# No QR Code do cliente, podera haver saldos de bilhetadoras que nao sejam deste validador
try:
    with open(path_json_instalacao) as json_data:
        json_inst = json.load(json_data)
        GLOBAL_OPERADORA = json_inst['operadora']
        GLOBAL_BILHETADORA = json_inst['bilhetadoraId']
except:
    GLOBAL_OPERADORA = ""
    GLOBAL_BILHETADORA = ""

try:
    with open(path_json_mensagens) as json_data:
        json_aux = json.load(json_data)
        GLOBAL_MENSAGEM_SEM_SALDO = json_aux['mensagem_sem_saldo_praca']
except:
    GLOBAL_MENSAGEM_SEM_SALDO = "Nao ha saldo\npara este municipio."

def get_local_json():
    return path_json_saida

def valor_qrcode_json():
    # Abre o arquivo
    try:
        with open(path_json_saida) as json_data:
            json_qrcode = json.load(json_data)
        return json_qrcode["qrcode"]
    except:
        return ""

def limpa_qrcode():
    # Remove arquivo
    os.system("sudo rm -f " + path_json_saida)

    # Recria o arquivo
    comando = "sudo echo '{\"qrcode\":\"\"}' | sudo tee "+ path_json_saida
    os.system(comando)    

def inicializa_coletor_qrcode():
    t1 = threading.Thread(target=coletor_qrcode)
    t1.start()

# Retorna status do leitor QRCode
def retorna_status_qrcode():
    status = "ON"
    try:
        with open(path_indicador_status) as json_data:
            json_status = json.load(json_data)
            status = json_status['status']
    except:
        pass

    return status

# Rotina que inicializa o evento de qrcode
def coletor_qrcode():
    while 1:
        # Atualiza o status da leitora de Qr Code
        comando = "sudo echo '{\"status\":\"OFF\"}' | sudo tee "+ path_indicador_status
        os.system(comando)

        try:
            limpa_qrcode()

            # Abre o arquivo de status
            with open(path_indicador_status) as json_data:
                json_status = json.load(json_data)

            # Abre o arquivo
            with open(path_json_saida) as json_data:
                json_qrcode = json.load(json_data)

            # Abre o arquivo de configuracao
            with open(path_atual + "/../../caixa-magica-vars/config.json") as f:
                aux = json.load(f)
                path_leitorqr1 = aux['leitorqr_tentativa1']
                path_leitorqr2 = aux['leitorqr_tentativa2']

            # Tenta primeiro pelo endereco #1
            try:
                ser = serial.Serial(
                    port=path_leitorqr1,\
                    baudrate=9600,\
                    parity=serial.PARITY_NONE,\
                    stopbits=serial.STOPBITS_ONE,\
                    bytesize=serial.EIGHTBITS,\
                    timeout=0)
            except:
                ser = serial.Serial(
                    port=path_leitorqr2,\
                    baudrate=9600,\
                    parity=serial.PARITY_NONE,\
                    stopbits=serial.STOPBITS_ONE,\
                    bytesize=serial.EIGHTBITS,\
                    timeout=0)

            line = []
            string_qr = ""
            
            cnt_status = 0
            while True:
                cnt_status = cnt_status + 1

                if cnt_status > 10:
                    # Atualiza o status do leitor QR
                    json_status['status'] = "ON"
                    with open(path_indicador_status, 'w') as f:
                        f.write(json.dumps(json_status))
                    cnt_status = 0
                    time.sleep(0.015)

                for c in ser.read():
                    line.append(chr(c))
                    if c == 13:
                        string_qr = ''.join(line).strip()
                        json_qrcode["qrcode"] = string_qr

                        # Caso alguma tela esteja ja em processamento deste semaforo, abortamos esta acao
                        # (ISSO EVITARA QUE UM QRCODE POSSA INTERFERIR NO PROCESSAMENTO)
                        if funcoes_viagem.semaforo_ativo():
                            json_qrcode["qrcode"] = ""
                        
                        with open(path_json_saida, 'w') as f:
                            f.write(json.dumps(json_qrcode))

                        line = []
                        break
            ser.close()
        except Exception as e:
            # Atualiza o status do leitor QR
            json_status['status'] = "OFF"
            with open(path_indicador_status, 'w') as f:
                f.write(json.dumps(json_status))

            time.sleep(5)


# Checa se a conta do cliente exige contra check de info facial
def checkContraCheckFacial(conta_id, conn):
    sql = "select 1 from contas where id_web = %s and contra_check_facial = true"
    dados = (conta_id,)
    result = conn.consultarComBind(sql, dados)
    
    for row in result:
        return True
    return False

# Checa se devemos criar a conta da pessoa em sistema
def cadastra_conta_qrcode(conta_id, nome, saldo):
    conn_interna = db.Conexao()
    
    # Insere a conta
    dados = (str(conta_id), str(nome),)
    sql = """insert into contas(id_web, cpf, nome, bloqueado,dateinsert)
           values (%s, '', %s, false,now()) on conflict (id_web) do update set bloqueado=false, dateupdate=now()"""
    conn_interna.manipularComBind(sql,dados)

    # Insere na tabela de saldo
    dados=(str(conta_id), str(saldo), )
    sql = """insert into contas_controle_saldos (contaid, saldo_sumario,dateinsert)
             values (%s, %s, now())
             on conflict (contaid) do nothing"""
    conn_interna.manipularComBind(sql, dados)

    del conn_interna

# Retorna id do operador
def getIdOperadorQr(qrcode):
    try:
        conn_interna = db.Conexao()
        dados = (qrcode, )
        sql = "select id_web from operadores where id_qr = %s"
        c = conn_interna.consultarComBind(sql, dados)
        del conn_interna
    
        for row in c:
            return row[0]
        return None
    except:
        return None

# checa se o qrcode eh de um fiscal
def check_fiscal(string_qrcode):
    conn_interna = db.Conexao()
    dados=(str(string_qrcode),)
    sql = "select count(*) from operadores where id_qr = %s and fiscal = true"
    c = conn_interna.consultarComBind(sql, dados)
    del conn_interna

    if c[0][0] == 0:
        return False
    return True

# checa se um qrcode ja foi utilizado pelo usuario nesta caixa magica
def check_qrcode_utilizado(string_qrcode):
    conn_interna = db.Conexao()

    dados=(str(string_qrcode),)
    sql = """select count(*) tot 
             from qrcodes_utilizados q 
             where q.qrcode = %s"""
    c = conn_interna.consultarComBind(sql,dados)
    del conn_interna

    if c[0][0] == 0:
        return False
    return True
 
# Insere um qrcode utilizado na base, para evitar que haja reuso
def registra_qrcode_utilizado(string_qrcode):
    conn_interna = db.Conexao()
    dados=(str(string_qrcode),)
    sql = "insert into qrcodes_utilizados (qrcode, dateinsert) values (%s, now())"
    conn_interna.manipularComBind(sql,dados)
    del conn_interna

# Rotina de expurgo de qrcodes ja utilizados com mais de 1 dia
def expurga_qrcodes_utilizados():
    conn_interna = db.Conexao()
    sql = "delete from qrcodes_utilizados qu where qu.dateinsert < now() - interval '1 day'"
    conn_interna.manipular(sql)
    del conn_interna

# Desmembra o trecho do qr code em base 64 para variaveis uteis
def desmembraQrCodeVars(qr_string):
    # Retorno
    # Posicao 0: sem uso
    # Posicao 1: id da conta
    # Posicao 2: saldo
    # Posicao 3: mensagem de erro (quando necessario)
    
    global GLOBAL_MEMSAGEM_SEM_SALDO

    try:
        arr_qr_string = qr_string.split("#")
        base_64_qr = arr_qr_string[2]

        # A partir da string base 64, efetuamos o decode dela
        base_64_qr_decode = str(base64.b64decode(base_64_qr).decode('utf-8'))

        # Se a string inicia com #, entao estamos no formato antigo (sem saldos por bilhetadora)
        if base_64_qr_decode[0:1] == "#":
            # Efetuamos a quebra da string de base 64
            arr_decode = base_64_qr_decode.split("#")
            arr_decode.append("")
        # Se a string iniciar com "A", quer dizer que estamos na seguinte notacao
        #idconta|bilhetadora|saldo|bilhetadora|saldo
        elif base_64_qr_decode[0:1] == "A":
            achou_saldo = False
            arr_decode_aux = base_64_qr_decode.split("|")

            # Neste formato, o id da conta esta na segunda posicao
            arr_decode = []
            arr_decode.append("")
            arr_decode.append(arr_decode_aux[1])

            # Quanto ao saldo, dvemos varrer as demais posicoes, para achar a bilhetadora em questao
            cnt_coluna=0
            arr_bilhetadora=[]
            arr_saldo=[]
            for coluna in arr_decode_aux:
                if cnt_coluna < 2:
                    cnt_coluna = cnt_coluna+1
                    continue
                else:
                    # se for uma posicao "par" no array, trata-se da bilhetadora
                    if (cnt_coluna % 2) == 0:
                        arr_bilhetadora.append(coluna)
                    else:
                        arr_saldo.append(coluna)
                cnt_coluna = cnt_coluna+1

            # partindo da lista de bilhetadora, olhamos se ha algum saldo pra bilhetadora deste equipamento
            i = 0
            while i < len(arr_bilhetadora):
                if str(arr_bilhetadora[i]) == str(GLOBAL_BILHETADORA):
                    achou_saldo = True
                    arr_decode.append(float(arr_saldo[i]))
                    arr_decode.append("") # Quando nao ha um erro
                    break
                i= i+1

            # Se nao existe saldo pra bilhetadora, atribuimos um saldo negativo que nao permitira o uso
            if not achou_saldo:
                arr_decode=[]
                arr_decode.append("")
                arr_decode.append(-999999999)
                arr_decode.append(-99999)
                arr_decode.append(GLOBAL_MENSAGEM_SEM_SALDO)

        # Caso contrario, esta na notacao nova (JSON)
        #else:
        #    achou_saldo = False
        #    json_origem = base_64_qr_decode.strip()
        #    arr_qrcode = json.loads(json_origem)
        #    arr_decode=[]
        #    arr_decode.append("")
        
        #    # Atribuimos o id de conta
        #    arr_decode.append(arr_qrcode['contaId'])

        #    # Atribuimos o saldo, de acordo com a bilhetadora da pessoa
        #    for row in arr_qrcode['saldos']:
        #        if row['bilhetadoraId'] == GLOBAL_BILHETADORA:
        #            achou_saldo = True
        #            arr_decode.append(row['saldo'])
        #            arr_decode.append("") # quando nao tem erros
        #            break

        #    # Se nao existe saldo pra bilhetadora, atribuimos um saldo negativo que nao permitira o uso
        #    if not achou_saldo:
        #        arr_decode=[]
        #        arr_decode.append("")
        #        arr_decode.append(-999999999)
        #        arr_decode.append(-99999)
        #        arr_decode.append(GLOBAL_MENSAGEM_SEM_SALDO)
    except Exception as e:
        arr_decode=[]
        arr_decode.append("")
        arr_decode.append(-999999999) # Id de conta
        arr_decode.append(-99999) # saldo
        arr_decode.append(GLOBAL_MENSAGEM_SEM_SALDO)
    return arr_decode

# Checa a validade do qrcode
def checaTokenQrCode(qr_string, num_seconds_expire):
    global GLOBAL_OPERADORA
    global GLOBAL_BILHETADORA

    try:
        # Quebra a string no caractere definido |
        arr_qr_string = qr_string.split("#")

        # A primeira parte serve como chave token
        token_qr = arr_qr_string[1]
        base_64_qr = arr_qr_string[2]

        # A partir da string base 64, efetuamos o decode dela
        base_64_qr_decode = str(base64.b64decode(base_64_qr))

        # se a string inicia com #, entao estamos no formato antigo (sem saldos por bilhetadora)
        if base_64_qr_decode[2] == "#":
            # Efetuamos a quebra da string de base 64
            arr_decode = base_64_qr_decode.split("#")
            conta_id = arr_decode[1]
        elif base_64_qr_decode[2] == "A":
            arr_decode = base_64_qr_decode.split("|")
            conta_id = arr_decode[1]
        else:
            conta_id = ""

        if conta_id == "":
            return 'EXPIRADO'

        i = -5 # Tolerancia de 5 segundos
        utc_now = datetime.utcnow()

        while i <= num_seconds_expire:
            current_timestamp_de = utc_now + timedelta(seconds=i)
            str_timestamp_de = str(current_timestamp_de.strftime("%Y%m%d%H%M%S"))
            #print(str_timestamp_de)
            str_timestamp = str_timestamp_de + "#" + str(conta_id)

            str_timestamp = str_timestamp.encode("utf-8") 
        
            # A partir do valor do timestamp, geramos o sha1
            m = hashlib.sha1(str_timestamp)
            str_timestamp_sha1 = (m.hexdigest())

            # Se o token do qr code bater com o que temos aqui, entao deixamos passar)
            if str_timestamp_sha1 == token_qr:
                return 'OK'

            i = i+1

        # Se chegou ate aqui, significa que o timestamp nao bateu. Caso expirado
        return 'EXPIRADO'
    except:
        return "INVALIDO"

#print(datetime.utcnow())
#print(checaTokenQrCode('#9bd56e6bb43ddf3ccb977280f216c76f02368cc9#QXw0NDQ0fDd8NDIuOA==',120))
#print(datetime.utcnow())

#print(checaTokenQrCode("Hello Pareto World", 120))

#print(checaTokenQrCode("#91631e5df50f59436b56de651c2cb1a1bd8f0e9c#QXwxMDM2fDF8MTAuMDB8MnwyMC4wMA==", 600))

#coletor_qrcode()
