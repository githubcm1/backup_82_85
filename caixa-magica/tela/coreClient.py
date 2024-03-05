import socket
import json
from time import sleep

HOST = 'localhost'  # The server's hostname or IP address
PORT = 30020        # The port used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    data = {
        'tela': 1,
        'nome': 'Jeiverson'
    }
    js = json.dumps(data)
    print (js)
    s.sendall(js.encode('utf-8'))
    sleep(10)
    data = {
        'tela': 2,
        'nome': ''
    }
    js = json.dumps(data)
    print (js)
    s.sendall(js.encode('utf-8'))
    # data = s.recv(1024)
    sleep(10)
    data = {
        'tela': 3,
        'nome': ''
    }
    js = json.dumps(data)
    print (js)
    s.sendall(js.encode('utf-8'))
    # data = s.recv(1024)
    sleep(10)

print('Received', repr(data))
