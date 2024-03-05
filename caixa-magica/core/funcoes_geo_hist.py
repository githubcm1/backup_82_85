import datetime
import sys
import pathlib
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_viagem
import db
import json
import time

from haversine import haversine, Unit

conn = db.Conexao()

LIMITE_KMS_MOV_VIAGEM_FECHADA = 1
NUM_CHECKS_MOV_VIAGEM_FECHADA = 10


try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        LIMITE_KMS_MOV_VIAGEM_FECHADA = aux['limite_kms_mov_viagem_fechada']
except:
    pass

def get_geoloc_recente():
    try:
        with open(path_atual + "/../../caixa-magica-operacao/geolocalizacao.json") as json_data:
            aux = json.load(json_data)
            geoloc = aux['geolocalizacao']
    except:
        geoloc = ""

    return geoloc.strip()

# Insere a geolocalizacao corrente na tabela de controle
def insereHistoricoGeoloc():
    now = datetime.datetime.utcnow()

    # Primeiro, pegamoso id da viagem que esta aberta
    try:
        id_viagem = funcoes_viagem.get_viagem_atual()
    
        if id_viagem == None:
            id_viagem = ""
    except:
        id_viagem = ""

    try:
        with open(path_atual + "/../../caixa-magica-operacao/motorista.json") as json_data:
            aux = json.load(json_data)
            motoristaid = aux['id_web']
    except:
        motoristaid = "0"

    try:
        # atraves da geolocalizacao registrada no arquivo JSON, pegamos a latitude e longitude
        geoloc = get_geoloc_recente()

        # Separamos a string por virgulas
        if geoloc != "":
            try:
                lat_long = geoloc.split(",")
                latitude = lat_long[0]
                longitude = lat_long[1]
            except:
                latitude = 0
                longitude = 0
        else:
            latitude =0 
            longitude = 0
        
        # se nao existem dados de latitude e longitude, nem gravamos na base de dados
        if latitude == 0 and longitude == 0:
            return

        # Insere na tabela
        sql = """insert into historico_geoloc (latitude, longitude, viagemid, motoristaid, dateinsert)
                 values (%s, %s, %s, %s, %s) on conflict (id) do nothing"""
        dados = (latitude, longitude, id_viagem, motoristaid, now,)
        conn.manipularComBind(sql, dados)
    except Exception as e:
        pass

# Pegamos o ID do ultimo registro de hsitorico
def pegaUltimoHistoricoGeoloc():
    sql = "select coalesce(max(id),0) from historico_geoloc"
    result = conn.consultar(sql)

    for row in result:
        return row[0]
    return 0

# Pegamos o ID imediantamente anterior de historico
def pegaAnteriorHistoricoGeoloc(idgeo):
    sql = "select coalesce(max(id),0) from historico_geoloc where id < %s"
    dados=(idgeo,)
    result = conn.consultarComBind(sql, dados)

    for row in result:
        return row[0]
    return 0

# Pegamos a latitude e longitude do registro
def pegaLatLongHistoricoGeoloc(idgeo):
    sql = "select latitude, longitude from historico_geoloc where id = %s"
    dados=(idgeo,)
    result = conn.consultarComBind(sql, dados)

    ret = []
    for row in result:
        ret.append(row[0])
        ret.append(row[1])

    if len(ret) <= 0:
        ret.append(0)
        ret.append(0)
    return ret
    

# rotina que insere um historico, e ja calcula a imediata distancia em relacao ao registro anterior
def calculaDistanciaHistoricoGeoloc():
    # Primeiro, insere o novo registro
    insereHistoricoGeoloc()

    # Pegamos o ultimo ID
    ultimoid = pegaUltimoHistoricoGeoloc()

    # Pega o antecessor
    penultimoid = pegaAnteriorHistoricoGeoloc(ultimoid)

    # Pegamos os detalhes de latitude e longitude do registro + recente
    if ultimoid != "":
        lat_long_1 = pegaLatLongHistoricoGeoloc(ultimoid)

        if lat_long_1[0] == 0 and lat_long_1[1] == 0:
            distancia = 0
        else:
            p_atual = (lat_long_1[0], lat_long_1[1])

            if penultimoid != "":
                lat_long_2 = pegaLatLongHistoricoGeoloc(penultimoid)
                if lat_long_2[0] == 0 and lat_long_2[0] == 0:
                    distancia = 0
                else:    
                    p_ant = (lat_long_2[0], lat_long_2[1])

                    try:
                        distancia = haversine(p_ant, p_atual, unit=Unit.KILOMETERS)
                    except Exception as e:
                        distancia = 0
            else:
                distancia = 0

    # Atualiza a distancia na base de dados
    sql = "update historico_geoloc set distancia_last_id_km = %s where id = %s"
    dados = (distancia, ultimoid,)
    conn.manipularComBind(sql, dados)

# Rotina usada para identificar eventuais casos onde algum motorista esteja trafegando
# com viagem fechada (ou seja, veiculo apresentou movimento pelo GPS)
def pega_mov_viagem_fechada():
    ret = []
    primeira_data = ""
    ultima_data = ""

    # Consideramos para analise o horario e dat UTC
    now = datetime.datetime.utcnow()
    data_check_a_partir = now - datetime.timedelta(minutes = 5)
    
    cnt = 1
    sql = """select id, viagemid, motoristaid, distancia_last_id_km, dateinsert
             from historico_geoloc h
             where dateinsert >= '""" + str(data_check_a_partir) + """' 
             order by 1 desc limit """ + str(NUM_CHECKS_MOV_VIAGEM_FECHADA)
    result = conn.consultar(sql)

    soma_dist = 0

    for row in result:
        primeira_data = row[4]

        if cnt == 1:
            ultima_data = primeira_data

        viagemid = row[1]

        # Se houver algum registro de viagem no intervalo, deveremos abortar a checagem
        if viagemid != "":
            ret.append(False)
            ret.append("")
            ret.append("")
            return ret
        else:
            soma_dist = soma_dist + row[3]

        cnt = cnt + 1

    # Se nao há um numero de registros suficiente, nao consideramos a analise
    if cnt < NUM_CHECKS_MOV_VIAGEM_FECHADA:
        ret.append(False)
        ret.append("")
        ret.append("")
        return ret

    # Se a soma da distancia percorrida for superior ao limite estabelecido, marcamos como TRUE
    if soma_dist > LIMITE_KMS_MOV_VIAGEM_FECHADA:
        ret.append(True)
        ret.append(primeira_data)
        ret.append(ultima_data)
        return ret
    else:
        ret.append(False)
        ret.append("")
        ret.append("")
        return ret
          
        

