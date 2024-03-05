#!/usr/bin/env python3
from core import gera_uuid
from core import funcoes_logs
from core import funcoes_tela_corrente
from core import funcoes_credenciais_token_rotas
from tela import funcoes_telas

import os
from time import sleep
import json
import subprocess
import sys

sys.path.insert(1, 'discord')
import functions_discord

# Registra que a aplicacao foi iniciada
functions_discord.insere_notificacao_fila('Aplicacao iniciada', 'eventos')

#from itertools import count
from tela.AnimatedGIF import *

if os.geteuid() != 0:
    funcoes_logs.insere_log("Aplicacao encerrada, nao iniciada como root", local)
    exit("Acesso root é necessário")

path_atual = "/home/pi/caixa-magica"

local = 'start.py'
funcoes_tela_corrente.registraTelaAtual("TELA_LOADING_SISTEMA")

# Iniciar processo que efetua alocacao da maquina no shellhub
funcoes_logs.insere_log("Adicionando maquina no ShellHub", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_adiciona_shellhub.py &")

# Instala o cliente do ZeroTier
funcoes_logs.insere_log("Adicionando client ZeroTier", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_inicia_zerotier.py &")

# Na pasta de operacoes, gera um JSON contendo o ID de sessao
funcoes_logs.insere_log("Gerando UUID de sessao", local)
try:
    uuid_sessao = gera_uuid.gera_uuid()
    funcoes_logs.insere_log("UUID de sessao gerado: " + str(uuid_sessao), local)
except Exception as e:
    funcoes_logs.insere_log("Erro gerando UUID de sessao: " + str(e), local)


path_operacao = path_atual + "/../caixa-magica-operacao/"

funcoes_logs.insere_log("Gravando sessao em " + path_operacao, local)
try:
    arq_json_sessao = path_operacao + "/sessao.json"
    conteudo = {"sessao": "" + uuid_sessao + ""}
    os.system("sudo rm -rf " + arq_json_sessao)
    with open(arq_json_sessao, 'w') as f:
        json.dump(conteudo, f)

    funcoes_logs.insere_log("Arquivo sessao.json gravado com UUID " + str(uuid_sessao), local)
except Exception as e:
    funcoes_logs.insere_log("Erro gravando sessao em " + path_operacao + ": " + str(e), local )

def instalado():
    try:
        file = open(path_atual +'/../caixa-magica-operacao/instalacao.json')
        data = file.read()
        instalacao = json.loads(data)
        if (not instalacao['acesso'] or instalacao['acesso'] == ''):
            return False
        else:
            return True
    except:
        return False

# Checa se já existe uma instalacao feita
funcoes_logs.insere_log("Checando se ha instalacao feita", local)
while not instalado():
    funcoes_logs.insere_log("Sem instalacao feita. Apresentando tela para informe do ID do onibus.", local)
    aguarde = funcoes_telas.TelaAguarde()
    p = subprocess.Popen(['python3', path_atual +'/instalacao.py'])
    p.wait()

def inicializado():
    try:
        file = open(path_atual + "/../caixa-magica-operacao/aberto.txt", "r")
        data = file.read()
        return True
    except:
        return False

# Geramos aqui um token de autenticacao inicial
funcoes_credenciais_token_rotas.gera_json_auth()

# Se nao tem viagem aberta, direcionamos pra tela de leitura de QR code do operador
if not inicializado():
    funcoes_logs.insere_log("Instalacao efetuada. Abrindo tela informe QR Code operador.", local)
    p = subprocess.Popen(['python3', path_atual+ '/core/telaInicializacao.py'])
    p.wait()
# caso contrario, direcionamos pra tela de viagem aberta (leitura facial e/ou qr code)
else:
    funcoes_logs.insere_log("Viagem ja esta aberta. Redirecionando para tela reconhecimento facial/QR Code", local)
    os.system("sudo sh " + path_atual + "/core/inicializar_sistema.sh")
