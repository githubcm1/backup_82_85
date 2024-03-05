echo "Copiando script autostart"
sudo cp /home/pi/caixa-magica/templates/autostart/auto.desktop /home/pi/.config/autostart/auto.desktop

echo "Efetuando reboot..."
sleep 1
sudo reboot -f

