import cv2
import numpy as np
from time import sleep

def check_mouth_exists(path_img):
    try:
        mouth_cascade = cv2.CascadeClassifier('/home/pi/caixa-magica-rec-facial/haarcascade_mcs_mouth.xml')

        if mouth_cascade.empty():
            return False

        img = cv2.imread(path_img,0)

        print("PATH: " + path_img)
        print("IMG:"+ str(img))
        mouth_rects = mouth_cascade.detectMultiScale(img, 1.7, 4)
        print("MOUTH:" + str(mouth_rects))

        for (x,y,w,h) in mouth_rects:
            y = int(y - 0.15 * h)
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 3)
            print("boca: " + str(mouth_rects))
            return True
            break

        return False
    except Exception as e:
        print(str(e))
        return False

#check_mouth_exists("/home/pi/caixa-magica-img/009409ff-e0a2-4f29-8699-674717085edc.jpg")

