import sys
import pathlib
path_atual = "/home/pi/caixa-magica"
sys.path.insert(1, path_atual)
import os.path as path
import os

sys.path.insert(1, path_atual + "/core/")
import funcoes_logs

local = 'gera_jsons_linha_base.py'

funcoes_logs.insere_log("Iniciando " + local, local)

# gera conteudo base do arquivo config_sentido_viagem.json
arquivo = path_atual + "/../caixa-magica-vars/config_sentido_viagem.json"
if not path.exists(arquivo):
    funcoes_logs.insere_log("Gerando arquivo " + arquivo, local)
    os.system("sudo touch " + arquivo)

    funcoes_logs.insere_log("Colocando configuracao padrao no arquivo config_sentido_viagem.json", local)
    os.system("sudo echo '{\"informe_sentido_habilitado\": true}' | sudo tee " + arquivo)
else:
    funcoes_logs.insere_log("Arquivo " + arquivo + " ja existe, mantendo versao existente", local)

