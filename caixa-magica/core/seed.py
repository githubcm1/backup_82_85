from numpy import load
import db
from tqdm import tqdm
conn = db.Conexao()
# load dict of arrays
data = load('dataset.npy')
# print the array

def salvar_imagem(nome, conta, metricas):
    array_str = ",".join(map(str, metricas))
    #print(array_str)
    sql = "INSERT INTO facial(nome, conta, data) VALUES('" + nome + "', " + str(conta) + " , cube(ARRAY[" + array_str + "]));"
    #print(sql)
    conn.manipular(sql)

for index, d in tqdm(enumerate(data)):
    try:
        salvar_imagem('Seed ' + str(index), 10, d)
    except Exception as e:
        print("Problema ao salvar ", e)
