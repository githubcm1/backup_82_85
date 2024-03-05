import cv2
import dlib
import numpy as np

import time
import sys
import threading

path = '/home/pi/caixa-magica/core/'
sys.path.insert(1, path)
import funcoes_camera

global faceDetector
global landmarkDetector

path_camera = "rtsp://192.168.1.200/" 
FPS = 30

# Path for the detection model, you can download it from here: https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat
PREDICTOR_PATH = "/home/pi/caixa-magica-rec-facial/share/shape_predictor_68_face_landmarks.dat"

# Create object to detect the face
faceDetector = dlib.get_frontal_face_detector()

# Create object to detect the facial landmarks
landmarkDetector = dlib.shape_predictor(PREDICTOR_PATH)

def faceLandmarks(im):
    # Detect faces
    faceRects = faceDetector(im, 0)

    # Initialize landmarksAll array
    landmarksAll = []

    # For each face detected in the image, this chunk of code creates a ROI around the face and pass it as an argument to the 
    # facial landmark detector and append the result to the array landmarks 
    for i in range(0, len(faceRects)):
        newRect = dlib.rectangle(int(faceRects[i].left()),
                            int(faceRects[i].top()),
                            int(faceRects[i].right()),
                            int(faceRects[i].bottom()))
        landmarks = landmarkDetector(im, newRect)
        landmarksAll.append(landmarks)

    return landmarksAll, faceRects


def renderFacialLandmarks(im, landmarks):
    # Convert landmarks into iteratable array
    points = []
    [points.append((p.x, p.y)) for p in landmarks.parts()]

    # Loop through array and draw a circle for each landmark
    for p in points:
        cv2.circle(im, (int(p[0]),int(p[1])), 2, (255,0,0),-1)

    # Return image with facial landmarks 
    return im

# Iniciamos o status de prova de vida
funcoes_camera.status_inicial_prova_vida()

DISPLAY_VIDEO = True

global LAST_IMAGE

# Rotina que atualiza o check do arquivo de prova de vida
def check_prova_vida():
    while 1:
        try:
            funcoes_camera.check_expirada_prova_vida()
            #time.sleep(0.05)
        except:
            pass

def captura():
    global LAST_IMAGE

    cam = cv2.VideoCapture(path_camera)
    cam.set(cv2.CAP_PROP_BUFFERSIZE,1)
    cam.set(cv2.CAP_PROP_FPS, FPS)

    while 1:
        try:
            _, LAST_IMAGE = cam.read()
        except:
            cam = cv2.VideoCapture(path_camera)
            cam.set(cv2.CAP_PROP_BUFFERSIZE,1)
            cam.set(cv2.CAP_PROP_FPS, FPS)

def leitura():
    global LAST_IMAGE

    ratio_old = 0
    ratio = 0
    result = "No Smile"
    min_ratio = 0.31
    min_ratio2 = 0.27 #0.285
    min_diff_ratio = 0.02 # 0.06
    max_diff_ratio = 0.08
    habilita = False
    num_tries = 5
    cnt_num_tries = 0
    ponto_face_0x = 0
    ponto_face_0y = 0

    diff_boca_old = 0
    diff_boca = 0

    diff_olho_somb1 = 0
    diff_olho_somb2 = 0

    queue_ratio = []

    cv2.namedWindow("FrameVida", cv2.WND_PROP_FULLSCREEN)
    #cv2.setWindowProperty("FrameVida", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while 1:
        try:
            ratio_old = ratio
            habilita = False
            ponto_face_0x_ant = ponto_face_0x
            ponto_face_0y_ant = ponto_face_0y

            diff_boca_old = diff_boca

            im = LAST_IMAGE
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            im = cv2.GaussianBlur(np.array(im), (3,3), sigmaX=0, sigmaY=0)

            # Get landmarks using the function created above
            landmarks, _ = faceLandmarks(im)

            # Render the landmarks on the first face detected. You can specify the face by passing the desired index to the landmarks array.
            # In this case, one face was detected, so I'm passing landmarks[0] as the argument.
            try:
                faceWithLandmarks = renderFacialLandmarks(im, landmarks[0])
            except:
                faceWithLandmarks= []
            if len(faceWithLandmarks) <= 0:
                print("Sem face")
                diff_boca = 0
                diff_boca_old = diff_boca
                continue

            # Calculate lips width
            lips_width = abs(landmarks[0].parts()[49].x - landmarks[0].parts()[55].x)

            # Calculate jaw width
            jaw_width = abs(landmarks[0].parts()[3].x - landmarks[0].parts()[15].x)

            # Calculate the ratio of lips and jaw widths
            ratio = lips_width/jaw_width

            if len(queue_ratio) == 10:
                del queue_ratio[0]
            queue_ratio.append(ratio)

            ratio_old = min(queue_ratio)
            ratio = max(queue_ratio)

            ponto_face_0x = landmarks[0].parts()[0].x
            ponto_face_0y = landmarks[0].parts()[0].y

            diff_ponto_face_0x = abs(ponto_face_0x - ponto_face_0x_ant)
            diff_ponto_face_0y = abs(ponto_face_0y - ponto_face_0y_ant)

            try:
                diff_boca = abs((landmarks[0].parts()[62].y) - (landmarks[0].parts()[66].y))
            except:
                diff_boca = 0

            if diff_boca_old > 0 and diff_boca > 0:
                diff_boca_momento = abs(diff_boca - diff_boca_old)
            else:
                diff_boca_momento=0
            boolean_smile = False

            print("Boca: "+ str(diff_boca_momento))

            if diff_boca_momento >=12:
                diff_boca = 0
                diff_boca_old = diff_boca
                boolean_smile = True
            
            if boolean_smile:
                result = "Smile"
            else:
                result = "No Smile"

            # Add result text to the image that will be displayed
            faceWithLandmarks_v = faceWithLandmarks

            # Forma retangulo ao redor do rosto
            x = landmarks[0].parts()[0].x-10 #shape[1][0]-10
            y = landmarks[0].parts()[20].y-10 #shape[20][1]-10
            w = landmarks[0].parts()[16].x -x + 10 #shape[16][0]-x+10
            h = landmarks[0].parts()[9].y - y + 5  #shape[9][1] - y+10
            cv2.rectangle(faceWithLandmarks_v, (x,y), (x+w, y+h), (255,0,0), 3)

            cv2.putText(faceWithLandmarks_v, result, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(faceWithLandmarks_v, "Ratio Ant: " + str(ratio_old), (50, 320), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(faceWithLandmarks_v, "Ratio Atu: " + str(ratio), (50, 350), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(faceWithLandmarks_v, "Ponto Zero " + str(diff_ponto_face_0x) + " " + str(diff_ponto_face_0y), (50, 410), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # Add result text to the image that will be displayed
            faceWithLandmarks_v = faceWithLandmarks

            # Display image
            #DISPLAY_VIDEO= False
            if DISPLAY_VIDEO:
                try:
                    cv2.imshow("FrameVida", faceWithLandmarks_v)
                except Exception as e:
                    cv2.imshow("FrameVida", im)

                if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
                    break

            if result == "Smile":
                # Deixamos o status de prova de vida como verdadeiro por alguns segundos
                funcoes_camera.atualiza_status_prova_vida(True)

                result = "No Smile"

                queue_ratio = []
                ratio = 0
                ratio_old = 0

            cnt_num_tries = cnt_num_tries + 1

            if cnt_num_tries == num_tries:
                cnt_num_tries = 0

            continue
        except Exception as e:
            ratio = 99
            ratio_old = 99
            queue_ratio = []
            print("Erro:" + str(e))

t0 = threading.Thread(target=check_prova_vida)
t0.start()

t1 = threading.Thread(target=captura)
t1.start()
time.sleep(2)
t2 = threading.Thread(target=leitura)
t2.start()


