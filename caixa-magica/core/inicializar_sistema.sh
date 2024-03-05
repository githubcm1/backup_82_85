sudo pkill -9 -f telas_init
sudo pkill -9 -f telaInicializacao
sudo pkill -9 -f sincronismo
sudo pkill -9 -f monitor_placa_serial
sudo pkill -9 -f central_placa_serial
sudo pkill -9 -f inicializar_sistema.py
sudo pkill -9 -f keep_alive

echo "Iniciando aplicacao"

sudo python3 /home/pi/caixa-magica/core/monitor_placa_serial.py &
sudo python3 /home/pi/caixa-magica/keep_alive.py &
sleep 1
sudo python3 /home/pi/caixa-magica/core/inicializar_sistema.py &
