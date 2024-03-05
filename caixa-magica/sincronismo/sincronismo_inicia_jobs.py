import os
import sys

import pathlib
path_atual = "/home/pi/caixa-magica/sincronismo"
path_atual = path_atual + "/.."

sys.path.insert(1, path_atual + "/core/")
import funcoes_logs
from time import sleep
import funcoes_viagem

local ='sincronismo_inicia_logs.py' 

if funcoes_viagem.get_viagem_atual() != "":
    viagem_aberta = True
else:
    viagem_aberta = False

INTERVALO_ENTRE_JOBS = 5

sleep(INTERVALO_ENTRE_JOBS)

os.system("sudo python3 " + path_atual + "/keep_alive.py &")
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_gera_json.py &")
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_lastupdate_json.py")
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_job_discord.py &")

sleep(INTERVALO_ENTRE_JOBS)

funcoes_logs.insere_log("Iniciando jobs de controle abertura e encerramento viagens", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_controle_viagens.py &")

sleep(INTERVALO_ENTRE_JOBS)

funcoes_logs.insere_log("Iniciando sincronismo.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo.py &")

sleep(INTERVALO_ENTRE_JOBS)

funcoes_logs.insere_log("Iniciando sincronismo_atualiza_indices_faciais.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_atualiza_indices_faciais.py &")

sleep(INTERVALO_ENTRE_JOBS)

funcoes_logs.insere_log("Iniciando sincronismo_gps.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_gps.py &")

sleep(INTERVALO_ENTRE_JOBS)

funcoes_logs.insere_log("Iniciando sincronismo_internet.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_internet.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_remove_imagens_legadas.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_remove_imagens_legadas.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando check_free_space.py", local)
os.system("sudo python3 " + path_atual + "/check_free_space.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando check_database_alive.py", local)
os.system("sudo python3 " + path_atual + "/check_database_alive.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando comprime_logs.py", local)
    os.system("sudo python3 " + path_atual + "/comprime_logs.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_obtem_linhas.py", local)
    os.system("sudo python3 " + path_atual + '/sincronismo/sincronismo_obtem_linhas.py &')

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_facial_linhas.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_facial_linhas.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_gera_arqs_logs.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_gera_arqs_logs.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_gera_arq_log_unico.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_gera_arq_log_unico.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_expurga_logs_enviados.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_expurga_logs_enviados.py &")

    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_expurga_qrcodes_utilizados.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_expurga_qrcodes_utilizados.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_envia_sentido.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_envia_sentido.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando  sincronismo_obtem_beneficios_pontuais.py",local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_obtem_beneficios.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_cobranca_similaridade_facial.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_cobranca_similaridade_facial.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_importa_favoritos.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_importa_favoritos.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_expurga_favoritos.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_expurga_favoritos.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_limpa_cache.py &")
    sleep(INTERVALO_ENTRE_JOBS)

    funcoes_logs.insere_log("Iniciando sincronismo_expurga_logs_integracoes.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_expurga_logs_integracoes.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_indicadores.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_indicadores.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_vacuum_logs.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_vacuum_logs.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_historico_gps", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_historico_gps.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_vacuum_historico_geoloc.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_vacuum_historico_geoloc.py &")

sleep(INTERVALO_ENTRE_JOBS)
funcoes_logs.insere_log("Iniciando sincronismo_estatisticas_geoloc.py", local)
os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_estatisticas_geoloc.py &")

if not viagem_aberta:
    sleep(INTERVALO_ENTRE_JOBS)
    funcoes_logs.insere_log("Iniciando sincronismo_vacuum_full_semanal.py", local)
    os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_vacuum_full_semanal.py &")

#sleep(5)
#funcoes_logs.insere_log("Iniciando sincronismo_envia_logs_api.py", local)
#os.system("sudo python3 " + path_atual + "/sincronismo/sincronismo_envia_logs_api.py &")

