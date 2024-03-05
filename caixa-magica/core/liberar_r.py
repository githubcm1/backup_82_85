import db
import json
import sys
sys.path.insert(1, '/home/pi/caixa-magica/core/')
import funcoes_serial
isRasp = funcoes_serial.getRaspPI()

if isRasp:
    from RPi import GPIO
from time import sleep

CONFIG = None
with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    CONFIG = json.load(json_data)

global girando
girando = False

def both(channel):
    global girando
    girando = False
    print("Event - GPIO", GPIO.input(channel))

if isRasp:
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering
    liberaRoleta = CONFIG['pins']['catraca'] #32
    buzzer = CONFIG['pins']['buzzer'] #36
    retorno = 26

    GPIO.setup(retorno,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(retorno, GPIO.RISING, callback=both)
    GPIO.setup(liberaRoleta,GPIO.OUT) 

    GPIO.output(liberaRoleta, GPIO.LOW)
    sleep(0.3)
    GPIO.output(liberaRoleta, GPIO.HIGH)
    sleep(0.3)
    girando = True
    while girando == True:
        sleep(0.01)
    GPIO.output(liberaRoleta, GPIO.LOW)
