sudo pkill -9 -f start_monitor.sh
sleep 2
sudo pkill -9 -f python3
sleep 2
sudo pkill -9 -f pyconcrete
sleep 2

echo 'Zerando pasta de fotos'
sudo rm -rf 	/home/pi/caixa-magica-img
sudo mkdir 	/home/pi/caixa-magica-img

echo "Zerando logs"
sudo rm -rf /home/pi/caixa-magica-logs
sudo mkdir -p /home/pi/caixa-magica-logs

echo 'Zerando banco'
sh reset_bd.sh

echo 'Removendo os JSON de inicializacao e tal'
rm -f /home/pi/caixa-magica-operacao/*


#sudo reboot -f
