# Limpa a tela do terminal.
clear

# Finaliza, imediatamente, os processos ativos do Elasticsearch (banco de dados das matrizes para reconhecimento facial).
sudo pkill -9 -f elastic

# Interrompe a execucao do script por 2 segundos.
sleep 2

# Imprime o texto "Iniciando elastic" na tela do terminal.
echo "Iniciando elastic"

# Inicializa o Elasticsearch utilizando os processadores listados no parametro "-c". O comando e executado
# com o usuario "buspay" ("su - buspay") e a saida e direcionada para "/dev/null" (descartada).
sudo taskset -c 3,2,1,0 su - buspay /home/pi/elastic_search/bin/elasticsearch & > /dev/null 2>&1

