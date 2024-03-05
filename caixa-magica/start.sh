# Limpa a tela
clear

# Removemos pastas de cache que porventura estejam ainda no sistema
sudo rm -rf /home/pi/caixa-magica/core/__pycache__
sudo rm -rf /home/pi/caixa-magica/sincronismo/__pycache__
sudo rm -rf /home/pi/caixa-magica/tela/__pycache__

# Removemos arquivos de operacao, que devem ser refeitos durante o uso da aplicacao
sudo mkdir -p /home/pi/caixa-magica-operacao
sudo rm -rf /home/pi/caixa-magica-operacao/mensagem_process_core.json
sudo rm -rf /home/pi/caixa-magica-operacao/mensagem_serial.json
sudo rm -rf /home/pi/caixa-magica-operacao/prova-vida.json
sudo rm -rf /home/pi/caixa-magica-operacao/var_core.json
sudo rm -rf /home/pi/caixa-magica-operacao/vars_serial.json
sudo rm -rf /home/pi/caixa-magica-operacao/telaatual.txt 
sudo rm -rf /home/pi/caixa-magica-operacao/qrcode.json
sudo rm -rf /home/pi/caixa-magica-operacao/semaforoleitura.txt
sudo rm -rf /home/pi/caixa-magica-operacao/status_cobranca.json
sudo rm -rf /home/pi/caixa-magica-logs/logs_db.txt

# Cria pasta de token de updates, caso ainda nao exista
sudo mkdir -p /home/pi/caixa-magica-updates/

# Cria pasta de logs, caso ainda nao exista
sudo mkdir -p /home/pi/caixa-magica-logs
sudo mkdir -p /home/pi/caixa-magica-logs/sessao

# Cria a pasta de imagens, caso ainda nao exista
sudo rm -rf /home/pi/caixa-magica-img-rec
sudo rm -rf /home/pi/caixa-magica-img
sudo mkdir -p /home/pi/caixa-magica-img

sudo mkdir -p /home/pi/caixa-magica-vars
sudo mkdir -p /home/pi/caixa-magica-share
sudo mkdir -p /home/pi/caixa-magica-rec-facial
sudo mkdir -p /home/pi/caixa-magica-rec-facial/share


# Determina variavel de ambiente
export HOME_CM="/home/pi/caixa-magica"

# Mata processos python3
echo "-- FINALIZANDO PROCESSOS PYTHON3 --"
sudo pkill -9 -f python3

# Mata processos pyconcrete
echo "-- FINALIZANDO PROCESSOS PYCONCRETE --"
sudo pkill -9 -f pyconcrete

sudo pkill -9 -f nfcDemoApp
sleep 0.2
sudo pkill -9 -f nfcCaixaMagica
sleep 0.2

# Remove arquivos com extensoes temporarias (criadas pelo proprio Python em execucoes passadas)
sudo python3 /home/pi/caixa-magica/remove_arqs_cache.py

# Inicia servico do Elastic Search
sudo python3 /home/pi/caixa-magica/start_es.py &

# Inicializa programa que indica que a aplicacao esta ativa
sudo python3 /home/pi/caixa-magica/keep_alive.py &

# Inicializa tela de aguarde (loading)
sudo python3 /home/pi/caixa-magica/tela_aguarde.py &

# Inicia programa monitor de placa serial
sudo python3 /home/pi/caixa-magica/core/monitor_placa_serial.py &
sleep 1

echo "-- REMOVENDO ANTIGO DIRETORIO TESTE HARDWARE --"
sudo rm -rf "/home/pi/caixa-magica-teste-HW"

# Executa script criacao jsons basicos
cd $HOME_CM
sudo python3 /home/pi/caixa-magica/gera_jsons_linha_base.py & 

# chama script que obtem as linhas
echo "Obtendo linhas"
sudo python3 /home/pi/caixa-magica/sincronismo/sincronismo_obtem_linhas.py force 

echo "Baixando conf discord"
sudo python3 /home/pi/caixa-magica/discord/download_conf_discord.py &

# Inicia aplicacao principal
echo "-- INICIANDO APLICACAO --"
sudo python3 /home/pi/caixa-magica/start.py

