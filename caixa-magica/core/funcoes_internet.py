
import json
from datetime import datetime

path_status = '/home/pi/caixa-magica-operacao/status_internet.json'

# Grava o arquivo de status atual da internet
def atualiza_status_internet(status):
    datahorautc = datetime.utcnow().isoformat()
    string_file = '{"status": "' + str(status) + '", "datahorautc": "' + str(datahorautc) +'"}'

    with open(path_status, "w") as f:
        f.write(string_file)

# Checamos o status atual da camera
def get_status_internet():
    try:
        with open(path_status) as json_data:
            aux = json.load(json_data)
            return aux["status"]
    except Exception as e:
        return 'ONLINE'

