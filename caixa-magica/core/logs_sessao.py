import pathlib
import json
import os
from datetime import datetime
import sys

path_atual = "/home/pi/caixa-magica/core"

sys.path.insert(1, str(path_atual))
import identificador_caixa_magica

# obtemos arquivo de sessao
def obtem_sessao():
    path_json = str(path_atual) + "/../../caixa-magica-operacao/sessao.json"
    with open(path_json) as json_data:
        sessao_json = json.load(json_data) 
        
        return sessao_json['sessao']

# determina nome do arquivo de sessao
# Notacao (a cada ";"):
# campo 1: enviado para backend (S ou N)
# campo 2: data e hora registro
# campo 3: ID da caixa magica
# campo 4: string relato
# campo 5: se o log eh considerado critico ou nao (S ou N)
# campo 6: empresa da caixa magica
# campo 7: id da instalacao (onibus)
# campo 8: identificacao onibus
def determina_logs_sessao():
    path = str(path_atual) + "/../../caixa-magica-logs/sessao/" + obtem_sessao() + ".txt"
    return path

# Grava arquivo de sessao (caso ele ainda não exista
def gera_arq_logs_sessao():
    path = determina_logs_sessao()
    os.system("sudo touch " + path)

# Grava log da sessao
def grava_log_sessao(string_log, critico = "N"):
    # Abre arquivo de instalacao da CM, para obter detalhes
    if 1==1:#try:
        with open(str(path_atual) + "/../../caixa-magica-operacao/instalacao.json") as json_data:
            dados = json.load(json_data)
            operadoraid = str(dados['operadora'])
            veiculo_id = str(dados['veiculo'])
            veiculo = str(dados['numeroVeiculo'])
    else:#except:
        operadoraid = ""
        veiculo_id = ""
        veiculo = ""

    gera_arq_logs_sessao()
    path = determina_logs_sessao()

    data_hora = datetime.now()
    data_hora = data_hora.strftime('%Y-%m-%d %H:%M:%S')
    
    id_caixa = identificador_caixa_magica.getserial()

    saida = "N;" + str(data_hora) + ";" + str(id_caixa) + ";" + str(string_log).strip().upper() + ";" + str(critico) + ";" + operadoraid + ";" + veiculo_id + ";" + veiculo +";" + "\n"
    
    obj = open(path, "a")
    obj.write(saida)
    obj.close

