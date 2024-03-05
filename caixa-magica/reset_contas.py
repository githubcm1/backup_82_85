import sys

sys.path.insert(1, '/home/pi/caixa-magica/core/')
import db

conn = db.Conexao()

s = "truncate table facial"
conn.manipular(s)

s = """select pt.tablename from pg_catalog.pg_tables pt
where pt.tablename like 'facial_linha%' and pt.tablename not like '%_p_%'"""
result = conn.consultar(s)

for row in result:
    s = "truncate table " + row[0]
    print(s)
    conn.manipular(s)

s = "truncate table contas_controle_saldos"
conn.manipular(s)

s = "delete from contas"
conn.manipular(s)
