import socket

HOST = "127.0.0.1"
PORT = 30010

cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#cs.bind((HOST, PORT))
cs.connect((HOST, PORT))
cs.shutdown(socket.SHUT_RDWR)
cs.close()
