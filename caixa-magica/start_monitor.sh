#!/bin/bash

# Limpa a tela do terminal.
clear

# Finaliza, imediatamente, os processos ativos do Python 3.
sudo pkill -9 -f python3

# Finaliza, imediatamente, os processos ativos do Pyconcrete (encriptacao dos scripts Python).
sudo pkill -9 -f pyconcrete

# Finaliza, imediatamente, os processos ativos do Elasticsearch (banco de dados das matrizes para reconhecimento facial).
sudo pkill -9 -f elastic

# Forca a instalacao da biblioteca "haversine" (calculo da distancia geografica entre 2 pontos - latitude x longitude).
yes | sudo pip3 install haversine

# Limpa a tela do terminal.
clear

# Forca a instalacao da biblioteca "deepface" (framework para reconhecimento facial e analise dos atributos faciais).
yes | sudo pip3 install deepface

# Instala o servico "unbuffer", para coleta de saidas do NFC via Stream
yes | sudo apt-get install expect

# Atualiza o modulo de criptografia
yes | sudo python3 -m pip install --upgrade pyjwt[crypto]

# Limpa a tela do terminal.
clear

# Instala o lxterminal
# filename='check_start_sh.txt'
# string_to_find='python3 /home/pi/caixa-magica/keep_alive.py'

# Executa o script Python que exibe a tela de aguarde com o logo da Buspay e um GIF animado de "spinner" na janela principal da aplicacao.
# O caractere "&" no final da instrucao indica que a proxima instrucao nao deve aguardar finalizar a execucao desta instrucao.
sudo python3 /home/pi/caixa-magica/tela_aguarde.py &

# Executa o script Python que inicializa o servico do Elasticsearch e cria os indices necessarios.
sudo python3 /home/pi/caixa-magica/start_es.py primeira_exec

# Imprime a mensagem "Iniciando BD" na tela do terminal.
echo "Iniciando BD"

# Executa o script Python que inicializa o banco de dados PostgreSQL local (do validador).
sudo python3 /home/pi/caixa-magica/start_conf_db.py

# Imprime a mensagem "Rodando script criacao BD" na tela do terminal.
echo "Rodando script criacao BD"

# Executa o script Python que cria os objetos necessarios no banco de dados PostgreSQL local.
sudo python3 /home/pi/caixa-magica/scripts_bd/script_bd.py

# Imprime a mensagem "Criando particoes" na tela do terminal. 
echo "Criando particoes"

# Caminho do script: /home/pi/caixa-magica/sincronismo/sincronismo_obtem_linhas.py
sudo python3 sincronismo/sincronismo_obtem_linhas.py force

#exit 0

sudo sh /home/pi/caixa-magica/start.sh

cnt_tries=0

while :
do
  sudo python3 /home/pi/caixa-magica/check_keep_alive.py
  sleep 5
done
