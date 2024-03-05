import sys
sys.path.insert(1,'/home/pi/caixa-magica/core/')
import db
import json

path_operadores = '/home/pi/caixa-magica-operacao/sincronismo_operadores.json'
path_facial = '/home/pi/caixa-magica-operacao/sincronismo_facial.json'
path_contas = '/home/pi/caixa-magica-operacao/sincronismo.json'

conn = db.Conexao()

# Pega a maior data atualizacao de registro de operadores
sql = "select coalesce(max(backend_lastupdatetime),'0001-01-01T00:00:00') from operadores"
result = conn.consultar(sql)

try:
    with open(path_operadores) as json_data:
        aux = json.load(json_data)
        aux['lastUpdateTime'] = str(result[0][0])

    pos = aux['lastUpdateTime'].find("+")

    if pos > 0:
        aux['lastUpdateTime'] = aux['lastUpdateTime'][0:pos]

    with open(path_operadores, "w") as fil:
        fil.write(json.dumps(aux))
except:
    pass

# Pega a maior data de atualizacao de contas
sql = "select coalesce(max(backend_lastupdatetime),'0001-01-01T00:00:00') from contas"
result = conn.consultar(sql)

try:
    with open(path_contas) as json_data:
        aux = json.load(json_data)
        aux['lastSyncAtualizacao'] = str(result[0][0])

    pos = aux['lastSyncAtualizacao'].find("+")

    if pos > 0:
        aux['lastSyncAtualizacao'] = aux['lastSyncAtualizacao'][0:pos]

    with open(path_contas, "w") as fil:
        fil.write(json.dumps(aux))
except:
    pass

# Pega a maior data de atualizacao de registros de faces
# Utilizamos a mesma data referente ao registro de contas
try:
    with open(path_facial) as json_data:
        aux = json.load(json_data)
        aux['lastUpdateTime'] = str(result[0][0])

    pos = aux['lastUpdateTime'].find("+")

    if pos > 0:
        aux['lastUpdateTime'] = aux['lastUpdateTime'][0:pos]

    with open(path_facial, "w") as fil:
        fil.write(json.dumps(aux))
except:
    pass

