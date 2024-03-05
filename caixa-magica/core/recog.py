import cv2
import dlib
import numpy as np
import sys

import os
BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, BASEDIR + "/../tela/")

import funcoes_telas

sys.path.insert(2, BASEDIR + "/../core/")
import funcoes_reboot
import funcoes_elastic

from os.path import exists

import funcoes_downloads
import threading
from datetime import datetime

dat_pose_predictor = BASEDIR + "/../../caixa-magica-rec-facial/share/shape_predictor_5_face_landmarks.dat"
dat_face_encoder = BASEDIR + "/../../caixa-magica-rec-facial/share/dlib_face_recognition_resnet_model_v1.dat"

# checamos se os arquivos existem

# aqruivo "shape predictor"
if not exists(dat_pose_predictor):
    mensagem = "\n\n\nDat Shape Predictor\n\nnao localizado.\n\nEfetuando download\naguarde...\n\nReiniciando aplicacao."

    # Roda o processo de download como um thread
    t = threading.Thread(target = funcoes_downloads.download_shape_predictor)
    t.start()

    # Espera ate 1 minuto, caso o download nao tenha sido finalizado na thread anterior
    funcoes_telas.tela_alerta(mensagem,60000,"red")
    funcoes_reboot.restart_cm()

# arquivo "face recognition"
if not exists(dat_face_encoder):
    mensagem = "\n\n\nDat Face Encoder\n\nnao localizado.\n\nEfetuando download\naguarde...\n\nReiniciando aplicacao."

    # Roda o processo de download como um thread
    t = threading.Thread(target = funcoes_downloads.download_face_encoder)
    t.start()

    # Espera ate 1 minuto, caso o download nao tenha sido finalizado na thread anterior
    funcoes_telas.tela_alerta(mensagem,60000,"red")
    funcoes_reboot.restart_cm()

global face_detector
global face_predictor_68_point
global face_encoder

try:
    face_detector = dlib.get_frontal_face_detector()
except:
    mensagem = "Erro carregar\n\nFace detector.\n\n"
    funcoes_telas.tela_alerta(mensagem, 10000, "red")
    funcoes_reboot.restart_cm()

try:
    pose_predictor_68_point = dlib.shape_predictor(dat_pose_predictor)
except:
    mensagem="Erro carregar\n\nPose predictor."
    funcoes_telas.tela_alerta(mensagem, 10000, "red")
    funcoes_reboot.restart_cm()


try:
    face_encoder = dlib.face_recognition_model_v1(dat_face_encoder)
except:
    mensagem="Erro carregar\n\nFace encoder."
    funcoes_telas.tela_alerta(mensagem, 10000, "red")
    funcoes_reboot.restart_cm()


# Carregamos a listagem de modelos de reconhecimento facial
modelos_faciais = []
modelos_faciais_aux = funcoes_elastic.lista_conf_indices()
for aux in modelos_faciais_aux:
    arrAux = []

    if aux['habilita_rec'] == True:
        arrAux.append(aux['algoritmo'])
        arrAux.append(aux['prioridade'])
        modelos_faciais.append(arrAux)

modelos_faciais = sorted(modelos_faciais, key=lambda x:x[1], reverse=False)


def whirldata_face_detectors(img, number_of_times_to_upsample=1):
	return face_detector(img, number_of_times_to_upsample)

def whirldata_face_encodings(face_image,num_jitters=1):
    ret = []
    #print(str(datetime.utcnow()) + " Ini face_detectors")
    face_locations = whirldata_face_detectors(face_image)
    #print(str(datetime.utcnow()) + " Fim face_detectors")
    pose_predictor = pose_predictor_68_point
    predictors = [pose_predictor(face_image, face_location) for face_location in face_locations]

    try:
        predictor = predictors[0]
        #print(str(datetime.utcnow()) + " Ini arr_descriptor")
        arr_descriptor = face_encoder.compute_face_descriptor(face_image, predictor, num_jitters, 0.25)
        #print(str(datetime.utcnow()) + " Fim arr_descriptor")

        encodings = np.array(arr_descriptor)

        return encodings
    except Exception as e:
        pass

    return ret

def get_metricas(img):
    ret = []
    try:
        im_bgr = cv2.imread(img)
        known_image = im_bgr

        # Para cada modelo facial, aplicamos a checagem metrica (indo pela prioridade)
        for registro_modelo in modelos_faciais:
            modelo = registro_modelo[0].lower()

            # Se o modelo for o dlib
            if modelo == 'dlib':
                enc = whirldata_face_encodings(known_image)
                return enc
    except:
        pass

    return ret
