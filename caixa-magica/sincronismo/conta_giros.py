import sys
sys.path.insert(1, '/home/pi/caixa-magica/core/')
import funcoes_serial
isRasp = funcoes_serial.getRaspPI()

if isRasp:
    import RPi.GPIO as GPIO

from time import sleep
import datetime
#import cobranca

if isRasp:
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering

    retorno = 26 

    GPIO.setup(retorno,GPIO.IN,pull_up_down=GPIO.PUD_UP)

    global giros
    giros = 0

    while True:
        state = GPIO.input(retorno)
        if state == 0:
            giros += 1
            print(giros)
            sleep(0.45)
        sleep(0.1)
