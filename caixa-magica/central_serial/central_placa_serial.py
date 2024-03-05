import time
import serial
import os
import json

path = "/home/pi/caixa-magica/"

liga = False

try:
    with open(path + "/../caixa-magica-vars/config.json") as jsondata:
        aux = json.load(jsondata)
        liga = aux['liga_serial_placa']
except Exception as e:
    print(str(e))
    pass

if liga == False:
    quit()

path_serial = "/dev/serial/by-id/"
path_json = path + "/central_serial/vars_serial.json"
path_mensagem = path + "/central_serial/mensagem_serial.json"

def define_serial():
    try:
        arr = os.listdir(path_serial)
        for row in arr:
            serial_check = path_serial + row
            try:
                serialPort = serial.Serial(port=serial_check, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

                serialPort.write(str.encode("CA000EZ"))
                read_val = str(serialPort.read(size=19))

                retorno_esperado = read_val[2:4]
                print(retorno_esperado)

                if retorno_esperado == "EZ":
                    return row

            except Exception as e:
                pass
    except:
        return None

    return None

def healthcheck(serial_usar):
    try:
        arr = os.listdir(path_serial)
        print(arr)

        if len(arr) <= 0:
            return False
        else:
            for row in arr:
                if row == serial_usar:
                    return True

        return False
    except Exception as e:
        return False

serial_usar = define_serial()

if serial_usar == None:
    print("Serial nao conectada")
    quit()

path_serial_completo = path_serial + serial_usar
serialPort = serial.Serial(port=path_serial_completo, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

comando = "sudo echo '{\"mensagem\": \"CA000EZ\"}' | sudo tee " + path_mensagem
os.system(comando)

comando ="sudo echo '{\"sonar\": 0, \"luz_ambiente\": 0, \"sensor_mao\": 0, \"tensao_entrada\": 0, \"gratuidade\": 0, \"dinheiro\": 0, \"catraca\": 0}' | sudo tee " + path_json
os.system(comando)


i = 0

while 1:
    if healthcheck(serial_usar) == False:
        print("Serial desconectado. Encerrando.")
        break

    try:
        os.system("clear")
        
        # Le a mensagem que foi configurada para comunicacao com a placa
        try:
            with open(path_mensagem) as json_data:
                vars_mensagem = json.load(json_data)
                str_encode = vars_mensagem['mensagem']
        except:
            pass

        try:
            with open(path_json) as json_data:
                vars_serial = json.load(json_data)
        except:
            pass

        serialPort.write(str.encode(str_encode))
        read_val = serialPort.read(size=19)

        str_retorno = str(read_val)

        header = str_retorno[2:4]
        luz_ambiente = str_retorno[4:7]
        sensor_mao = str_retorno[7:10]
        sonar = str_retorno[10:14]
        tensao_entrada = str_retorno[14:16]
        entrada1 = str_retorno[16]
        entrada2 = str_retorno[17]
        entrada3 = str_retorno[18]
        footer = str_retorno[19:21]

        vars_serial['sonar'] = int(sonar)
        vars_serial['luz_ambiente'] = int(luz_ambiente)
        vars_serial['sensor_mao'] = int(sensor_mao)
        vars_serial['tensao_entrada'] = int(tensao_entrada)
        vars_serial['gratuidade'] = int(entrada1)
        vars_serial['dinheiro'] = int(entrada2)
        vars_serial['catraca'] = int(entrada3)
        
        with open(path_json, "w") as saida:
            json.dump(vars_serial, saida)

        print("Alive")
        #print("Retorno: " + str(read_val))
        #print("header:" + header)
        #print("Luz:" + luz_ambiente)
        #print("Sensor mao:" + sensor_mao)
        #print("Tensao:" + tensao_entrada)
        #print("Sonar:" + sonar)
        #print("Entrada1:" + entrada1)
        #print("Entrada2:" + entrada2)
        #print("Entrada3:" + entrada3)
        #print("Footer:" + footer)

    except:
        continue

    time.sleep(0.1)
