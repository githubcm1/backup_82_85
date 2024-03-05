import time
import serial
import os
import json
import sys
import glob

sys.path.insert(1, "/home/pi/caixa-magica/core/")
import funcoes_placa_serial
import funcoes_core
import funcoes_logs

path = "/home/pi/caixa-magica-operacao/"

path_serial = "/dev/"
path_json = path+ "vars_serial.json"
path_mensagem = path + "mensagem_serial.json"

path_config = '/home/pi/caixa-magica-vars/config.json'

with open(path_config) as f:
    aux = json.load(f)
    refresh_placa_serial = aux['refresh_placa_serial']

BAUDRATE = 115200
TIMEOUT=0.07

global contador
contador = -1
global arquivo_log

# Lista os subdiretorios de devices
def lista_devices():
    ret=[]

    for filename in glob.iglob(path_serial + "**", recursive=True):
        filename = filename.replace(":","")
        ret.append(filename)
    return ret

def healthcheck(serial_usar):
    funcoes_logs.registra_linha_log_arquivo(arquivo_log, "iniciando healthcheck")
    try:
        #arr = os.listdir(path_serial)
        arr = lista_devices()

        if len(arr) <= 0:
            return False
        else:
            for row in arr:
                if row == serial_usar:
                    return True

        return False
    except Exception as e:
        return False

# Mata processo
def reinicia_placa():
    global contador
    contador = -1

    funcoes_logs.registra_linha_log_arquivo(arquivo_log, "reiniciando placa")
    funcoes_core.atualiza_status_placa("OFF")
    funcoes_placa_serial.reinicia_placa()

def kill_processo():
    funcoes_logs.registra_linha_log_arquivo(arquivo_log, "matando processo central_placa_serial.py")
    funcoes_core.atualiza_status_placa("OFF")
    os.system("sudo pkill -9 -f central_placa_serial.py")

def define_serial():
    funcoes_logs.registra_linha_log_arquivo(arquivo_log, "definindo serial controladora")
    funcoes_placa_serial.inicia_mensagem_placa()
    mensagem = funcoes_placa_serial.obtem_mensagem_serial()
    arrReservados = ['hidraw','/dev/serial/','/dev/ttyUSB']

    skip_device = False
    try:
        arr = lista_devices()
        for row in arr:
            
            serial_check = row

            # Nao testamos dispositivos USB, para nao conflitar com o NFC
            for reservado in arrReservados:
                if reservado in serial_check:
                    #print("Pulei " + serial_check)
                    skip_device = True
                    break

            if skip_device:
                skip_device = False
                continue

            #print("Testando " + serial_check)
            try:
                serialPort = serial.Serial(port=serial_check, baudrate=BAUDRATE, bytesize=8, timeout=TIMEOUT, stopbits=serial.STOPBITS_ONE)
                #print(serial_check)
                serialPort.write(str.encode(mensagem))
                read_val = str(serialPort.read(size=30))

                retorno_esperado = read_val[2:4]

                if retorno_esperado == "EZ":
                    funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Serial controladora determinada: " + (str(row)))
                    return row

            except Exception as e:
                pass
    except:
        return None

    return None

arquivo_log = funcoes_logs.determina_nome_log("controladora")

# Definimos a placa a ser usada
serial_usar = ""


funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Iniciando, checando serial para a controladora")
while serial_usar == "" or serial_usar == None:
    try:
        serial_usar = define_serial()
        if serial_usar == None:
            funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Serial nao conectada")
            time.sleep(1)
            kill_processo()
    except Exception as e:
        funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Erro serial: " + str(e))
        time.sleep(1)

# reseta o status da placa
funcoes_core.zera_status_placa()

# Uma vez definida a placa a ser usada, abrimos comunicacao com a mesma
path_serial_completo = serial_usar

funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Abrindo conexao com a controladora")
serialPort = serial.Serial(port=path_serial_completo, baudrate=BAUDRATE, bytesize=8, timeout=TIMEOUT, stopbits=serial.STOPBITS_ONE)

# Reseta o arquivo json de variaveis
comando = "sudo echo '{\"sonar\": 0, \"luz_ambiente\": 0, \"sensor_mao\": 0, \"tensao_entrada\": 0, \"gratuidade\": 0, \"dinheiro\": 0, \"catraca\": 0}' | sudo tee " + path_json
os.system(comando)

# Reseta o arquivo de mensagem a enviar para a placa
funcoes_placa_serial.inicia_mensagem_placa()

time.sleep(1)
num_tries = 0

while 1:
    # A cada loop, determinamos o nome do log (pois pode ocorrer mudanca na data)
    arquivo_log = funcoes_logs.determina_nome_log("controladora")

    funcoes_core.atualiza_status_placa("ON")
    
    try:
        num_tries = num_tries + 1

        try:
            if contador == -1:
                # Forca o reboot da placa
                funcoes_logs.registra_linha_log_arquivo(arquivo_log, "reiniciando placa")
                funcoes_placa_serial.reinicia_placa()
            if contador == 0:
                funcoes_logs.registra_linha_log_arquivo(arquivo_log, "desligando modem")
                funcoes_placa_serial.desliga_modem()
            if contador == 1:
                # Forcamos o religamento do modem
                funcoes_logs.registra_linha_log_arquivo(arquivo_log, "iniciando modem")
                funcoes_placa_serial.liga_modem()
            if contador > 1:
                contador = 2

            # Le a mensagem que foi configurada para comunicacao com a placa
            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Lendo mensagem para envio controladora")
            try:
                with open(path_mensagem) as json_data:
                    vars_mensagem = json.load(json_data)
                    str_encode = vars_mensagem['mensagem']
                    #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Lida mensagem para envio controladora: " + str(str_encode) )
            except Exception as e:
                pass
                #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Erro ao ler mensagem para envio controladora: " + str(e))

            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Lendo variaveis obtidas na controladora")
            try:
                with open(path_json) as json_data:
                    vars_serial = json.load(json_data)
                    #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Lidas variaveis obtidas na controladora: " + str(vars_serial) )
            except Exception as e:
                pass
                #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Erro ao ler variaveis obtidas na controladora: " + str(e))
            
            if len(str_encode) < 8:
                #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Mensagem de envio para controladora menor: " + str(str_encode))
                continue

            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Enviando mensagem controladora: " + str(str_encode))
            serialPort.write(str.encode(str_encode))

            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Recebendo mensagem controladora: " + str(str_encode))
            read_val = serialPort.read(size=30)

            #os.system("clear")
            #print("Enviado: " + str(str_encode))
            #print("Recebido: " + str(read_val))
            #time.sleep(0.2)

            # Se foi solicitado reboot da placa, aguardamos alguns segundos e ai atribuimos a mensagem padrao para retomar conexao
            if contador == -1:
                funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Efetuando reboot na placa")
                contador = 0
                time.sleep(2)
                funcoes_placa_serial.inicia_mensagem_placa()
                continue

            str_retorno = str(read_val)
            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Retorno da controladora: " + str(str_retorno))
            str_retorno = str_retorno[2:len(str_retorno)-1]
            
            if len(str_retorno) == 0:
                num_tries = num_tries+1
                
                if num_tries < 5:
                    time.sleep(0.1)        
                    continue
                else:
                    #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Sem retorno serial, reconectando")
                    kill_processo()

            header = str_retorno[0:2]
            luz_ambiente = str_retorno[2:5]
            sensor_mao = str_retorno[5:6] 
            sonar = str_retorno[6:9]
            tensao_entrada = str_retorno[9:12]
            entrada1 = str_retorno[12]
            entrada2 = str_retorno[13]
            entrada3 = str_retorno[14]
            footer = str_retorno[15:17]
            
            ### Para testes: desabilita valor vindo do sensor laser de presencao, colocando valor fixo
            vars_serial['sonar'] = int(sonar)
            vars_serial['luz_ambiente'] = int(luz_ambiente)
            vars_serial['sensor_mao'] = int(sensor_mao)
            vars_serial['tensao_entrada'] = int(tensao_entrada)
            vars_serial['gratuidade'] = int(entrada1)
            vars_serial['dinheiro'] = int(entrada2)
            vars_serial['catraca'] = int(entrada3)

            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Gravando variaveis obtidas via controladora")
            with open(path_json, "w") as saida:
                json.dump(vars_serial, saida)
                num_tries = 0
                #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Gravadas variaveis obtidas via controladora")

            if contador == 1 or contador == 0:
                time.sleep(1)

            contador = contador +1
        
        except Exception as e:
            #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Erro central: " + str(e))
            
            if healthcheck(serial_usar) == False:
                #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Serial desconectado.")
                kill_processo()

            if 'write' in str(e):
                kill_processo()
            time.sleep(0.1)
    except Exception as e:
        pass
        #funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Erro central: " + str(e))

    time.sleep(refresh_placa_serial)
