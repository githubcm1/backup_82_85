import os

# Checa arquivo de sincronismo
path = "/home/pi/caixa-magica-operacao/sincronismo.json"
try:
    tam = os.path.getsize(path)
except:
    tam = 0

if tam <= 0:
    os.system("sudo touch " + path)
    os.system("echo '{\"lastSyncAtualizacao\": \"0001-01-01T00:00:00\", \"lastSyncBloq\": \"1900-01-01T00:00:00\", \"lastSyncDesbloq\": \"1900-01-01T00:00:00\"}' | sudo tee " + path)

# Checa arquivo de sincronismo
path = "/home/pi/caixa-magica-operacao/sincronismo.json"
try:
    tam = os.path.getsize(path)
except:
    tam = 0

if tam <= 0:
    os.system("sudo touch " + path)
    os.system("echo '{\"lastUpdateTime\": \"0001-01-01T00:00:00\"}' | sudo tee " + path)

# Checa arquivo de sincronismo 
path = "/home/pi/caixa-magica-operacao/sincronismo_facial.json"
try:
    tam = os.path.getsize(path)
except:
    tam = 0

if tam <= 0:
    os.system("sudo touch " + path)
    os.system("echo '{\"lastUpdateTime\": \"0001-01-01T00:00:00\"}' | sudo tee " + path)
