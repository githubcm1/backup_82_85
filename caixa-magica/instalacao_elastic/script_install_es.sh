### SCRIPT UTILIZADO APENAS PARA O PROCEDIMENTO DE INSTALACAO ###
clear

print("Instalando elastic search")
sudo pkill -9 -f python3
sudo pkill -9 -f pyconcrete
sudo pkill -9 -f start

echo "Atualizando PIP"
sudo pip3 install --upgrade pip
echo "Atualizado PIP"

sudo rm -rf /home/pi/elastic_search/
sudo mkdir -p /home/pi/elastic_search

cd /home/pi/procedimento_elastic/
sudo rm -rf elasticsearch-8.5.3
sudo mkdir -p /home/pi/download_es/
cd /home/pi/download_es/
sudo wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.5.3-linux-x86_64.tar.gz

echo "Extraindo conteudo do Elastic..."
sudo tar -xvf elasticsearch-8.5.3-linux-x86_64.tar.gz
echo "Conteudo extraido"

sudo chown -R buspay:buspay elasticsearch-8.5.3
sudo mv elasticsearch-8.5.3/* /home/pi/elastic_search/
sudo rm -rf  elasticsearch-8.5.3/
sudo chown -R buspay:buspay /home/pi/elastic_search/

echo "Baixando client Python do Elastic Search..."
sudo pip3 uninstall elasticsearch -y
sudo pip3 install elasticsearch==8.5.3
echo "Baixado client Python do Elastic Search"

sudo rm -f /home/pi/caixa-magica-vars/param_elastic.json
sudo echo '{"habilitado": false}' | sudo tee /home/pi/caixa-magica-vars/param_elastic.json

sleep 1

sudo pkill -9 -f elastic
echo "Iniciando elastic"
sudo su - buspay /home/pi/elastic_search/bin/elasticsearch & > /dev/null 2>&1

echo "Aguardando start elastic..."
sleep 120

echo "Mudando conf elastic (sem https)"
sudo sed -i 's/xpack.security.enabled: true/xpack.security.enabled: false/g' /home/pi/elastic_search/config/elasticsearch.yml
sudo pkill -9 -f elastic

echo "Reiniciando elastic"
sudo su - buspay /home/pi/elastic_search/bin/elasticsearch & > /dev/null 2>&1
sleep 120

sudo curl -XPUT "localhost:9200/_template/default_template" -H 'Content-Type: application/json' -d '{"index_patterns": ["*"], "settings": {"number_of_replicas": 0}}'
