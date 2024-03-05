import sys
import time
import json
import requests

path = '/home/pi/caixa-magica/'
sys.path.insert(1, path + "/core")
import endpoints
import db

ENDPOINT = endpoints.urlbase

# Checamos se o envio esta habilitado
try:
    with open(path + "/../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        habilitado = aux['habilita_envio_logs_api']
except:
    habilitado = False

if habilitado:
    INTERVALO_EXEC = 60
    ENDPOINT = ENDPOINT + "Log"
    conn = db.Conexao()

    # Abrimos o arquivo de instalacao, para obtermos detalhes do log do veiculo
    try:
        with open(path + "/../caixa-magica-operacao/instalacao.json") as json_data:
            aux = json.load(json_data)
            operadora = aux['operadora']
            codigoacesso = aux['acesso']
            caixaid = aux['caixa_id']
            numeroVeiculo = aux['numeroVeiculo']
            veiculo = aux['veiculo']
    except Exception as e:
        print(str(e))
        pass

    header = {"codigoAcesso": str(codigoacesso),
              "content-type": "application/json"}

    while 1:
        sql = "select id, string_log, local, dateinsert,severidade from logs where data_envio_servidor is null order by 1 limit 100"
        result = conn.consultar(sql)

        for row in result:
            try:
                mensagem = str(row[2]) + ";"+str(row[3])+";"+str(row[1])
                body = {"severidade": str(row[4]),
                    "mensagem": str(mensagem)}
                r = requests.post(ENDPOINT, data=json.dumps(body), headers=header, timeout=5)
            
                if r.ok:
                    sql = """update logs 
                         set data_envio_servidor=(now() at time zone 'utc')
                         where id = %s"""
                    data = (row[0],)
                    conn.manipularComBind(sql, data)
            except:
                pass

        time.sleep(INTERVALO_EXEC)

