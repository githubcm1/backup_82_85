import numpy as np
import cv2
import time
import socket
import json
import recog
from picamera.array import PiRGBArray
from picamera import PiCamera
import operacoes as database

HOST = ''  # The server's hostname or IP address
PORT = 0        # The port used by the server
BUFSIZE = 0
NOME = 'Otavio'
CONTA = 2

with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    HOST = config['core']['host']
    PORT = config['core']['port']
    BUFSIZE = config['core']['bufsize']

#cap = cv2.VideoCapture()
face_cascade = cv2.CascadeClassifier('/home/pi/caixa-magica-rec-facial/haarcascade_frontalface_default.xml')




with PiCamera() as camera:
    rawCapture = PiRGBArray(camera)
    global FRAME
    FRAME = 0
    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        rawCapture.truncate(0)
        frame = f.array
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        FRAME = FRAME + 1
        print(FRAME)
        if FRAME == 60:
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                im = frame[y:y+h, x:x+w]
                cv2.imwrite("cap.jpg", im)
            if (len(faces) > 0):
                metricas = recog.get_metricas('cap.jpg')
                print(metricas)
                database.salvar_imagem(NOME, CONTA, metricas)
                cv2.destroyAllWindows()
                exit()
            print(faces)
            FRAME = 0
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
