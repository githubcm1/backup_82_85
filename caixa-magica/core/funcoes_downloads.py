import os
import json
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)

import funcoes_reboot

with open(path_atual + "/../../caixa-magica-vars/config_urls_bib.json") as json_data:
    config = json.load(json_data)
    url_shape_predictor = config['url_shape_predictor']
    url_face_encoder = config['url_face_encoder']
    url_haarcascade_frontal = config['url_haarcascade_frontal']

def download_individual(origem, destino):
    try:
        destino = destino + origem[origem.rfind("/")+1: len(origem)]
        os.system("sudo wget -O " + destino + " " + origem )
        funcoes_reboot.restart_cm()
    except:
        print("")

def download_shape_predictor():
    origem = url_shape_predictor
    destino = path_atual + "/../../caixa-magica-rec-facial/share/"

    try:
        download_individual(origem, destino)
    except:
        print("")

def download_face_encoder():
    origem = url_face_encoder
    destino = path_atual + "/../../caixa-magica-rec-facial/share/"

    try:
        download_individual(origem, destino)
    except:
        print("")

def download_haarcascade_frontal():
    origem = url_haarcascade_frontal
    destino = path_atual + "/../../caixa-magica-rec-facial/"
    
    try:
        download_individual(origem, destino)
    except:
        print("")
