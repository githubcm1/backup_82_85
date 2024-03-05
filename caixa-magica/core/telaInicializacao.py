import os
import sys
import queue

path_atual = "/home/pi/caixa-magica/core/"
sys.path.insert(1, path_atual)

os.system("sudo pkill -9 -f keep_alive.py")
os.system("sudo python3 " + path_atual + "/../keep_alive.py &")

import cv2
from PIL import Image as PilImage
from pyzbar import pyzbar 
import json
import time 

from threading import Thread 
sys.path.insert(1, path_atual +'/../')
from sincronismo import req as sincronismo

sys.path.insert(2, path_atual + '/../tela/')
import funcoes_telas

sys.path.insert(3, path_atual + '/../sincronismo/')
import datetime
import socket

from PIL import Image, ImageTk
from tkinter import *
import threading

sys.path.insert(4, path_atual +'/../tela/')
from tela.AnimatedGIF import *
import funcoes_telas

sys.path.insert(2, path_atual + '/../core/')
import db
import funcoes_logs
import funcoes_serial
import funcoes_camera
import funcoes_tela_corrente
import funcoes_qrcode
import funcoes_internet

global dados
dados = None
global operacao

global LAST_IMAGE_LIDA
LAST_IMAGE_LIDA = time.time() + 10

global STATUS_QR
STATUS_QR = "ON"

global STATUS_INTERNET
STATUS_INTERNET=""

local = 'telaInicializacao.py'

funcoes_logs.insere_log("Abrindo conexao com o BD", local, 2)
conn = db.Conexao()

funcoes_logs.insere_log("Iniciando telas_init.py", local, 2)
os.system("sudo python3 " + path_atual + "/telas_init.py &")

funcoes_logs.insere_log("Iniciando jobs com sincronismo_inicia_jobs.py", local, 2)
os.system("sudo python3 " + path_atual + "/../sincronismo/sincronismo_inicia_jobs.py &")

HOST = 'localhost'  # The server's hostname or IP address
PORT = 30090        # The port used by the server

funcoes_logs.insere_log("Determinado HOST " + str(HOST), local, 2)
funcoes_logs.insere_log("Determinando PORTA " + str(PORT), local, 2)

skin = PilImage.open(path_atual + '/../tela/oie_transparent.png')

q_tela = queue.Queue()
q_barcode = queue.Queue()

global LAST_IMAGE
LAST_IMAGE = ""

skin = PilImage.open(path_atual + '/../tela/oie_transparent.png')

version = "none"
try:
   with open(path_atual + "/../version.txt", "r") as f:
      version = f.read()
      f.close()
except:
   version = ""

# Obtemos a info do serial
serial = funcoes_serial.getSerial()

# Obtemos o numero do veiculo
try:
    with open(path_atual + "/../../caixa-magica-operacao/instalacao.json") as json_data_inst:
        aux = json.load(json_data_inst)
        numeroVeiculo = str(aux['numeroVeiculo'])
except:
    numeroVeiculo = ""

# Exibe mensagem de alerta, quando necessario
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

def send_tela(tela, nome_motorista=None, id_qrcode_motorista=None, id_web_motorista=None):
   try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

         data = {
               'tela': tela,
               'nome_motorista':nome_motorista,
               'id_qrcode_motorista':id_qrcode_motorista,
               'id_web_motorista':id_web_motorista
         }

         funcoes_logs.insere_log("Enviando dados core " + str(data), local, 2)
         s.connect((HOST, PORT))
         js = json.dumps(data)
         s.sendall(js.encode('utf-8'))
         data = s.recv(128)
         funcoes_logs.insere_log("Received: " + repr(data), local, 0)
   except Exception as e:
       funcoes_logs.insere_log("Erro ao enviar tela para tela_init - " + str(e), local, 3)

# Rotina usada para capturar as imagens
def captura():
   global LAST_IMAGE
   global LAST_IMAGE_LIDA

   # Inicializamos o status da tela sem o lock
   funcoes_camera.atualiza_lock_tela_viagem(False)

   # Obtemos a camera a ser utilizada
   try:
        with open(path_atual + "/../../caixa-magica-vars/config.json", "r") as json_data_aux:
           aux = json.load(json_data_aux)
           camera_cv2 = aux['camera_cv2']
           tela_x_inicio = aux["tela_x_inicio"]
           tela_x_final = aux["tela_x_final"]
           tela_y_inicio = aux["tela_y_inicio"]
           tela_y_final = aux["tela_y_final"]

   except Exception as e:
        camera_cv2 = 0
        print(str(e))

   # Checa se foi colocada uma camera para testes
   camera_testes = funcoes_camera.get_camera_testes()

   if camera_testes != "":
       camera_cv2 = camera_testes

   # O processo efetuara o streaming da camera de forma continua
   # Todavia, se a comunicacao com o dispositivo falhar, as tentativas continuarao a ocorrer na tentativa de autorecuperacao
   while 1:
       try:
           # Inicia a camera
           if camera_testes == "":
               vid = cv2.VideoCapture(camera_cv2)
               vid.set(cv2.CAP_PROP_BUFFERSIZE,1)

           LAST_IMAGE_LIDA = time.time()
           cap = cv2.VideoCapture(camera_cv2)
           ret, frame = cap.read()
           LAST_IMAGE = frame
           funcoes_camera.atualiza_status_camera(True)

           while ret:
               data_hora = datetime.datetime.now()
               data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")

               ret, frame = cap.read()
               frame = frame[tela_x_inicio:tela_x_final, tela_y_inicio:tela_y_final]

               LAST_IMAGE = frame
               LAST_IMAGE_LIDA = time.time()
               funcoes_camera.atualiza_status_camera(True)
       except Exception as e:
           funcoes_camera.atualiza_status_camera(False)
           print("Erro captura: " + str(e))
           time.sleep(0.1)

# Efetua a checagem do QR Code pela camera
def leitura_qr():
    global LAST_IMAGE

    while 1:
        try:
            image = cv2.flip(LAST_IMAGE,1)
            barcodes = pyzbar.decode(image)

            for barcode in barcodes:
                barcodeData = barcode.data.decode("utf-8")
                processaQR(barcodeData)
                funcoes_qrcode.limpa_qrcode()
        except:
            pass
        time.sleep(0.1)

# Rotina que faz a leitura de um qrcode a partir do coletado pelo leitor dedicado (Thread)
def interpreta_qrcode_leitora():
    funcoes_qrcode.inicializa_coletor_qrcode()
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


# Rotina que processa o QR code enviado pelo leitor dedicado ou pela tela
def processaQR(barcodeData):
    try:
        if barcodeData == "REBOOT_VALIDADOR":
            os.system("sudo reboot -f")

        funcoes_logs.insere_log("Consultando operador com o qr code: " + str(barcodeData), local, 2)

        sql = "select id_web,nome,matricula,manutencao from operadores where id_qr = '{}' /*and fiscal=false*/".format(barcodeData)
        result = conn.consultar(sql)

        if len(result) > 0:
            stop_thread = True

            # QR code de fiscal
            if result[0][3] == True:
                stop_thread = True
                    
                funcoes_logs.insere_log("Utilizando QR Code de manutencao", local)
                cv2.destroyAllWindows()
                send_tela(2)
                voltou = True
                return

            nome_motorista = str(result[0][1])
            id_qrcode_motorista = barcodeData
            id_web_motorista = str(result[0][0])
            matricula = str(result[0][2])

            payload = {
                            "nome": nome_motorista,
                            "id_qrcode": id_qrcode_motorista,
                            "id_web": id_web_motorista,
                            "matricula": matricula
                        }
            funcoes_logs.insere_log("Gravando motorista.json com conteudo :" + str(payload), local, 2)
            with open(path_atual +"/../../caixa-magica-operacao/motorista.json", "w+") as resp:
                resp.write(json.dumps(payload))

                funcoes_logs.insere_log("Executando send_tela", local, 2)
                send_tela(1, nome_motorista, id_qrcode_motorista, id_web_motorista)

                voltou = True
                return
        # Caso o QR Code nao exista na tabela de operadores, exibir mensagem de alerta
        else:
            funcoes_tela_corrente.registraTelaAtual("TELA_QR_CODE_MOTORISTA_NAO_ENCONTRADO")
            funcoes_logs.insere_log("Nao encontrado motorista com Qr Code: " + str(barcodeData), local, 2)
            mensagem= "\n\n\n\nQR Code informado\n\nnão encontrado\n\ncomo motorista."
            funcoes_telas.tela_alerta(mensagem, 3000, "red")
    except Exception as e:
        print(str(e))
        pass

# Rotina de leitura das capturas
def leitura():
    global LAST_IMAGE
    global STATUS_QR
    global STATUS_INTERNET
    local_exibe_tela = False

    while True:
        try:
            frame = LAST_IMAGE
            
            data_hora = datetime.datetime.now()
            data_hora = data_hora.strftime("%d/%m/%Y %H:%M:%S")

            if not local_exibe_tela:
                cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                local_exibe_tela = True

               # Preenchimento superior
            cv2.rectangle(frame, (0, 0),(700,120), (255,255,255),-1)

            # Preenchimento inferior
            cv2.rectangle(frame, (000, 650),(700,800), (255,255,255),-1)

               # preenchimento lateral esquerda
            cv2.rectangle(frame, (0,0),(50,700), (255,255,255), -1)

               # preenchimento lateral direita
            cv2.rectangle(frame, (550,0),(700,700), (255,255,255), -1)

               # Quadro da imagem
            cv2.rectangle(frame, (50,120),(550,650),(0,0,0),6)

               # Texto superior
            cv2.putText(frame, "Aponte QR Code no quadro abaixo:", (20, 100), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)

               # Texto inferior
            if STATUS_QR == "ON":
                cv2.putText(frame, "Ou aponte o QR Code no leitor abaixo:", (20, 690), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
            else:
                cv2.putText(frame, "Leitor QR Code indisponivel.", (30, 780), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)
                cv2.putText(frame, "Utilize QR Code via tela.", (30, 815), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)

            cv2.putText(frame, "Versao: " + str(version), (20, 715), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 255), 2)
            cv2.putText(frame, "Serial: {}".format(serial), (30, 15), cv2.FONT_HERSHEY_SIMPLEX, .6, (0,0,255),2)
            cv2.putText(frame, "Veiculo: {}".format(numeroVeiculo), (30, 35), cv2.FONT_HERSHEY_SIMPLEX, .6, (0,0,255),2)
            cv2.putText(frame, "Data/hora: {}".format(data_hora), (30, 55), cv2.FONT_HERSHEY_SIMPLEX, .6, (0,0,255),2)

            # Mostra o status da internet        
            cv2.putText(frame, str(STATUS_INTERNET), (505,25),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except Exception as e:
            time.sleep(0.01)

def check_status_camera():
    global LAST_IMAGE_LIDA
    global STATUS_QR
    timeout = 5

    time.sleep(10)

    while 1:
        try:
            time_limit = LAST_IMAGE_LIDA + timeout

            # Se nao existe lock de tela
            if not funcoes_camera.get_param_lock_tela_viagem():
                if time.time() > time_limit:
                    funcoes_camera.atualiza_status_camera(False)
                    notificacao = "Camera\nindisponivel"

                    if STATUS_QR == "ON":
                        notificacao = notificacao + "\n\nUtilize Leitor\nQR Code\npara abrir viagem"
                    else:
                        notificacao = notificacao + "\n\nLeitor\nQR Code\nindisponivel."
                    cfgTelas("red2", "white", notificacao,"", 150, 10000, 25, "red2")
                else:
                    funcoes_camera.atualiza_status_camera(True)

            # Mas se ha lock, efetuamos novo teste apos alguns segundos apenas
            else:
                time.sleep(2)
                LAST_IMAGE_LIDA = time.time()
                funcoes_camera.atualiza_status_camera(True)
        except Exception as e:
            print(str(e))
        time.sleep(0.1)

# Thread que checa o status do leitor QR
def check_status_qr():
    global STATUS_QR

    time.sleep(5)

    while 1:
        try:
            STATUS_QR = funcoes_qrcode.retorna_status_qrcode()
        except Exception as e:
            print(str(e))
            pass

# Thread que checa o status da internet periodicamente
def check_status_internet():
    global STATUS_INTERNET

    while 1:
        try:
            STATUS_INTERNET = funcoes_internet.get_status_internet()
        except Exception as e:
            print(str(e))
            pass

t1 = threading.Thread(target=captura)
t2 = threading.Thread(target=leitura)
t3 = threading.Thread(target=leitura_qr)
t4 = threading.Thread(target=interpreta_qrcode_leitora)
t5 = threading.Thread(target=check_status_camera)
t6 = threading.Thread(target=check_status_qr)
t7 = threading.Thread(target=check_status_internet)

# Primeiro, iniciamos a fila (que demora mais)
t1.start()

# Agora iniciamos a captura dos frames
t2.start()

# Efetua processamento via leitora QR na tela
t3.start()

# Iniciar thread de reconhecimento via leitora dedicada
t4.start()
t6.start()

t7.start()

time.sleep(2)
t5.start()
