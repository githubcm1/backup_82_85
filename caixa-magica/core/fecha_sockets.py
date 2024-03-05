import socket

try:
    s = socket.socket()
    s.connect(("127.0.0.1", 30010))
    s.close()
except:
    pass

try:
    s = socket.socket()
    s.connect(("127.0.0.1", 30020))
    s.close()
except:
    pass

try:
    s = socket.socket()
    s.connect(("127.0.0.1", 30110))
    s.close()
except:
    pass
