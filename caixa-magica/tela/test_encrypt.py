import sys
sys.path.insert(1, '/home/pi/caixa-magica/core/')
import encrypt

qr_encrypt = encrypt.encrypt(str(21))
print(qr_encrypt)