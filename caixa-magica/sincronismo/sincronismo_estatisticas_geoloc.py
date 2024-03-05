import sys
path = '/home/pi/caixa-magica/core/'
sys.path.insert(1, path)
import db
import time
import datetime
import json

conn = db.Conexao()

INTERVALO_EXEC = 60 * 30 # A cada 30 minutos

try:
    with open(path + "../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        INTERVALO_EXEC = aux['intervalo_exec_estatistica_geoloc']
except:
    pass

EXEC = 1

while True:
    while EXEC <= 2:
        # Na execucao 1, pegamos as infos do dia atual
        # Na execucao 2, pegamos do dia anterior
        
        # Checamos em qual data estamos
        now = datetime.datetime.utcnow()
        now_detalhes = now

        if EXEC == 2:
            now = now - datetime.timedelta(days=1)

        now = now.strftime("%Y-%m-%d")

        try:
            # Agora que temos a data corrente, checamos os limite da data (em horarios)
            sql = """with intervalos as
                (
	            with q1 as 
	            (
	                select '"""+ str(now) + """'::date dat
	            )
	            select q1.dat, 
		           q1.dat + interval '3 hours' dat_ini,
		           q1.dat + interval '1 day 2 hours 59 minutes 59 seconds' dat_fim
	            from q1
                )
                select * from intervalos"""    
            result = conn.consultar(sql)
            for row in result:
                inicial = row[1]
                final = row[2]
        except:
            inicial = ""
            final = ""

        # ANALISE 1 Pegamos o total da data
        try:
            sql = """with q1 as
                (
                  select '""" + str(now) + """'::date dat,
                         sum(distancia_last_id_km) total
                  from historico_geoloc g
                  where g.dateinsert between '""" + str(inicial) + """' and '""" + str(final) + """'
                )
                select q1.dat, q1.total from q1
                """
            result = conn.consultar(sql)
            for row in result:
                sql = """insert into estatistica_total_km (dat, total_km, dateinsert)
                     values ('""" + str(now) + """', """ + str(row[1]) + """, '""" + str(now_detalhes) + """')
                     on conflict (dat) do update set total_km = """ + str(row[1]) + """, 
                          dateupdate = '""" + str(now_detalhes) + """'"""
                conn.manipular(sql)
        except:
            pass

        # ANALISE 2: pegamos o total da data por motorista 
        try:
            sql = """select g.motoristaid,
                        o.nome,
                        sum(distancia_last_id_km) total
                 from historico_geoloc g,
                      operadores o
                 where o.id_web = g.motoristaid
                   and g.dateinsert between '""" + str(inicial) + """' and '""" + str(final) + """'
                   and g.viagemid <> ''
                 group by g.motoristaid, o.nome
              """
            result = conn.consultar(sql)
            for row in result:
                sql = """insert into estatistica_total_motorista_km
                       (dat, motoristaid, motorista, total_km, dateinsert)
                     values ('""" + str(now) + """', """ + str(row[0]) + """,
                             '""" + str(row[1]) + """', """ + str(row[2]) + """,
                             '""" + str(now_detalhes) + """')
                     on conflict (dat, motoristaid) do
                     update set total_km =""" + str(row[2]) + """,
                                dateupdate = '""" + str(now_detalhes) + """'"""
                conn.manipular(sql)
        except:
            pass

        # ANALISE 3: pegamos o total por viagem
        try:
            sql = """select g.motoristaid,
                        o.nome,
                        v.id_viagem_cm,
                        v.linha_id,
                        l.codigopublico,
                        sum(distancia_last_id_km) total
                 from historico_geoloc g,
                      operadores o,
                      viagem v,
                      linhas l
                 where g.motoristaid = o.id_web
                   and v.id_viagem_cm = g.viagemid
                   and l.id = v.linha_id
                   and g.dateinsert between '""" + str(inicial) + """' and '""" + str(final) + """'
                 group by g.motoristaid, o.nome, v.id_viagem_cm, v.linha_id, l.codigopublico
              """
            result = conn.consultar(sql)
            for row in result:
                sql = """insert into estatistica_total_viagem_km (dat, motoristaid, motorista, id_viagem_cm,
                            linha_id, codigopublico, total_km, dateinsert)
                        values ('""" + str(now) + """', """ + str(row[0]) + """, '""" + str(row[1]) + """',
                                '""" + str(row[2]) + """', """ + str(row[3]) + """, '""" + str(row[4]) + """',
                                """ + str(row[5]) + """, '""" + str(now_detalhes) + """')
                            on conflict (dat, motoristaid, id_viagem_cm)
                            do update set dateupdate='""" + str(now_detalhes) +"""', 
                                          total_km = """ + str(row[5])
                conn.manipular(sql)
        except:
            pass

        # ANALISE 4: pegamos o total por linha
        try:
            sql = """select v.linha_id,
                        l.codigopublico,
                        sum(distancia_last_id_km) total
                 from historico_geoloc g,
                      viagem v,
                      linhas l
                 where g.viagemid = v.id_viagem_cm
                   and l.id = v.linha_id
                   and g.dateinsert between '""" + str(inicial) + """' and '""" + str(final) + """'
                 group by v.linha_id, l.codigopublico
               """
            result = conn.consultar(sql)
            for row in result:
                sql = """insert into estatistica_total_linha_km (dat, linha_id, codigopublico, 
                        total_km, dateinsert)
                     values ('""" + str(now) + """', """ + str(row[0]) + """, '""" + str(row[1]) + """',
                             """ + str(row[2]) + """, '""" + str(now_detalhes) + """')
                     on conflict (dat, linha_id) do
                     update set dateupdate ='""" + str(now_detalhes) + """',
                                total_km = """ + str(row[2])
                conn.manipular(sql)
        except:
            pass

	# ANALISE 5: pega o total por status de viagem
        try:
            sql = """select x.dat,
	                x.status_viagem,
	                sum(x.tot) tot
                 from
                 (   
	            select '""" + str(now) + """' dat,
		           case when g.viagemid <> '' then 'ABERTA' else 'FECHADA' end status_viagem,
		           g.distancia_last_id_km tot
	            from historico_geoloc g
	            where g.dateinsert between '""" + str(inicial) + """' and '""" + str(final) + """'
                 ) x
                 group by x.dat,
	                 x.status_viagem"""
            result = conn.consultar(sql)
            for row in result:
                sql = """insert into estatistica_total_status_viagem_km (dat, status_viagem, total_km, dateinsert)
                     values ('""" + str(now) + """', '""" + str(row[1]) + """', """ + str(row[2]) + """, 
                             '""" + str(now_detalhes) + """')
                     on conflict (dat, status_viagem) do
                     update set dateupdate = '""" + str(now_detalhes) + """',
                                total_km = """ + str(row[2])
                conn.manipular(sql)
        except:
            pass

        EXEC = EXEC +1

        if EXEC > 2:
            EXEC = 1
            time.sleep(INTERVALO_EXEC)
