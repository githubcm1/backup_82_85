import paramiko
from datetime import datetime
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
##import funcoes_viagem
import db

import json

def get_geoloc_recente():
    try:
        with open(path_atual + "/../../caixa-magica-operacao/geolocalizacao.json") as json_data:
            aux = json.load(json_data)
            geoloc = aux['geolocalizacao']
    except:
        geoloc = ""

    return geoloc

def retorna_coord(valor, pos_globo):
    DD = int(float(valor)/100)
    SS = float(valor) - DD * 100

    LatDec = DD + SS/60

    if pos_globo == "W" or pos_globo == "S":
        LatDec = LatDec * -1

    return LatDec

def retorna_latitude_longitude(lat, pos_lat, lon, pos_lon):
    lat = retorna_coord(lat, pos_lat)
    lon = retorna_coord(lon, pos_lon)
    return str(lat) + "," + str(lon)

def decodifica_gps(string_gps):
    try:
        arrGPS = string_gps.strip().split(",")

        lat = float(arrGPS[3])
        pos_lat = arrGPS[4]
        lon = float(arrGPS[5])
        pos_lon = arrGPS[6]
        return retorna_latitude_longitude(lat, pos_lat, lon, pos_lon)
    except:
        return "0,0"

# Rotina utilizada para captura do GPS no roteador ICR
def get_geoloc_icr():
    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cliente.connect("192.168.100.1",username="admin", password="admin", look_for_keys=False)

        # Roda o comando para obter a geolocalizacao
        comando = "cat /tmp/GNSS/NMEA"

        stdin, stdout, stderr = cliente.exec_command(comando)
        saida = str(stdout.read().decode("utf-8")).strip()

        stdin.flush()
        stdin.close()
    except:
        saida = ""
    return saida

# Rotina que converte a geoloc do roteador ICR em padrao latitude + longitude
def get_latitude_longitude_icr():
    saida = get_geoloc_icr()

    if saida != "":
        saida = decodifica_gps(saida)
        return saida
    return ""
