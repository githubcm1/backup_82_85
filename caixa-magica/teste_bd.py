from core import db

global conn
conn = db.Conexao()

sql = "select 1'"
conn.consultar(sql)

sql = "select 2"
print("2")
result =conn.consultar(sql)
print(result)

sql = "select 3"
result = conn.consultar(sql)
print(result)

sql = "select 4 from dsadsa"
result = conn.consultar(sql)
print(result)

sql = "select 5"
result = conn.consultar(sql)
print(result)

sql = "select %s"
dados=("12", "13", )
result = conn.consultarComBind(sql, dados)

sql = "select 6"
result = conn.consultar(sql)
print(result)
