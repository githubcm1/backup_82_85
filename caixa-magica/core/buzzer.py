import time

import sys
sys.path.insert(1, '/home/pi/caixa-magica/core/')
import funcoes_serial
isRasp = funcoes_serial.getRaspPI()

if isRasp:
    import RPi.GPIO as GPIO
import json

CONFIG = None
with open('/home/pi/caixa-magica-vars/config_versao_cm.json') as json_data:
    CONFIG = json.load(json_data)

class Buzzer(object):
    def __init__(self, pin=CONFIG['pins']['buzzer']):
        self.pino = pin

    def buzzer_ok(self):
        if isRasp:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pino,GPIO.OUT)
            for x in range(2):
                GPIO.output(self.pino,GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.pino,GPIO.LOW)
                time.sleep(0.1)

    def buzzer_nok(self):
        if isRasp:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pino,GPIO.OUT)
            for x in range(1):
                GPIO.output(self.pino,GPIO.HIGH)
                time.sleep(0.8)
                GPIO.output(self.pino,GPIO.LOW)
