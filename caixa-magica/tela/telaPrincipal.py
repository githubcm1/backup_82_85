import dlib
from imutils import face_utils

import os
import time
import sys
path_atual = "/home/pi/caixa-magica/tela"
sys.path.insert(1, path_atual)

os.system("sudo python3 " + path_atual + "/../tela_aguarde.py & ")
os.system("sudo python3 "+ path_atual+ "/../keep_alive.py &")

os.system("sudo pkill -9 -f core.py")
os.system("sudo pkill -9 -f monitor_core_check.py")
os.system("sudo python3 " + path_atual + "/../core/monitor_core_check.py &")

# Inicia job de luz auxiliar (em caso de proximidade do sonar e com iluminacao ambiente ruim)
os.system("sudo python3 " + path_atual + "/../core/luz_auxiliar.py &")

from tkinter import *
from pyzbar import pyzbar 
import tkinter.ttk as ttk
import cv2
import socket
import json
import unicodedata
import re
from threading import Thread
from datetime import datetime
import uuid
import numpy as np
from PIL import Image, ImageFont, ImageDraw
sys.path.insert(1, path_atual + '/../core/')
import funcoes_serial
import funcoes_camera
import funcoes_tela_corrente
import funcoes_core
import funcoes_internet
import funcoes_elastic
import funcoes_prova_vida_olhos

with open(path_atual + "/../version.txt", "r") as f:
    version = f.read()
    f.close()

import sonar
import check_mouth
import db
import funcoes_qrcode
import funcoes_logs
import funcoes_viagem
import funcoes_matrizes_memoria
import funcoes_nfc
import funcoes_temperatura

sys.path.insert(2, path_atual + '/../tela/')
import funcoes_telas

from PIL import Image, ImageTk
import tkinter as tk
import threading
from itertools import count

import os.path
from datetime import datetime, timedelta

global LAST_IMAGE
LAST_IMAGE = []
global LAST_IMAGE_TS
LAST_IMAGE_TS = ""
global LAST_IMAGE_LIDA
LAST_IMAGE_LIDA = time.time() + 30

global HAAR_X
global HAAR_Y
global HAAR_W
global HAAR_H
global NUM_TENTATIVAS_FAIL_CORE
NUM_TENTATIVAS_FAIL_CORE = 0

global MATAR_THREAD
MATAR_THREAD = False

global MENSAGEM_PROCESS
MENSAGEM_PROCESS = ""
global SUSPENDE_SEND
SUSPENDE_SEND = False

local = 'telaPrincipal.py'
funcoes_logs.insere_log("Iniciando " + local, local)

global GLOBAL_SENTIDO 
GLOBAL_SENTIDO= 'IDA'

global frame
global rawCapture
global FRAME
global vid

# cria diretorio de imagens tmeporarias (qrcode)
global FOLDER_QR_TMP
global FILE_QR_TMP
FOLDER_QR_TMP = "/home/pi/caixa-magica-img/qr_tmp/"
FILE_QR_TMP = FOLDER_QR_TMP + "qr.jpg"
os.system("sudo mkdir -p " + FOLDER_QR_TMP)

global CORE_STATUS
CORE_STATUS = "ON"

global PLACA_STATUS
PLACA_STATUS = "ON"

global STATUS_QR
STATUS_QR = "ON"

global STATUS_NFC
STATUS_NFC = "ON"

global STATUS_ES
STATUS_ES = "ON"

global SUSPENDE_CORE_FECHAMENTO
SUSPENDE_CORE_FECHAMENTO = False

global serial_id
serial_id = funcoes_serial.getSerial()

FILE_VIDEO_ALIVE = "/home/pi/caixa-magica/video_alive.txt"

GLOBAL_MENSAGEM_FACE = "Rosto enquadrado"

global GLOBAL_TIMEOUT_PARA_PROPAGANDA
GLOBAL_TIMEOUT_PARA_PROPAGANDA = datetime.utcnow()

global GLOBAL_LIMITE_TIMEOUT_PARA_PROPAGANDA
GLOBAL_LIMITE_TIMEOUT_PARA_PROPAGANDA = 5

global GLOBAL_ARRAY_LISTA_PROPAGANDAS
GLOBAL_ARRAY_LISTA_PROPAGANDAS = []

global GLOBAL_TIMEOUT_CADA_PROPAGANDA
GLOBAL_TIMEOUT_CADA_PROPAGANDA = datetime.utcnow()

global GLOBAL_LIMITE_TIMEOUT_CADA_PROPAGANDA
GLOBAL_LIMITE_TIMEOUT_CADA_PROPAGANDA = 5

global GLOBAL_IMAGEM_PROPAGANDA
GLOBAL_IMAGEM_PROPAGANDA = ""

global GLOBAL_EXIBE_PROPAGANDA
GLOBAL_EXIBE_PROPAGANDA = False

global GLOBAL_CAMERA_ID

global GLOBAL_PERIODO_CONTRA_CHECK_FACIAL
GLOBAL_PERIODO_CONTRA_CHECK_FACIAL = False

global GLOBAL_INICIO_CONTRA_CHECK_FACIAL
GLOBAL_INICIO_CONTRA_CHECK_FACIAL = ""

global STATUS_INTERNET
STATUS_INTERNET = ""

global VAL_SONAR
VAL_SONAR = -1

global LAMBDA_DISPLAY
LAMBDA_DISPLAY = 0

global GLOBAL_TEMPERATURA_CPU
GLOBAL_TEMPERATURA_CPU = ""

conn = db.Conexao()

# Obtemos o id de camera do parametro 2 do sys.argv (se informado)
try:
    GLOBAL_CAMERA_ID = sys.argv[1]
except:
    GLOBAL_CAMERA_ID = ""

# Rotina que checa se as propagandas devem ser exibidas na tela principal
def permite_exibir_propaganda():
    global GLOBAL_TIMEOUT_PARA_PROPAGANDA
    global GLOBAL_LIMITE_TIMEOUT_PARA_PROPAGANDA
    global GLOBAL_EXIBE_PROPAGANDA

    if not GLOBAL_EXIBE_PROPAGANDA:
        return False

    utc_atual = datetime.utcnow()
    utc_comparar = GLOBAL_TIMEOUT_PARA_PROPAGANDA + timedelta(seconds=GLOBAL_LIMITE_TIMEOUT_PARA_PROPAGANDA)

    distancia_permitida = config['rec_facial']['max_dist_sonar']
    dist = sonar.distance()
    
    if dist < 0:
        dist = distancia_permitida+1

    # Se a distancia maxima permitida for inferior aquela registrada pelo sonar, entao nao existem objetos proximos
    # assim, podemos ativar a exibicao
    if dist > distancia_permitida:
        # Se ja passou o tempo limite com o sonar distante de alguma pessoa, ai sim permitir a exibicao
        if utc_atual > utc_comparar:
            return True
    else:
        GLOBAL_TIMEOUT_PARA_PROPAGANDA = datetime.utcnow()
            
    return False

def thread_propaganda():
    time.sleep(20)

    global GLOBAL_ARRAY_LISTA_PROPAGANDAS
    global GLOBAL_TIMEOUT_CADA_PROPAGANDA
    global GLOBAL_LIMITE_TIMEOUT_CADA_PROPAGANDA
    global GLOBAL_IMAGEM_PROPAGANDA

    while True:
        # Se nao tem propagandas no array, consulta a lista no banco de dados
        if len(GLOBAL_ARRAY_LISTA_PROPAGANDAS) <= 0:
            sql = "select id, imagem, duracao_em_segundos from propagandas_em_exec where now() between vigenciade and vigenciaate  order by ordenacao"
            result = conn.consultar(sql)

            for row in result:
                arrAux = []
                arrAux.append(row[0])
                arrAux.append(row[1])
                arrAux.append(int(row[2]))
                GLOBAL_ARRAY_LISTA_PROPAGANDAS.append(arrAux)
        
        # Estabelece que a imagem em questao seja a primeira da lista
        GLOBAL_IMAGEM_PROPAGANDA = ""

        if len(GLOBAL_ARRAY_LISTA_PROPAGANDAS) > 0:
            GLOBAL_IMAGEM_PROPAGANDA              = GLOBAL_ARRAY_LISTA_PROPAGANDAS[0][1]
            GLOBAL_LIMITE_TIMEOUT_CADA_PROPAGANDA = GLOBAL_ARRAY_LISTA_PROPAGANDAS[0][2]

            utc_atual = datetime.utcnow()
            utc_comparar = GLOBAL_TIMEOUT_CADA_PROPAGANDA + timedelta(seconds=GLOBAL_LIMITE_TIMEOUT_CADA_PROPAGANDA)

            if utc_atual > utc_comparar:
                GLOBAL_TIMEOUT_CADA_PROPAGANDA = datetime.utcnow()
                
                # Remove a propaganda da lista de exibicao
                GLOBAL_ARRAY_LISTA_PROPAGANDAS.pop(0)

        time.sleep(0.5)

def capturaHaar(gray, factor1, factor2, mensagem, image):
    faces = face_cascade.detectMultiScale(gray, factor1, factor2)

    for x,y,w,h in faces:
        return faces
    
    faces = []
    return faces

def rotateImage(image, angel):#parameter angel in degrees
    height = image.shape[0]
    width = image.shape[1]
    height_big = height * 2
    width_big = width * 2
    image_big = cv2.resize(image, (width_big, height_big))
    image_center = (width_big/2, height_big/2)#rotation center
    rot_mat = cv2.getRotationMatrix2D(image_center,angel, 0.5)
    result = cv2.warpAffine(image_big, rot_mat, (width_big, height_big), flags=cv2.INTER_LINEAR)

    del height
    del width
    del height_big
    del width_big
    del image_big
    del rot_mat
    del image_center
    return result

def telaCheckMask():
    funcoes_logs.insere_log("Exibindo tela de notificacao do uso da mascara", local)
    root = tk.Tk()
    root.configure(background='orange')
    root.attributes("-fullscreen",True)
    mensagem = tk.Label(root, text="\n\n\n\n\nVerifique\n\nuso da máscara.", fg='black', bg='orange', font=('Verdana','26','bold'))
    mensagem.pack()
    root.after(800, lambda: [root.destroy(), root.quit()])
    root.mainloop()
    return

#################################################################
#  funcao tem por objetivo definir o padrao de tela
#  parametro: background - cor de fundo
#                   foreground   - core de primeiro plano
#                   texto1  - primeira linha de texto a ser impressa
#                   texto2  - segunda linha de texto a ser impressa
#################################################################
def cfgTelas(background,foreground,texto1, texto2,ipady = 350,tempo = 3000, tamanho = 36, fundo = "green2"):                          
    root = Tk()
    widget = Frame(root)
    root.configure(background = fundo)
    root.attributes("-fullscreen",True)
    widget.pack()
    localString = texto1
    
    if (len(texto2)>0):
        localString +=  '\n ' + texto2
        
    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana',tamanho,'bold'))
    
    msg.grid(row=0,column=1,ipady=ipady)
    root.after(tempo, lambda: root.destroy())
    root.mainloop()

global aux_catraca
aux_catraca = True
global GLOBAL_EXPIRACAO_QRCODE

HOST = 'localhost'              # Endereco IP do Servidor
PORT = 30020          # Porta que o Servidor esta

orig = (HOST, PORT)
orig_c = (HOST,30110)
HOST_CORE = ''  # The server's hostname or IP address
PORT_CORE = 0        # The port used by the server
BUFSIZE = 0

PATH_FRONTALFACE = path_atual + '/../../caixa-magica-rec-facial/haarcascade_frontalface_default.xml'

# checa se a biblioteca existe no sistema
if not os.path.isfile(PATH_FRONTALFACE):
    funcoes_logs.insere_log("Biblioteca " + PATH_FRONTALFACE + " para rec facial não identificada. Reiniciando aplicação.", local)
    cfgTelas("red2", "white", "Biblioteca\nrec facial\nnão encontrada.\n\nReiniciando aplicação.","", 250, 3000, 25, "red2")
    os.system("sudo " + path_atual + "/../restart.sh")


path_skin = path_atual + "/tela_moldura.png"
skin = Image.open(path_skin).convert('RGBA')
face_cascade = cv2.CascadeClassifier(PATH_FRONTALFACE)
funcoes_logs.insere_log("CV2 face_cascade instanciado", local)

GLOBAL_EXIBE_NOME_FACIAL = True
GLOBAL_EXIBE_NOME_QRCODE = True
GLOBAL_BGR2GRAY = True

# Abrimos o arquivo de configuracao de prova de vida dos olhos, caso a configuracao esteja habilitada
try:
    with open(path_atual + "/../../caixa-magica-vars/params_prova_vida_olhos.json") as json_data:
        aux = json.load(json_data)
        BLINK_OLHOS_VALIDACAO = aux['ligado']
        BLINK_OLHOS_LIMITE_EAR = aux['limite_ear']
        BLINK_OLHOS_MIN_EAR = aux['min_ear']
        BLINK_OLHOS_MAX_EAR = aux['max_ear']
        BLINK_OLHOS_PATH_LANDMARKS = aux['path_landmarks']
except Exception as e:
    BLINK_OLHOS_VALIDACAO = False
    BLINK_OLHOS_LIMITE_EAR = 0
    BLINK_OLHOS_MIN_EAR = 0
    BLINK_OLHOS_MAX_EAR = 0
    BLINK_OLHOS_PATH_LANDMARKS = ""

# Se a prova de vida por olhos estiver ligada
if BLINK_OLHOS_VALIDACAO == True:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(BLINK_OLHOS_PATH_LANDMARKS)
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Abre arquivo de configuracoes gerais
with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    HOST_CORE = config['core']['host']
    PORT_CORE = config['core']['port']
    BUFSIZE = config['core']['bufsize']

    try:
        GLOBAL_TIMEOUT_CONTRA_CHECK_FACIAL = config['timeout_contra_check_facial']
    except:
        GLOBAL_TIMEOUT_CONTRA_CHECK_FACIAL = 3

    try:
        GLOBAL_LIMITE_TIMEOUT_PARA_PROPAGANDA = config['propaganda_apos_segundos']
    except:
        pass

    try:
        GLOBAL_EXIBE_PROPAGANDA = config['exibe_propaganda']
    except:
        GLOBAL_EXIBE_PROPAGANDA = False

    try:
        GLOBAL_GRAUS_INCLINACAO_DIREITA = config['graus_inclinacao_direita']
    except:
        GLOBAL_GRAUS_INCLINACAO_DIREITA = 0

    try:
        GLOBAL_GRAUS_INCLINACAO_ESQUERDA = config['graus_inclinacao_esquerda']
    except:
        GLOBAL_GRAUS_INCLINACAO_ESQUERDA = 0

    try:
        GLOBAL_EXIBE_MOLDURA = config['exibe_moldura']
    except:
        GLOBAL_EXIBE_MOLDURA = False

    try:
        GLOBAL_EXIBE_NOME_FACIAL = config['exibe_nome_facial']
    except:
        pass

    try:
        GLOBAL_EXIBE_NOME_QRCODE = config['exibe_nome_qrcode']
    except:
        pass

    try:
        GLOBAL_BGR2GRAY = config['bgr2gray']
    except:
        pass

    try:
        GLOBAL_EXPIRACAO_QRCODE = config['expiracao_qrcode']
    except:
        GLOBAL_EXPIRACAO_QRCODE = 120

    try:
        GLOBAL_SCALE_FACTOR = config['scaleFactor']
    except:
        GLOBAL_SCALE_FACTOR = 1.1

    try:
        GLOBAL_MIN_NEIGH = config['minNeigh']
    except:
        GLOBAL_MIN_NEIGH = config['minNeigh']

# Atualiza o contador de tentativas de acesso ao core
def atualiza_tentativas_core():
    global NUM_TENTATIVAS_FAIL_CORE

    NUM_TENTATIVAS_FAIL_CORE = NUM_TENTATIVAS_FAIL_CORE+1

# Zera contatdor de tentativas ao acesso core
def zera_tentativas_core():
    global NUM_TENTATIVAS_FAIL_CORE

    NUM_TENTATIVAS_FAIL_CORE = 0

# Rotina envia ao core arquivo de imagem, além da matriz facial
def send(file, var_sessao):
    global SUSPENDE_SEND

    if SUSPENDE_SEND:
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'facial',
                'path': file,
                'var_sessao': var_sessao
            }
            s.connect((HOST_CORE, PORT_CORE))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)

            s.shutdown(socket.SHUT_RDWR)
            s.close()

            zera_tentativas_core()
    except Exception as e:
        atualiza_tentativas_core()
        funcoes_logs.insere_log("Erro ao enviar face para o core - " + str(e), local)

def tratar_palavra(palavra):
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)

def send_fechar(barcode):
    global SUSPENDE_SEND
    global SUSPENDE_CORE_FECHAMENTO

    if str(barcode) != "":
        SUSPENDE_SEND = True

        zera_tentativas_core()

        # Mostramos a tela de loading, antes de encerrar a aplicacao de imediato
        funcoes_telas.inicia_tela_aguarde()
        time.sleep(1)

        funcoes_viagem.inicia_semaforo()

        funcoes_logs.insere_log("Tela de fechamento iniciada", local, 2)
        
        SUSPENDE_CORE_FECHAMENTO = True
        time.sleep(1)

        funcoes_logs.insere_log("Chamando tela Fechamento da viagem", local,2)
        os.system("sudo pkill -9 -f core.py")
        
        os.system("sudo python3 /home/pi/caixa-magica/core/telaFechamento.py " + str(barcode))
        funcoes_logs.insere_log("Executada telaFechamento.py", local,2)

        time.sleep(2)
    return

def send_qrcode(id_web, qrcode):
    global SUSPENDE_SEND

    if SUSPENDE_SEND:
        return

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'qrcode',
                'contaid': id_web,
                'qrcode': qrcode,
                'var_sessao':''
            }

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.connect((HOST_CORE, PORT_CORE))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            s.shutdown(socket.SHUT_RDWR)
            s.close()

            zera_tentativas_core()
        funcoes_logs.insere_log("QR Code detectado - id_web enviado para o core", local)
    except Exception as e:
        atualiza_tentativas_core()
        funcoes_logs.insere_log("Erro ao enviar QR Code para o core", local)
global veiculo
veiculo = ""

# motorista.json
funcoes_logs.insere_log("Obtendo dados do motorista da viagem (motorista.json)", local)
try:
    with open(path_atual + "/../../caixa-magica-operacao/motorista.json", "r") as json_data:
        dados_motorista = json.load(json_data)

        nome_motorista = dados_motorista['nome']
        id_qrcode_motorista = dados_motorista['id_qrcode']
except Exception as e:
    funcoes_logs.insere_log("Erro ao abrir 'motorista.json' em 'tela_principal.py': " + str(e), local)

# Rotina usada para capturar as imagens
def captura():
   global LAST_IMAGE
   global MATAR_THREAD
   global LAST_IMAGE_TS
   global LAST_IMAGE_LIDA
   FPS = 30

   arquivo_log = funcoes_logs.determina_nome_log("camera")

   # Obtemos a camera a ser utilizada
   try:
        with open(path_atual + "/../../caixa-magica-vars/config.json", "r") as json_data_aux:
           aux = json.load(json_data_aux)
           camera_cv2 = aux['camera_cv2']
           tela_x_inicio = aux["tela_x_inicio"]
           tela_x_final = aux["tela_x_final"]
           tela_y_inicio = aux["tela_y_inicio"]
           tela_y_final = aux["tela_y_final"]
           funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Usando camera de config.json: " + str(camera_cv2) )
   except Exception as e:
        camera_cv2 = 0
        funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Usando camera generica de: " + str(camera_cv2) )

   # Checa se foi colocada uma camera para testes
   camera_testes = funcoes_camera.get_camera_testes()

   if camera_testes != "":
       funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Usando camera de  testes: " + str(camera_testes) )
       camera_cv2 = camera_testes

   # Inicia a camera
   if camera_testes == "":
       funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Iniciando VideoCapture")
       cap = cv2.VideoCapture(camera_cv2)
       cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
       cap.set(cv2.CAP_PROP_FPS, FPS)

   while 1:
       try:
           ret, frame = cap.read()
           LAST_IMAGE = frame
           LAST_IMAGE_TS = time.time()#datetime.utcnow()
           funcoes_camera.atualiza_status_camera(True)

           while ret:
               if MATAR_THREAD:
                   return

               ret, frame = cap.read()
               if camera_cv2 != 0:
                   frame = frame[tela_x_inicio:tela_x_final, tela_y_inicio:tela_y_final]
                   #frame = frame[70:300,130:330]

               LAST_IMAGE = frame
               LAST_IMAGE_TS = time.time()#datetime.utcnow()
               LAST_IMAGE_LIDA = time.time()

           funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Reconectando camera..." )
           cap = cv2.VideoCapture(camera_cv2)
           cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
           cap.set(cv2.CAP_PROP_FPS, FPS)

       except Exception as e:
           funcoes_camera.atualiza_status_camera(False)
           funcoes_logs.registra_linha_log_arquivo(arquivo_log, "Reconectando camera..." + (str(e)) )
           cap = cv2.VideoCapture(camera_cv2)
           cap.set(cv2.CAP_PROP_BUFFERSIZE,1)
           cap.set(cv2.CAP_PROP_FPS, FPS)
           time.sleep(0.05)
           continue

# Rotina de leitura das capturas
def leitura():
    global MATAR_THREAD
    global GLOBAL_EXIBE_MOLDURA
    global HAAR_X
    global HAAR_Y
    global HAAR_H
    global HAAR_W
    global LAST_IMAGE_LIDA
    global MENSAGEM_PROCESS
    global LAST_IMAGE
    global STATUS_QR
    global STATUS_NFC
    global STATUS_INTERNET
    global STATUS_ES
    global VAL_SONAR
    global LAMBDA_DISPLAY
    global GLOBAL_TEMPERATURA_CPU

    local_exibe_tela = False

    camera_testes = funcoes_camera.get_camera_testes()
    nome =  tratar_palavra(nome_motorista)

    while True:
        delay_haar = 0

        try:
            if MATAR_THREAD:
                break               

            data_hora = datetime.now()
            data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")
            image = LAST_IMAGE

            size_fonte_hora = 0.8
            espessura_fonte_hora = 2
            size_fonte_resp = 0.6
            espessura_fonte_resp = 2
            pos_y_resp = 680#620
            pos_y_sentido = 710
            size_fonte_core = 0.6
            size_fonte_serial = 0.8
            espessura_fonte_serial = 2

            # Mostra o status da internet        
            cv2.putText(image, str(STATUS_INTERNET), (505,25),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            cv2.putText(image, time.strftime("%d/%m/%Y - %H:%M:%S"), (25,60),cv2.FONT_HERSHEY_SIMPLEX, size_fonte_hora, (0, 0, 255), espessura_fonte_hora)
            cv2.putText(image, "Serial: " + str(serial_id), (25,25),cv2.FONT_HERSHEY_SIMPLEX, size_fonte_serial, (0, 0, 255), espessura_fonte_serial)

            if camera_testes == "":
                dist = sonar.distance() # em cm
            else:
                dist = config['rec_facial']['max_dist_sonar'] - 1

            if dist < config['rec_facial']['max_dist_sonar'] and dist > config['rec_facial']['min_dist_sonar']:
                pass
            else:
                cv2.putText(image, "Resp: "+nome, (15,pos_y_resp), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_resp, (0, 0, 255), espessura_fonte_resp)
                cv2.putText(image, "Sentido: "+ GLOBAL_SENTIDO, (15,pos_y_sentido), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_resp, (0, 0, 255), espessura_fonte_resp)
                cv2.putText(image, "Core: " + str(CORE_STATUS) + " (" + version + ")", (240,pos_y_sentido), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_core, (0, 0, 255), espessura_fonte_resp)

                #v2.putText(image, str(LAMBDA_DISPLAY) +" "+ str(VAL_SONAR), (15,pos_y_sentido+55), cv2.FONT_HERSHEY_SIMPLEX, (size_fonte_core - 0.3), (255, 255, 255), 1 )

                # Se o Elastic Search nao esta disponivel
                if STATUS_ES != "ON":
                    cv2.putText(image, "LEITORA FACIAL INDISPONIVEL.", (15,pos_y_resp-73), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_core, (0, 0, 255), espessura_fonte_resp)

                # Se o leitor de QR Code nao esta disponivel
                mensagem_leitor_indisp = ""
                if STATUS_QR == "ON" and STATUS_NFC == "ON":
                    pass
                elif STATUS_QR == "OFF" and STATUS_NFC == "ON":
                    mensagem_leitor_indisp = "LEITOR QR CODE INDISPONIVEL."
                elif STATUS_QR == "ON" and STATUS_NFC == "OFF":
                    mensagem_leitor_indisp = "LEITOR NFC INDISPONIVEL."
                else:
                    mensagem_leitor_indisp = "LEITORES QR CODE/NFC INDISPONIVEIS."

                if mensagem_leitor_indisp != "":
                    cv2.putText(image, mensagem_leitor_indisp, (15,pos_y_resp-30), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_core, (0, 0, 255), espessura_fonte_resp)

            # Fim trecho modificado em 16/08/2023

            if not local_exibe_tela:
                cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                local_exibe_tela = True

                cv2.imshow("Frame", image)
                time.sleep(1)

                # Elimina tela de aguarde, caso esteja ativa
                funcoes_telas.kill_tela_aguarde()
            else:
                cv2.putText(image, MENSAGEM_PROCESS, (25,105), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_core, (255, 0, 0), espessura_fonte_resp)                        
                cv2.imshow("Frame", image)

            cv2.waitKey(30)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except Exception as e:
            time.sleep(1)

# Rotina que faz a leitura de um NFC a partir do coletado pelo leitor dedicado (Thread)
def interpreta_nfc_leitora():
    path = funcoes_nfc.get_local_json()

    while 1:
        try:
            nfc = funcoes_nfc.valor_nfc_json()

            if nfc != "":
                processaNFC(nfc)
                funcoes_nfc.reset_json()
        except Exception as e:
            pass

# Rotina que faz a leitura de um qrcode a partir do coletado pelo leitor dedicado (Thread)
def interpreta_qrcode_leitora():
    path = funcoes_qrcode.get_local_json()

    while 1:
        try:
            qrcode = funcoes_qrcode.valor_qrcode_json()

            if qrcode != "":
                processaQR(qrcode)
                funcoes_qrcode.limpa_qrcode()
        except Exception as e:
            pass
        time.sleep(0.1)        

# rotina que faz a leitura de um qr code a partir da foto capturada (Thread)
def interpreta_qrcode():
    global LAST_IMAGE

    while 1:
        try:
            image = cv2.flip(LAST_IMAGE, 1)
            #image = LAST_IMAGE
            #image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #image = image[70:300,130:330]
            
            #print(image.shape)
            #scale_resize = 40
            #width_resize = int(image.shape[1] * scale_resize / 100)
            #height_resize = int(image.shape[0] * scale_resize / 100)
            #dim = (width_resize, height_resize)
            #image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
            #print(image.shape)

            leitura_qrcode_feita = False
            barcodes = pyzbar.decode(image)
            #print("Barcodes: " + str(barcodes))

            for barcode in barcodes:
                leitura_qrcode_feita = True

                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                if barcodeData != "":
                    processaQR(barcodeData)
                    funcoes_qrcode.limpa_qrcode()
        except Exception as e:
            time.sleep(0.1)
            pass
        time.sleep(0.01)

# Interpreta o conteudo oriundo de um leitor NFC
def processaNFC(nfc):
    try:
        # Se o semaforo estiver ativo, quer dizer que tem algum processamento facial ou de QR Code.
        # Neste caso, travar as demais acoes
        if funcoes_viagem.semaforo_ativo():
            return

        # Se a chave NFC nao conseguiu ser lida na origem (ex: erro de leitura ou sem propriedade TEXT)
        # Emitimos uma sinalizacao de erro
        if "NAOENCONTRADO" in nfc:
            cfgTelas("red2", "white", "Chave NFC\n\nnão identificada", "", 200, 3000, 32, "red2")
            return

        funcoes_logs.insere_log("Decodificando NFC " + str(nfc), local)

        nfc_code_expirado = False
        faz_cadastro_conta = False
        nfc_code_invalido = False

        # Se o NFC possui hashtag no inicio, entao temos um qr code modelo novo
        faz_cadastro_conta = True

        # Checamos se o NFC possui um token considerado valido
        nfc_decrypt = str(nfc)
        nfc_valido = funcoes_nfc.checaTokenNFC(nfc, GLOBAL_EXPIRACAO_QRCODE)

        if nfc_valido == "INVALIDO":
            nfc_code_invalido = True
        elif nfc_valido == "EXPIRADO":
            nfc_code_expirado = True
        else:
            conta_id = ""
            saldo_id_web = ""
            saldo_conta = ""
            nome_conta = ""
            mensagem_erro = ""
            valores_base_64 = funcoes_nfc.desmembraNFCVars(str(nfc))

            conta_id = valores_base_64[1]
            saldo_conta = valores_base_64[2]
            mensagem_erro = valores_base_64[3]
            saldo_id_web = ""

        if not nfc_code_expirado and not nfc_code_invalido:
            # Checamos se o NFC ja foi utilizado dentro desta caixa magica
            if funcoes_nfc.check_nfc_utilizado(nfc) == True:
                funcoes_viagem.inicia_semaforo()
                cfgTelas("red2", "white", "Chave NFC\n\njá utilizada", "", 200, 3000, 32, "red2")
                funcoes_logs.insere_log("Chave NFC ja utilizada, cobranca nao permitida: "+ str(barcodeData), local)
                funcoes_viagem.remove_semaforo()
            elif mensagem_erro != "":
                cfgTelas("red2", "white", mensagem_erro, "", 250, 3000, 32, "red2")
            else:
                # Se devemos checar o cadastro da conta, rodamos este trecho
                if faz_cadastro_conta:
                    funcoes_nfc.cadastra_conta_nfc(conta_id, nome_conta, saldo_conta)

                #Envia o ID WEB lido do NFC
                funcoes_logs.insere_log("NFC detectado - enviando para o core", local)
                send_qrcode(conta_id, nfc)
        elif nfc_code_invalido:
            funcoes_viagem.inicia_semaforo()
            cfgTelas("red2","white","Chave NFC\n\nInvalida","",200,3000,32,"red2")
            funcoes_logs.insere_log("Chave NFC Invalida: " + str(nfc), local)
            funcoes_viagem.remove_semaforo()
        else:
            funcoes_viagem.inicia_semaforo()
            cfgTelas("red2","white","Chave NFC\n\nExpirada","",200,3000,32,"red2")
            funcoes_logs.insere_log("Chave NFC Expirada: " + str(nfc), local)
            funcoes_viagem.remove_semaforo()

    except Exception as e:
        print(str(e))

# Interpreta o conteudo oriundo de um QR Code
def processaQR(barcodeData):
    try:
        # Se o semaforo estiver ativo, quer dizer que tem algum processamento facial ou de QR Code.
        # Neste caso, travar as demais acoes
        if funcoes_viagem.semaforo_ativo():
            return

        interrompe_viagem = False

        # Se for um qrcode para forcar reboot
        if barcodeData == "REBOOT_VALIDADOR":
            os.system("sudo reboot -f")

        # Se o qr code for o do motorista, encerra viagem
        if barcodeData == id_qrcode_motorista:  
            interrompe_viagem = True
            funcoes_logs.insere_log("QR Code do motorista informado", local)

        # mas se o qr code for do fiscal, tambem encerra viagem
        elif funcoes_qrcode.check_fiscal(barcodeData) == True:
            interrompe_viagem = True
            funcoes_logs.insere_log("QR Code do fiscal informado", local)

        # se identificada uma tentativa de encerramento de viagem
        if interrompe_viagem:
            # Se estiver parametrizado para informar a viagem
            # Chama tela de escolha no encerramento
            if funcoes_viagem.informe_sentido_habilitado():
                funcoes_logs.insere_log("Chamando tela confirmacao encerramento viagem", local)

                tela_confirma_encerramento_viagem(barcodeData)
            # caso contrario, ja vai direto pra tela de encerramento (sem perguntar nada ao motorista)
            else:
                funcoes_logs.insere_log("Entrando direto na tela de encerramento da viagem", local)
                encerrarViagem(barcodeData)

        else:
            # Se o semaforo estiver ativo, quer dizer que tem algum processamento facial ou de QR Code.
            # Neste caso, travar as demais acoes
            if funcoes_viagem.semaforo_ativo():
                return

            funcoes_logs.insere_log("Decodificando Qr Code " + str(barcodeData), local)

            qr_code_expirado = False
            faz_cadastro_conta = False
            qr_code_invalido = False

            # Se o qr code possui hashtag no inicio, entao temos um qr code modelo novo
            faz_cadastro_conta = True

            # Checamos se o QR Code possui um token considerado valido
            qrcode_decrypt = str(barcodeData)
            qr_valido = funcoes_qrcode.checaTokenQrCode(barcodeData, GLOBAL_EXPIRACAO_QRCODE)
            
            if qr_valido == "INVALIDO":
                qr_code_invalido = True
            if qr_valido == "EXPIRADO":
                qr_code_expirado = True
            else:
                conta_id = ""
                saldo_id_web = ""
                saldo_conta = ""
                nome_conta = ""
                mensagem_erro = ""
                valores_base_64 = funcoes_qrcode.desmembraQrCodeVars(str(barcodeData))
                    
                conta_id = valores_base_64[1]
                saldo_conta = valores_base_64[2]
                mensagem_erro = valores_base_64[3]
                saldo_id_web = ""

            if not qr_code_expirado and not qr_code_invalido:
                # Checamos se o qrcode ja foi utilizado dentro desta caixa magica
                if funcoes_qrcode.check_qrcode_utilizado(barcodeData) == True:
                    funcoes_viagem.inicia_semaforo()
                    cfgTelas("red2", "white", "QR Code\n\njá utilizado", "", 200, 3000, 32, "red2")
                    funcoes_logs.insere_log("QR Code ja utilizado, cobranca nao permitida: "+ str(barcodeData), local)
                    funcoes_viagem.remove_semaforo()
                elif mensagem_erro != "":
                    cfgTelas("red2", "white", mensagem_erro, "", 250, 3000, 32, "red2")
                else:
                    # Checamos aqui se o qr code da pessoa seria da mesma pessoa que abriu a viagem
                    if funcoes_viagem.checkClienteMotoristaViagem(conta_id,conn) == True:
                        funcoes_viagem.inicia_semaforo()
                        cfgTelas("red","white", "Ação\nnão permitida", "", 200, 3000, 32, "red")
                        funcoes_logs.insere_log("Tentativa de passagem de QR Code do motorista como cliente: conta id " + str(conta_id), local)
                        funcoes_viagem.remove_semaforo()
                    else:
                        # Se devemos checar o cadastro da conta, rodamos este trecho
                        if faz_cadastro_conta:
                            print("Conta: " + str(conta_id) + " " + nome_conta + " " + str(saldo_conta))
                            funcoes_qrcode.cadastra_conta_qrcode(conta_id, nome_conta, saldo_conta)

                        #Envia o ID WEB lido do QRCode
                        funcoes_logs.insere_log("QR Code detectado - enviando para o core", local)
                        send_qrcode(conta_id, barcodeData)
            elif qr_code_invalido:
                funcoes_viagem.inicia_semaforo()
                cfgTelas("red2","white","QR Code\n\nInvalido","",200,3000,32,"red2")
                funcoes_logs.insere_log("QR Code Invalido: " + str(barcodeData), local)
                funcoes_viagem.remove_semaforo()
            else:
                funcoes_viagem.inicia_semaforo()
                cfgTelas("red2","white","QR Code\n\nExpirado","",200,3000,32,"red2")
                funcoes_logs.insere_log("QR Code Expirado: " + str(barcodeData), local)
                funcoes_viagem.remove_semaforo()
    except Exception as e:
        print(str(e))


# rotina que faz a leitura facial da foto capturada (Thread)
def interpreta_foto():
    global LAST_IMAGE
    global LAST_IMAGE_TS
    global unique_filename
    global HAAR_X
    global HAAR_Y
    global HAAR_H
    global HAAR_W
    global STATUS_ES
    global LAMBDA_DISPLAY

    # Obtemos se eh uma camera teste ou nao
    camera_testes = funcoes_camera.get_camera_testes()

    while 1:
        LAMBDA_DISPLAY = 0

        # Se o Elastic Search nao estiver no ar, nem processamos
        if STATUS_ES != "ON":
            continue

        # Se ainda esta em status de processamento da cobranca
        if funcoes_camera.get_status_cobranca():
            continue
            
        var_sessao = str(time.time())

        try:
            image = cv2.flip(LAST_IMAGE,1)
            image_sem_moldura = image

            funcoes_core.atualiza_mensagem_process("")
            fraude = False
            lamb = 0

            # Para todos os casos, a distancia do sonar deve estar dentro do intervalo
            # Quando se esta utilizando uma camera testes, o sonar devera ser ignorado
            if camera_testes == "":
                dist = sonar.distance() # em cm
            else:
                dist = config['rec_facial']['max_dist_sonar'] - 1

            if dist < config['rec_facial']['max_dist_sonar'] and dist > config['rec_facial']['min_dist_sonar']:
                # Cenario 1: imagem ereta
                gray= cv2.cvtColor(image_sem_moldura, cv2.COLOR_BGR2GRAY)
                
                faces = []
                local_scale_factor = GLOBAL_SCALE_FACTOR
                faces = capturaHaar(gray, local_scale_factor, GLOBAL_MIN_NEIGH, GLOBAL_MENSAGEM_FACE, image)

                # Se nao capturou a imagem
                if len(faces) <= 0:
                    # Cenario 2: inclinacao direita
                    if GLOBAL_GRAUS_INCLINACAO_DIREITA > 0:
                        imgRotate = rotateImage(image_sem_moldura, GLOBAL_GRAUS_INCLINACAO_DIREITA)
                        gray= cv2.cvtColor(imgRotate, cv2.COLOR_BGR2GRAY)
                        faces = capturaHaar(gray, local_scale_factor, GLOBAL_MIN_NEIGH, GLOBAL_MENSAGEM_FACE, image)

                # Se nao capturou a imagem
                if len(faces) <= 0:
                    # Cenario 3: inclinacao esquerda
                    if GLOBAL_GRAUS_INCLINACAO_ESQUERDA > 0:
                        imgRotate = rotateImage(image_sem_moldura, GLOBAL_GRAUS_INCLINACAO_ESQUERDA)
                        gray= cv2.cvtColor(imgRotate, cv2.COLOR_BGR2GRAY)
                        faces = capturaHaar(gray, local_scale_factor, GLOBAL_MIN_NEIGH, GLOBAL_MENSAGEM_FACE, image)

                lamb = 0
                mensagemNota = ""
               
                # Primeiro, ordenamos em cada face pela altura (height)
                faces_aux = []
                for (x, y, w, h) in faces:
                    faces_aux_interna = []
                    faces_aux_interna.append((x,y,w,h))
                    faces_aux_interna.append(h)
                    faces_aux.append(faces_aux_interna)

                # Das faces encontradas, elegemos a de MAIOR ALTURA como a que deve ser analisada
                cnt_indice = 0
                maior_altura = 0
                
                faces_usar = []
                for faces_analise in faces_aux:
                    if faces_analise[1] > maior_altura:
                        maior_altura = faces_analise[1]
                        faces_usar = []
                        faces_usar.append(faces_analise[0])
                    cnt_indice = cnt_indice+1

                # Determina a maior face como a da analise
                faces = faces_usar

                if len(faces) <= 0:
                    arrUltimosEAR = []

                #print("Faces:" + str(faces))

                # Analisa casa face identificada
                # Se uma delas supostamente atendeu requisitos, avancamos e ignoramos as demais faces
                for (x, y, w, h) in faces:
                    mensagemNota=""
                    HAAR_X = x
                    HAAR_Y = y
                    HAAR_W = w
                    HAAR_H = h

                    unique_filename = config['recog']['path'] + str(uuid.uuid4()) + ".jpg"
                    lamb = dist * h / 0.3
                    LAMBDA_DISPLAY = lamb

                    # Checa se o rosto captado esta menor do que o esperado
                    if (w < config['rec_facial']['min_width_face'] and h < config['rec_facial']['min_height_face']):
                        mensagemNota = "FACE PEQUENA, APROXIME MAIS"

                    # Caso a pessoa esteja longe
                    elif (dist > config['rec_facial']['max_dist_sonar']):
                        mensagemNota = "APROXIME MAIS"

                    # Caso a pessoa esteja perto demais
                    elif (dist < config['rec_facial']['min_dist_sonar']):
                        mensagemNota = "AFASTE UM POUCO"

                if mensagemNota != "":
                    faces = []
                    mensagemNota = mensagemNota
                    funcoes_core.atualiza_mensagem_process(mensagemNota)

                if (lamb < config['rec_facial']['min_lambda']):
                    fraude = True
                else:
                    im = cv2.resize(gray[y-50:y+h+50, x-15:x+w+15], (120,120))

                if (len(faces) > 0 and fraude == False):
                    funcoes_core.atualiza_mensagem_process("")
                    cv2.imwrite(unique_filename, im)
                 
                    SEMAFORO_ENVIA_CORE = False

                    # Se a checagem de prova de vida dos olhos estiver ligada
                    if BLINK_OLHOS_VALIDACAO == False:
                        SEMAFORO_ENVIA_CORE = True
                    else:
                        imagem_blink = cv2.imread(unique_filename)
                        rects = detector(imagem_blink, 0)
                        
                        if len(rects) <= 0:
                            ear = 0
                            ear_ant=0
                            arrUltimosEAR = []

                        for rect in rects:
                            shape = predictor(imagem_blink, rect)
                            shape = face_utils.shape_to_np(shape)
                            leftEye = shape[lStart:lEnd]
                            rightEye = shape[rStart:rEnd]

                            leftEAR = funcoes_prova_vida_olhos.eye_aspect_ratio(leftEye)
                            rightEAR = funcoes_prova_vida_olhos.eye_aspect_ratio(rightEye)
                            ear = (leftEAR + rightEAR) / 2.0

                            if len(arrUltimosEAR) < BLINK_OLHOS_LIMITE_EAR:
                                arrUltimosEAR.append(ear)
                            else:
                                while len(arrUltimosEAR) >= BLINK_OLHOS_LIMITE_EAR:
                                    # remove o primeiro item do array (o mais antigo)
                                    arrUltimosEAR.pop(0)

                            if len(arrUltimosEAR) <= BLINK_OLHOS_LIMITE_EAR and len(arrUltimosEAR) > 1:
                                if min(arrUltimosEAR) <= BLINK_OLHOS_MIN_EAR and max(arrUltimosEAR) >= BLINK_OLHOS_MAX_EAR:
                                    print("PISCOU")

                                    print("Array EAR: " + str(arrUltimosEAR))
                                    print(BLINK_OLHOS_MAX_EAR)
                                    print("Min: " + str(min(arrUltimosEAR)) + ", Max: " + str(max(arrUltimosEAR)) )

                                    aux_min_ear = min(arrUltimosEAR)
                                    aux_max_ear = max(arrUltimosEAR)

                                    SEMAFORO_ENVIA_CORE = True
                                    arrUltimosEAR = []
                                    break
                                else:
                                    print("NAo PISCOU")
                                    print("Array EAR: " + str(arrUltimosEAR))

                                if len(arrUltimosEAR) == BLINK_OLHOS_LIMITE_EAR:
                                    arrUltimosEAR = []

                    if SEMAFORO_ENVIA_CORE == True:
                        funcoes_core.atualiza_mensagem_process("ROSTO ENQUADRADO, AGUARDE... ")
                        send(unique_filename, var_sessao)

        except Exception as e:
            time.sleep(0.05)

# Thread que controla a mensagem de tela de processamento
def atualiza_mensagem_process():
    global MENSAGEM_PROCESS

    funcoes_core.zera_mensagem_process()

    while 1:
        try:
            MENSAGEM_PROCESS = funcoes_core.obtem_mensagem_process()
        except:
            pass
        time.sleep(0.2)

# Thread que controla o status do core
def atualiza_status_core():
    global CORE_STATUS
    global SUSPENDE_SEND
    global SUSPENDE_CORE_FECHAMENTO

    while 1:
        if SUSPENDE_CORE_FECHAMENTO:
            time.sleep(5)
            continue
        try:
            CORE_STATUS = funcoes_core.obtem_status_core()

            if CORE_STATUS == "OFF":
                SUSPENDE_SEND = True
                cfgTelas("red2", "white", "Core\nindisponivel\n\nUtilize o leitor\nQR Code.","", 250, 10000, 25, "red2")
                SUSPENDE_SEND = False
        except:
            time.sleep(0.05)
        time.sleep(2)

# Thread que controla o numero de tentativas atuais de acesso ao core
def check_tentativas_core():
    global NUM_TENTATIVAS_FAIL_CORE
    global SUSPENDE_SEND

    while 1:
        time.sleep(0.5)
        try:

            # Se o numero de tentativas passou de X, entao matamos o processo core
            # para que ele seja reiniciado por seu monitor
            if NUM_TENTATIVAS_FAIL_CORE > 20:
                SUSPENDE_SEND = True
                funcoes_core.zera_status_core()
                os.system("sudo pkill -9 -f core.py")
                time.sleep(10)
                zera_tentativas_core()
                SUSPENDE_SEND = False
        except:
            SUSPENDE_SEND = False
            pass

# Thread que controla o status da placa principal
def atualiza_status_placa():
    global PLACA_STATUS
    global SUSPENDE_SEND

    while 1:
        try:
            PLACA_STATUS = funcoes_core.obtem_status_placa()

            if PLACA_STATUS == "OFF":
                SUSPENDE_SEND = True
                cfgTelas("red2", "white", "Controladora\nindisponivel\n\nAguarde...","", 250, 3000, 25, "red2")
                SUSPENDE_SEND = False
        except:
            time.sleep(0.1)
        time.sleep(2)

# Thread que testa o status do streaming da camera
def check_status_camera():
    global LAST_IMAGE_LIDA
    global STATUS_QR
    global SUSPENDE_CORE_FECHAMENTO

    timeout = 5
    time.sleep(timeout)

    # Se a camera de testes estiver configurada, nao efetuamos o check
    camera_testes = funcoes_camera.get_camera_testes()
    if camera_testes != "":
        return

    while 1:
        time.sleep(1)
        if SUSPENDE_CORE_FECHAMENTO:
            time.sleep(1)
            continue

        # Caso esteja ainda em processamento da cobranca
        if funcoes_camera.get_status_cobranca():
            time.sleep(1)
            continue

        try:
            time_limit = LAST_IMAGE_LIDA + timeout

            if time.time() > time_limit:
                funcoes_camera.atualiza_status_camera(False)
                SUSPENDE_SEND = True

                # Mensagem de notificacao
                notificacao = "Camera\nindisponivel."

                # Caso a leitora de QR tambem esteja indisponivel
                if STATUS_QR == "ON":
                    notificacao = notificacao + "\n\nUtilize Leitor\nQR Code."
                else:
                    notificacao = notificacao + "\n\nLeitor\nQR Code indisponivel."

                cfgTelas("red2", "white", notificacao,"", 200, 10000, 25, "red2")
                SUSPENDE_SEND = False
            else:
                funcoes_camera.atualiza_status_camera(True)
        except Exception as e:
            print(str(e))
        time.sleep(1)

# Thread que checa o status do leitor QR
def check_status_qr():
    global STATUS_QR

    time.sleep(5)

    while 1:
        time.sleep(1)
        try:
            STATUS_QR = funcoes_qrcode.retorna_status_qrcode()
        except Exception as e:
            pass

# Thread que checa o status do leitor NFC
def check_status_nfc():
    global STATUS_NFC

    time.sleep(5)

    while 1:
        time.sleep(1)
        try:
            if funcoes_nfc.healthcheck():
                STATUS_NFC = "ON"
            else:
                STATUS_NFC = "OFF"
        except Exception as e:
            pass

# Thread que checa o valor atual do sonar
def check_sonar():
    global VAL_SONAR

    time.sleep(1)

    while 1:
        try:
            VAL_SONAR = sonar.distance()
        except:
            VAL_SONAR = -1

# Thread que checa o status do Elastic Search
def check_elastic_on():
    global STATUS_ES

    time.sleep(5)

    while 1:
        try:
            STATUS_ES = funcoes_elastic.check_elastic_on()
            if STATUS_ES == True:
                STATUS_ES = "ON"
            else:
                STATUS_ES = "OFF"
        except Exception as e:
            pass
        time.sleep(1)

# Thread que checa o status da internet periodicamente
def check_status_internet():
    global STATUS_INTERNET

    while 1:
        try:
            STATUS_INTERNET = funcoes_internet.get_status_internet()
        except Exception as e:
            pass
        time.sleep(5)

# Thread que checa a necessidade de eliminacao periodica do arquivo de matrizs
def check_exclui_arquivo_matrizes():
    while 1:
        try:
            funcoes_matrizes_memoria.elimina_arquivo_matrizes()
        except:
            pass
        time.sleep(0.1)

# Thread que pega a temperatura da Maquina
def pega_temperatura_cpu():
    global GLOBAL_TEMPERATURA_CPU

    while 1:
        try:
            funcoes_temperatura.getTemperature()
            GLOBAL_TEMPERATURA_CPU = funcoes_temperatura.getTemperatureJSON()
        except:
            pass
        time.sleep(5)

# Zera o arquivo de matrizes
funcoes_matrizes_memoria.cria_arquivo_matrizes()

t0 = threading.Thread(target=check_exclui_arquivo_matrizes)
t1 = threading.Thread(target=captura)
t2 = threading.Thread(target=leitura)
t3 = threading.Thread(target=interpreta_foto)
t4 = threading.Thread(target=interpreta_qrcode)
t5 = threading.Thread(target=interpreta_qrcode_leitora)
t6 = threading.Thread(target=atualiza_mensagem_process)
t7 = threading.Thread(target=atualiza_status_core)
t8 = threading.Thread(target=check_tentativas_core)
t9 = threading.Thread(target=atualiza_status_placa)
t10 = threading.Thread(target=check_status_camera)
t11 = threading.Thread(target=check_status_qr)
t12 = threading.Thread(target=check_status_internet)
t13 = threading.Thread(target=check_elastic_on)
t14 = threading.Thread(target=check_sonar)
t15 = threading.Thread(target=interpreta_nfc_leitora)
t16 = threading.Thread(target=check_status_nfc)
t17 = threading.Thread(target=pega_temperatura_cpu)

t0.start()
t12.start()
t13.start()
t6.start()

time.sleep(2)
t1.start()
t2.start()

time.sleep(1)
t4.start()
t5.start()

# Aguarda alguns segundos para iniciar o processo de reconhecimento da foto
time.sleep(5)
t3.start()
t7.start()
t8.start()
t9.start()
t10.start()
t11.start()
t14.start()
t15.start()
t16.start()
t17.start()

# Grava na base de dados o sentido optado na viagem
def gravaSentidoViagem():
    funcoes_logs.insere_log("Entrando em gravaSentidoViagem()", local)
    
    sentido = "IDA"

    #viagemId = funcoes_viagem.get_viagem_atual()
    funcoes_logs.insere_log("Obtendo sentido do arquivo sentido_informado_mtorista.json", local)
    try:
        with open(path_atual + '/../../caixa-magica-operacao/sentido_informado_motorista.json') as json_data:
            aux = json.load(json_data)
            sentido = aux['sentido']
            funcoes_logs.insere_log("Sentido obtido: " + sentido, local)
    except:
        funcoes_logs.insere_log("Sentido padrao adotado: "+ sentido, local)

    # Insere o sentido da viagem
    funcoes_logs.insere_log("Gravando sentido da viagem atual", local)
    funcoes_viagem.gravaSentido(sentido)
    funcoes_logs.insere_log("Sentido gravado", local)

# Obtem o sentido da viagem
def pegaSentidoJson():
    global GLOBAL_SENTIDO
    
    # Le o arquivo de sentido da viagem
    while True:
        try:
            with open(path_atual + "/../../caixa-magica-operacao/sentido_informado_motorista.json") as json_sv:
                aux = json.load(json_sv)
                GLOBAL_SENTIDO = aux['sentido']
                del aux
        except Exception as e:
            GLOBAL_SENTIDO = 'VOLTA'

        time.sleep(2)

def tela_confirma_encerramento_viagem(barcode):
   funcoes_tela_corrente.registraTelaAtual("TELA_SENTIDO_CONFIRMA_ENCERRAMENTO")

   root2 = tk.Tk()
   style = ttk.Style(root2)
   root2.update()
   root2.deiconify()
   root2.configure(background = "white")
   root2.attributes("-fullscreen",True)
   fonte = ('Courier','32','bold')
   width_botao = 22

   fonte2 = ("Arial 26 bold")
   root2.verif2 = Message(root2, text = "\nInforme a ação a realizar nesta viagem:\n", font=fonte2, bg='white')
   root2.verif2['width'] = '420'
   root2.verif2['justify'] = CENTER
   root2.verif2.pack(side = 'top')
   root2.l0 = Label(root2)
   root2.l0['text'] = ''
   root2.l0.configure(bg='white', activebackground='white')
   root2.l0.pack(side='top', padx=30)

   root2.butt_1 = Button(root2, command = lambda:[encerrarViagem(barcode), root2.destroy(), root2.quit()])
   root2.butt_1['text'] = 'ENCERRAR'
   root2.butt_1['font'] = fonte
   root2.butt_1['height'] = '2'
   root2.butt_1['width'] = width_botao
   root2.butt_1.configure(bg='white', activebackground='white')
   root2.butt_1.pack(side='top', padx = 20)
   root2.l1 = Label(root2)
   root2.l1['text'] = ''
   root2.l1.configure(bg='white', activebackground='white')
   root2.l1.pack(side='top', padx=30)

   root2.butt_2 = Button(root2, command = lambda:[funcoes_viagem.json_sentido_linha('IDA'), gravaSentidoViagem(), root2.destroy(), root2.quit()])
   root2.butt_2['text'] = 'SENTIDO IDA'
   root2.butt_2['font'] = fonte
   root2.butt_2['height'] = '2'
   root2.butt_2['width'] = width_botao
   root2.butt_2.configure(bg='white', activebackground='white')
   root2.butt_2.pack(side='top', padx = 20)
   root2.l2 = Label(root2)
   root2.l2['text'] = ''
   root2.l2.configure(bg='white', activebackground='white')
   root2.l2.pack(side='top', padx=20)

   root2.butt_3 = Button(root2, command = lambda:[funcoes_viagem.json_sentido_linha('VOLTA'), gravaSentidoViagem(), root2.destroy(), root2.quit()])
   root2.butt_3['text'] = 'SENTIDO VOLTA'
   root2.butt_3['font'] = fonte
   root2.butt_3['height'] = '2'
   root2.butt_3['width'] = width_botao
   root2.butt_3.configure(bg='white', activebackground='white')
   root2.butt_3.pack(side='top', padx = 20)
   root2.l3 = Label(root2)
   root2.l3['text'] = ''
   root2.l3.configure(bg='white', activebackground='white')
   root2.l3.pack(side='top', padx=20)

   root2.butt_4 = Button(root2, command = lambda:[root2.destroy(), root2.quit()])
   root2.butt_4['text'] = 'VOLTAR'
   root2.butt_4['font'] = fonte
   root2.butt_4['height'] = '2'
   root2.butt_4['width'] = width_botao
   root2.butt_4.configure(bg='white', activebackground='white')
   root2.butt_4.pack(side='top', padx = 20)
   root2.l3 = Label(root2)
   root2.l3['text'] = ''
   root2.l3.configure(bg='white', activebackground='white')
   root2.l3.pack(side='top', padx=20)

   root2.mainloop()
   return

def encerrarViagem(barcode):
    global MATAR_THREAD
    MATAR_THREAD = True
    global stop_timeout_thread
    stop_timeout_thread = True

    funcoes_logs.insere_log("Parando Thread de Failover Timeout", local)
    send_fechar(barcode)

# Ao abrir, ja grava o sentido inicial informado pelo motorista
gravaSentidoViagem()

##update_sentido = Thread(target = pegaSentidoJson)
##update_sentido.start()

##if GLOBAL_EXIBE_PROPAGANDA:
##    thread_prop = Thread(target=thread_propaganda)
##    thread_prop.start()
