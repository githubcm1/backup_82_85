from rfidgeek import PyRFIDGeek, ISO14443A, ISO15693

rfid = PyRFIDGeek(serial_port='/dev/ttyAMA0')
for protocol in [ISO14443A, ISO15693]:
    rfid.set_protocol(protocol)
    for uid in rfid.inventory():
        print('Found {} tag: {}', protocol, uid)

rfid.close()