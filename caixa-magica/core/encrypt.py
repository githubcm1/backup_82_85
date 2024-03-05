from cryptography.fernet import Fernet
def generate_cert(save=False):
    key = Fernet.generate_key()
    if save:
        string = key.decode('utf-8')
        with open('cert.key', 'w+') as c:
            c.write(string)
    return key

def encrypt(data):
    with open('/home/pi/caixa-magica/core/cert.key', 'r') as c:
       key = c.read().encode('utf-8')
    f = Fernet(key)
    return f.encrypt(data.encode('utf-8')).decode('utf-8')
    return data

def decrypt(data):
    with open('/home/pi/caixa-magica/core/cert.key', 'r') as c:
       key = c.read().encode('utf-8')
    f = Fernet(key)
    return f.decrypt(data.encode('utf-8')).decode("utf-8")
    return data
#print(encrypt("d4d48509-a33c-4bbb-82f5-b54be6698b36"))
#print(decrypt("gAAAAABe1J7l6UfzVyy1cBmXDhsmcB_OIJi77LKCb9LvMzxMiYeHntRnGDNZMkNNjPVP_vz3wQgX6c3K7XW2Ckhf5KDyiF53xamhNgUFpDKFPdKQ98Ag-CKXkWRer2Aqa0iMUYKphMzi"))
