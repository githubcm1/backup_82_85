import RPi.GPIO as GPIO
import logging
import datetime
from time import sleep

logging.basicConfig(filename='/home/pi/caixa-magica-logs/osc.log', filemode='a', format='%(asctime)-15s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering

retorno = 26 
contador = 0

GPIO.setup(retorno,GPIO.IN,pull_up_down=GPIO.PUD_UP)
last_state = GPIO.input(retorno)
last_time = datetime.datetime.now()
print("Inicializando...", last_state)
while True:
    sleep(0.01)
    state = GPIO.input(retorno)
    if state != last_state:
        last_state = state
        delta = datetime.datetime.now() - last_time
        last_time = datetime.datetime.now()
        contador += 0.5
        logging.info("MUDOU " +str(state))
        logging.info("Diferença de tempo: " + str(delta))
        logging.info("Contagem: " + str(contador))
        print("MUDOU " +str(state))
        print("Diferença de tempo: " + str(delta))
        print("Contagem: " + str(contador))
