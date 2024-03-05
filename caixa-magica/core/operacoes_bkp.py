import db
from RPi import GPIO
from time import sleep
import json
import tela_client

conn = db.Conexao()

counter = 0

CONFIG = None
with open('config.json') as json_data:
    CONFIG = json.load(json_data)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
liberaRoleta = CONFIG['pins']['catraca'] #32
buzzer = CONFIG['pins']['buzzer'] #36
retorno = 26 

GPIO.setup(retorno,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(liberaRoleta,GPIO.OUT)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.output(buzzer, GPIO.LOW)

def salvar_imagem(nome, conta, metricas):
    array_str = ",".join(map(str, metricas))
    #print(array_str)
    sql = "INSERT INTO facial(nome, conta, data) VALUES('" + nome + "', " + str(conta) + " , cube(ARRAY[" + array_str + "]));"
    #print(sql)
    conn.manipular(sql)

def liberar(retry=False):
    # GPIO.output(buzzer, GPIO.HIGH)
    # sleep(0.5)
    # GPIO.output(buzzer, GPIO.LOW)
    for i in range(3):
         GPIO.output(liberaRoleta, GPIO.LOW)
         sleep(0.1)
         GPIO.output(liberaRoleta, GPIO.HIGH)
    # GPIO.output(liberaRoleta, GPIO.LOW)
    
    #GPIO.output(liberaRoleta, GPIO.LOW)
    # while (ret == 1):
    #     pass

    i = 0
    sleep(0.5)
    ret = GPIO.input(retorno)
    # print("inicial", ret)
    if (ret == 1):
        GPIO.output(liberaRoleta, GPIO.LOW)
        sleep(1.5)
        return liberar(True) if retry == False else False
    while (ret == 0):
        ret = GPIO.input(retorno)
        # print(ret)
        if (i == 1500):
            break #timeout
        i += 1
        sleep(0.01)
    GPIO.output(liberaRoleta, GPIO.LOW)
    sleep(2)
    
def get_user(metricas):
    array_str = ",".join(map(str, metricas))
    sql = "SELECT nome, conta, data<->cube(ARRAY[" + array_str + "]) as dist FROM facial ORDER BY dist LIMIT 1;"
    global counter
    print(sql)
    result = conn.consultar(sql)
    for r in result:
        if (r[2] <= 0.45): 
            print(r[0], r[1], "liberado")
            return r
        elif (0.60>r[2]>0.45):
            print(r[2])
            counter += 1
            print("não conseguimos liberar:" + str(counter))
            if counter == 4:
                counter = 0
                tela_client.enviar_tela(2)

                
    return False

def get_cartao(id_cartao):
    sql = "SELECT conta FROM cartao WHERE numero='{}'".format(id_cartao)
    result = conn.consultar(sql)
    if result:
        for r in result:
            return r[0]
    return False
