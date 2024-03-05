import os
import time
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/tela"
sys.path.insert(1, path_atual)

os.system("sudo python3 " + path_atual + "/../tela_aguarde.py & ")
os.system("sudo python3 "+ path_atual+ "/../keep_alive.py &")

os.system("sudo pkill -9 -f core.py")
os.system("sudo python3 " + path_atual + "/../core/core.py &")

import subprocess

from tkinter import *
from pyzbar import pyzbar 
import tkinter.ttk as ttk
import dateutil.parser
import cv2
import socket
import sys
import json
import argparse
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

with open(path_atual + "/../version.txt", "r") as f:
    version = f.read()
    f.close()

isRasp = funcoes_serial.getRaspPI()

if isRasp:
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    from RPi import GPIO

import failover
import encrypt
import sonar
import check_mouth
import db
import funcoes_qrcode
import funcoes_logs
import funcoes_viagem
import funcoes_reboot
import funcoes_notif

sys.path.insert(2, path_atual + '/../tela/')
import funcoes_telas
import smtplib, ssl

from PIL import Image, ImageTk
import tkinter as tk
import threading
from itertools import count

import os.path

from imutils.video import FPS
from datetime import datetime, timedelta


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
CORE_STATUS = "OFF"

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

conn = db.Conexao()

global GLOBAL_FILA_IMAGEM

# Elimina fila de imagem
def inicia_fila_imagem():
    global GLOBAL_FILA_IMAGEM
    GLOBAL_FILA_IMAGEM = []

# Cria registro na fila de imagem
def insere_fila_imagem(imagem, dist_sonar):
    global GLOBAL_FILA_IMAGEM

    arrAuxRegistro = []
    arrAuxRegistro.append(datetime.utcnow())
    arrAuxRegistro.append(dist_sonar)
    arrAuxRegistro.append(imagem)
    arrAuxRegistro.append(False)
    GLOBAL_FILA_IMAGEM.append(arrAuxRegistro)
    return

# Rotina que processa imagem
def processa_facial(image, dist):

    try:
        print("Distancia: " + str(dist))
    except:
        pass

    time.sleep(1)

    return False

# Rotina que processa um qr code
def processa_qrcode(image):
    try:
        interrompe_viagem = False

        barcodes = pyzbar.decode(image)
        print("Barcode: " + str(barcodes))
        #time.sleep(0.1)

        for barcode in barcodes:
            (x,y,w,h) = barcode.rect
            cv2.rectangle(image, (x,y), (x+w, y+h),(0, 0, 255),2)
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            # Se for um qrcode para forcar reboot
            if barcodeData == "REBOOT_VALIDADOR":
                os.system("sudo reboot -f")

            if barcodeData == id_qrcode_motorista:
                interrompe_viagem = True
                funcoes_logs.insere_log("QR Code do motorista informado", local)
            elif funcoes_qrcode.check_fiscal(barcodeData) == True:
                interrompe_viagem = True
                funcoes_logs.insere_log("QR Code do fiscal informado", local)

            # Se for identiiicada uma interrupcao na viagem
            if interrompe_viagem:
                # se foi parametrizado para mudar o sentido da viagem
                if funcoes_viagem.informe_sentido_habilitado():
                    funcoes_logs.insere_log("Chamando tela para confirmacao encerramento viagem", local)
                    para_monitor()
                    tela_confirma_encerramento_viagem(barcodeData)
                    inicia_monitor()
                # Caso contrario, ja vai direito para tela de encerramento
                # Sem questionar nada ao motorista
                else:
                    funcoes_logs.insere_log("Entrando direito na tela de encerramento da viagem", local)
                    encerrarViagem(barcodeData)

                return True

            # Mas se nao foi identificado um qr code de motorista e/ou fiscal, analisamos o qr code que deve ser do CLIENTE
            else:
                funcoes_logs.insere_log("Decodificando QR Code " + str(barcodeData), local)
                print("Barcode:" + str(barcodeData))

                # Barcodes Buspay necessariamente iniciam como um "#"
                leu_qr = False
                try:
                    if barcodeData[0:1] == "#":
                        leu_qr = True
                        qrcode_decrypt = str(barcodeData)
                        qr_valido = funcoes_qrcode.checaTokenQrCode(barcodeData, GLOBAL_EXPIRACAO_QRCODE)

                        if qr_valido == "EXPIRADO":
                            qr_code_expirado = True
                        else:
                            conta_id = ""
                            saldo_id_web = ""
                            saldo_conta = ""
                            nome_conta = ""
                            valores_base_64 = funcoes_qrcode.desmembraQrCodeVars(str(barcodeData))
                            conta_id = valores_base_64[1]
                            saldo_conta = valores_base_64[2]
                            saldo_id_web=""

                        if not qr_code_expirado:
                            # Checamos se o qrcode ja foi usado
                            if funcoes_qrcode.check_qrcode_utilizado(barcodeData) == True:
                                cfgTelas("red2", "white", "QR Code\n\njá utilizado", "", 350, 3000, 32, "red2")
                                funcoes_logs.insere_log("QR Code ja utilizado, cobranca nao permitida: " + str(barcodeData), local)
                        
                                # Forcamos o reset da fila de imagens
                                inicia_fila_imagem()
                            else:
                                funcoes_qrcode.cadastra_conta_qrcode(conta_id, nome_conta, saldo_conta)
                                funcoes_logs.insere_log("QR Code detectado, enviando para o core", local)
                                send_qrcode(conta_id, barcodeData)
                        else:
                            cfgTelas("red2", "white", "QR Code Expirado","",350, 3000,32, "red2")
                            funcoes_logs.insere_log("QR Code Expirado: " + str(barcodeData), local)
                    
                            # Forcamos o reset da fila de imagens
                            inicia_fila_imagem()
                    else:
                        leu_qr = False
                except Exception as e:
                    leu_qr = False

                if not leu_qr:
                    cfgTelas("red2", "white", "QR Code\n\nfora do padrão","", 350, 3000, 32, "red2")
                    funcoes_logs.insere_log("QR Code fora do padrao: " + str(barcodeData), local)

                    # Forcamos o reset da fila de imagens
                    inicia_fila_imagem()
        return True
    except Exception as e:
        print(str(e))
        pass

    return False

# Rotina que le a memoria de imagens, e para cada leitura, efetua o delete do array
def processa_fila_imagens():
    global GLOBAL_FILA_IMAGEM

    time.sleep(0.1)

    while True:
        try:
            len_imagens = len(GLOBAL_FILA_IMAGEM)
            print("Tamanho fila: " + str(len_imagens))

            cnt = 0
            while cnt < len_imagens:
                try:
                    # Se a imagem esta na fila como pendente (status FALSE), entramos no processamento de teste
                    # primeiro, checamos se é um qr code. Se nao for, checamos se eh uma face
                    if GLOBAL_FILA_IMAGEM[cnt][3] == False:
                        #print(str(GLOBAL_FILA_IMAGEM[cnt][0]) + " " + str(datetime.utcnow()) )
                        # Processa primeiro o qr code
                        processou = processa_qrcode(GLOBAL_FILA_IMAGEM[cnt][2])
                        
                        # Se nao teve sucesso no qrcode, ai tentamos o facial
                        if not processou:
                            processou = processa_facial(GLOBAL_FILA_IMAGEM[cnt][2], GLOBAL_FILA_IMAGEM[cnt][1])

                        try:
                            # marca item do array para exclusao
                            GLOBAL_FILA_IMAGEM[cnt][3] = True
                        except Exception as e:
                            print(str(e))
                except Exception as e:
                    print(str(e))

                cnt = cnt +1
        except Exception as e:
            print(str(e))

        #print("Dentro fila")

# Rotina que expurga da memoria registros ja processados
def expurga_fila_imagens():
    #return
    global GLOBAL_FILA_IMAGEM

    time.sleep(1)

    while True:
        try:
            len_imagens = len(GLOBAL_FILA_IMAGEM)
            #print("Tamanho: " + str(len_imagens))

            cnt = 0
            try:
                while cnt < len_imagens:
                    if GLOBAL_FILA_IMAGEM[cnt][3] == True:
                        try:
                            del GLOBAL_FILA_IMAGEM[cnt]
                        except Exception as e:
                            print(str(e))
            except Exception as e:
                pass
                #print(str(e))
        
            cnt = cnt +1
        except Exception as e:
            pass
            #print(str(e))


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
    #distancia_permitida = 40
    dist = sonar.distance()
    
    if dist < 0:
        dist = distancia_permitida+1

    # Se a distancia maxima permitida for inferior aquela registrada pelo sonar, entao nao existem objetos proximos
    # assim, podemos ativar a exibicao
    if dist > distancia_permitida:
        # Se ja passou o tempo limite com o sonar distante de alguma pessoa, ai sim permitir a exibicao
        if utc_atual > utc_comparar:
            print("Exibe")
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
        cv2.putText(image, mensagem, (120,65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0),2)
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

def inicia_monitor():
    # Inicia processo monitor de tela
    os.system("sudo python3 " + path_atual + "/../sincronismo/sincronismo_monitor_tela.py &")

def para_monitor():
    os.system("sudo pkill -9 -f sincronismo_monitor_tela.py &")

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
    #msg = Label(widget, text= texto1 + '\n ' + texto2 ,fg=foreground,bg=background,font=('Verdana','36','bold'))
    localString = texto1
    
    if (len(texto2)>0):
        localString +=  '\n ' + texto2
        
    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana',tamanho,'bold'))
    
    msg.grid(row=0,column=1,ipady=ipady)
    root.after(tempo, lambda: root.destroy())
    root.mainloop()

checar_fraude = True
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


#path_skin = path_atual + '/tela_123.png'
path_skin = path_atual + "/tela_moldura.png"
skin = Image.open(path_skin).convert('RGBA')
face_cascade = cv2.CascadeClassifier(PATH_FRONTALFACE)
funcoes_logs.insere_log("CV2 face_cascade instanciado", local)

GLOBAL_EXIBE_NOME_FACIAL = True
GLOBAL_EXIBE_NOME_QRCODE = True
GLOBAL_BGR2GRAY = True

with open(path_atual +'/../../caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)
    HOST_CORE = config['core']['host']
    PORT_CORE = config['core']['port']
    BUFSIZE = config['core']['bufsize']

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


# Rotina teste de envio de pacotes, para checagem se o servico core esta no ar 
def core_healthcheck():
    global CORE_STATUS

    time.sleep(5)
    
    seconds_timeout = 15
    timeout = time.time() + seconds_timeout 

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                data = {
                'type': 'healthcheck'
                }
                
                #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
                s.connect((HOST_CORE, PORT_CORE))
                js = json.dumps(data)
                s.sendall(js.encode('utf-8'))
                data = s.recv(BUFSIZE)
                
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                CORE_STATUS = "ON"

                timeout = time.time() + seconds_timeout
        except Exception as e:
            print("OFF: " + str(e))
            CORE_STATUS = "OFF"
            if time.time() > timeout:
                print("----------------Desligando core.py------------------")
                funcoes_notif.insere_fila_notif("REINICIADO CORE.PY", "Reiniciando via healthcheck telaPrincipal.py")
                os.system("sudo pkill -9 -f core.py")
                time.sleep(0.001)
                os.system("sudo python3 " + path_atual + "/../core/core.py &")
                time.sleep(12)
                timeout = time.time() + seconds_timeout

        time.sleep(10)

# Rotina envia ao core arquivo de imagem, além da matriz facial
def send(file):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'facial',
                'path': file
            }
            #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.connect((HOST_CORE, PORT_CORE))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)

            s.shutdown(socket.SHUT_RDWR)
            s.close()
        #time.sleep(0.1)
    except Exception as e:
        print("erro send file")
        funcoes_logs.insere_log("Erro ao enviar face para o core - " + str(e), local)

def tratar_palavra(palavra):
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = u"".join([c for c in nfkd if not unicodedata.combining(c)])

    return re.sub('[^a-zA-Z0-9 \\\]', '', palavraSemAcento)

def send_fechar(barcode):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'fechar',
                'conta': '',
                'barcode': barcode
            }
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.connect((HOST_CORE, PORT_CORE))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
            data = s.recv(BUFSIZE)
        funcoes_logs.insere_log("QR Code detectado - fechando viagem", local)
    except Exception as e:
        funcoes_logs.insere_log("Erro para fechar viagem, verifique se o server esta up", local)


def send_qrcode(id_web, qrcode):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = {
                'type': 'qrcode',
                'contaid': id_web,
                'qrcode': qrcode
                # 'conta': id_web
            }

            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            s.connect((HOST_CORE, PORT_CORE))
            js = json.dumps(data)
            s.sendall(js.encode('utf-8'))
        #     data = s.recv(BUFSIZE)

            s.shutdown(socket.SHUT_RDWR)
            s.close()
        funcoes_logs.insere_log("QR Code detectado - id_web enviado para o core", local)
    except Exception as e:
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

def showVideo():
    funcoes_logs.insere_log("Iniciando showVideo()", local)
    global veiculo
    global frame
    global rawCapture
    global FRAME
    global vid
    FRAME = 0
    aux = 0

    with open( path_atual + '/../../caixa-magica-vars/config.json') as json_data:
        config = json.load(json_data)

    time.sleep(2)
    global abreviagem_timestamp_principal
    global GLOBAL_SENTIDO

    abreviagem_timestamp_principal = time.time()
    camera_testes = funcoes_camera.get_camera_testes()

    if camera_testes != "":
        camera = None
    else:
        try:
            if isRasp:
                camera = PiCamera()
                camera.resolution = (480, 800)
                camera.framerate = 40
                rawCapture = PiRGBArray(camera, size=(480, 800))
            else:
                width =480
                height=800
                dim = (width, height)
                vid = cv2.VideoCapture(config['camera_cv2'])
                vid.set(cv2.CAP_PROP_FPS, 60)

        except Exception as e:
            funcoes_reboot.restart_cm()

    # allow the camera to warmup
    time.sleep(0.2)

    # capture frames from the camera
    funcoes_logs.insere_log("Iniciando processo de captura do video", local)

    if not isRasp:
        while (True): ##for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            rotina_imagem()
    else:
        if camera_testes == "":
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                rotina_imagem(camera_testes)
        else:
            while True:
                rotina_imagem(camera_testes)

def rotina_imagem(camera_testes):
    global frame
    global FRAME
    global rawCapture
    global vid
    global FILE_QR_TMP
    global serial_id
    global GLOBAL_IMAGEM_PROPAGANDA

    nome =  tratar_palavra(nome_motorista)

    #os.system("sudo touch " + FILE_VIDEO_ALIVE)

    while True:
        exibe_propaganda = permite_exibir_propaganda()

        abreviagem_timestamp_principal = time.time()

        if camera_testes != "":
            vid = cv2.VideoCapture(camera_testes)
            vid.set(cv2.CAP_PROP_FPS, 40)
            ret, frame = vid.read()
            image = frame
        else:
            if isRasp:
                image = frame.array
            else:
                vid.set(cv2.CAP_PROP_POS_FRAMES,0)
                vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                ret, frame = vid.read()
                image = frame
        
        image = cv2.flip(image, 1)
        image_sem_moldura = image

        if not isRasp:
            image = image[0:1024, 150:430]

        cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN) 
        cv2.setWindowProperty("Frame",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

        # Se for pra exibir a propaganda, mostramos a imagem atual
        if exibe_propaganda:
            try:
                print("Exibindo prop")
                #GLOBAL_IMAGEM_PROPAGANDA = "/home/pi/caixa-magica/tela/Spinner-1s-200px.gif"
                if GLOBAL_IMAGEM_PROPAGANDA != "":
                    image = cv2.imread(GLOBAL_IMAGEM_PROPAGANDA)
                    cv2.imshow("Frame",image)
                    key = cv2.waitKey(1) & 0xFF
                    
                    try:
                        rawCapture.truncate(0)
                    except:
                        pass

                    if key == ord("q"):
                        return
            
                    continue
            except Exception as e:
                print("Erro prop: " + str(e))
                pass

        if GLOBAL_EXIBE_MOLDURA:
            pilim = Image.fromarray(image)
            pilim.paste(skin,box=(0,0),mask=skin)
            image = np.array(pilim)

        if isRasp:
            size_fonte_hora = 1
            espessura_fonte_hora = 2
            size_fonte_resp = 1
            espessura_fonte_resp = 2
            pos_y_resp = 740
            pos_y_sentido = 770
            size_fonte_core = 0.5
        else:
            size_fonte_hora = 0.6
            espessura_fonte_hora = 1
            size_fonte_resp = 0.6
            espessura_fonte_resp = 1
            pos_y_resp = 450
            pos_y_sentido = 425
            size_fonte_core = 0.6
        size_fonte_serial = 0.5
        espessura_fonte_serial = 2

        cv2.putText(image, time.strftime("%d/%m/%Y - %H:%M:%S"), (30,43),cv2.FONT_HERSHEY_SIMPLEX, size_fonte_hora, (0, 0, 255), espessura_fonte_hora)
        cv2.putText(image, "Serial: " + str(serial_id), (30,16),cv2.FONT_HERSHEY_SIMPLEX, size_fonte_serial, (0, 0, 255), espessura_fonte_serial)

        cv2.putText(image, "Resp: "+nome, (15,pos_y_resp), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_resp, (0, 0, 255), espessura_fonte_resp)
        cv2.putText(image, "Sentido: "+ GLOBAL_SENTIDO, (15,pos_y_sentido), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_resp, (0, 0, 255), espessura_fonte_resp)
        
        cv2.putText(image, "Core: " + str(CORE_STATUS) + " (" + version + ")", (15,pos_y_sentido+20), cv2.FONT_HERSHEY_SIMPLEX, size_fonte_core, (0, 0, 255), espessura_fonte_resp)

        ENVIADO_CORE = False

        # Para todos os casos, a distancia do sonar deve estar dentro do intervalo
        # Quando se esta utilizando uma camera testes, o sonar devera ser ignorado
        if camera_testes == "":
            dist = sonar.distance() # em cm
        else:
            dist = config['rec_facial']['max_dist_sonar'] - 1

        insere_fila_imagem(image, dist)

        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        if isRasp:
            try:
                rawCapture.truncate(0)
                pass
            except Exception as e:
                print("Erro no rawCapture.truncate(0)")
                pass

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            return

        break


def catraca_timeout():
    funcoes_logs.insere_log("Entrando em catraca_timeout()", local)

    global aux_catraca
    CNT_TENTATIVAS_SOCKET_CATRACAS = 3330000
    NUM_TENTATIVAS_SOCKET_CATRACAS = 0

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp:
                
                tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)   
                tcp.settimeout(0.1)
                tcp.bind(orig_c)
                tcp.listen()
                con, cliente = tcp.accept()
                with con:
                    while True:
                        pkg = con.recv(128)
                        if pkg:
                            data = json.loads(pkg.decode('utf-8'))
                            if(data['catraca'] == True):
                                aux_catraca = False
                        else:
                            break
        except Exception as e:
            funcoes_logs.insere_log("Erro ao abrir socket catracas - " + str(e), local)

def time_failover_principal():
    funcoes_logs.insere_log("Entrando em time_failover_principal()", local)

    global stop_timeout_thread
    timeout = 30
    funcoes_logs.insere_log("Thread de TimeFailOver iniciada", local)
    stop_timeout_thread = False

    while True:
        global abreviagem_timestamp_principal
        time.sleep(4) #para por (4) segundos
        if stop_timeout_thread == True:
            break
        time_limit = abreviagem_timestamp_principal + timeout
        if time.time() > time_limit:
            funcoes_logs.insere_log("Entrando em failover_reboot()", local)
            failover_reboot()

def failover_reboot():
    funcoes_logs.insere_log("Entrando em failover_reboot()", local)
    funcoes_logs.insere_log("TIMEOUT FAIL-OVER ACIONADO! Resetando aplicacao", local)
    
    os.system("sudo sh " + path_atual + "/../../caixa-magica/reboot.sh")

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
    aguarde = funcoes_telas.TelaAguarde()

    global stop_timeout_thread
    stop_timeout_thread = True
    funcoes_logs.insere_log("Parando Thread de Failover Timeout", local)
    #camera_failover.join()
    send_fechar(barcode)

inicia_fila_imagem()

# Ao abrir, ja grava o sentido inicial informado pelo motorista
gravaSentidoViagem()

funcoes_logs.insere_log("Iniciando Thread showVideo", local)
update_video = Thread(target = showVideo)
update_video.start()
funcoes_logs.insere_log("Iniciada Thread showVideo", local)


thread_fila = Thread(target=processa_fila_imagens)
thread_fila.start()

thread_fila_del = Thread(target=expurga_fila_imagens)
thread_fila_del.start()

##core_hc = Thread(target=core_healthcheck)
##core_hc.start()

##update_sentido = Thread(target = pegaSentidoJson)
##update_sentido.start()

if GLOBAL_EXIBE_PROPAGANDA:
    thread_prop = Thread(target=thread_propaganda)
    thread_prop.start()

##inicia_monitor()
