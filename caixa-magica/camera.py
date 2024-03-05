import numpy as np
import cv2
import time
import socket
import json
import uuid

HOST = ''  # The server's hostname or IP address
PORT = 0        # The port used by the server
BUFSIZE = 0

with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    HOST = config['core']['host']
    PORT = config['core']['port']
    BUFSIZE = config['core']['bufsize']

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('/home/pi/caixa-magica-rec-facial/haarcascade_frontalface_default.xml')

def send(file):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'facial',
                'path': file
            }
            s.connect((HOST, PORT))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)
        print('Received', repr(data))
    except:
        print("Verifique se o server está up")

FRAME = 0
while True:
    start_time = time.time()
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    FRAME = FRAME + 1
    if FRAME == 24:
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        global unique_filename
        for (x, y, w, h) in faces:
            im = frame[y:y+h, x:x+w]
            unique_filename = config['recog']['path'] + str(uuid.uuid4()) + ".jpg"
            cv2.imwrite(unique_filename, im)
        if (len(faces) > 0):
            send(unique_filename)
        FRAME = 0
    #cv2.imshow('frame', frame)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

cap.release()
cv2.destroyAllWindows()
