echo 'Matando tudo'
sudo pkill -9 -f start_monitor.sh
sleep 1
sudo pkill -9 -f python3
sleep 1
sudo pkill -9 -f pyconcrete
sleep 1

echo 'Zerando pasta de fotos'
sudo rm -rf 	/home/pi/caixa-magica-img
sudo mkdir 	/home/pi/caixa-magica-img
echo 'Foi'

echo "Zerando logs"
sudo rm -rf /home/pi/caixa-magica-logs
sudo mkdir -p /home/pi/caixa-magica-logs

echo 'Zerando banco'
sudo sh /home/pi/caixa-magica/reset_bd.sh

echo 'Removendo os JSON de inicializacao e tal'
rm -f /home/pi/caixa-magica-operacao/inicializacao.json
rm -f /home/pi/caixa-magica-operacao/motorista.json
rm -f /home/pi/caixa-magica-operacao/viagem.json
rm -f /home/pi/caixa-magica-operacao/passagens_viagem.json
rm -f /home/pi/caixa-magica-operacao/instalacao.json
rm -f /home/pi/caixa-magica-operacao/aberto.txt
rm -f /home/pi/caixa-magica-operacao/idFechamentoViagem.json
rm -f /home/pi/caixa-magica-operacao/camera_testes.txt
echo 'Foi'

echo "removendo da rede ZeroTier"
#sudo python3 /home/pi/caixa-magica/remove_zerotier.py

sudo rm -f /home/pi/caixa-magica-operacao/sincronismo.json
sudo rm -f /home/pi/caixa-magica-operacao/sincronismo_operadores.json
sudo rm -f /home/pi/caixa-magica-operacao/rede_zerotier.txt
sudo rm -f /home/pi/caixa-magica-operacao/sincronismo_facial.json
sudo rm -f /home/pi/caixa-magica-operacao/sincronismo_beneficios.json

sudo python3 /home/pi/caixa-magica/sincronismo/sincronismo_gera_json.py

sudo python3 /home/pi/caixa-magica/remove_indices_elastic.py

echo 'Reset efetuado'

sudo pkill -9 -f python3
sudo pkill -9 -f pyconcrete
sudo pkill -9 -f elastic
#sudo reboot -f
