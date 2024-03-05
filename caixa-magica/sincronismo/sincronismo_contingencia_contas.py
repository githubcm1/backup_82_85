import json
import sys
import time
from datetime import datetime, timedelta

path_atual = '/home/pi/caixa-magica/core'
sys.path.insert(1, path_atual)
import db

path_sincronismo        = '/home/pi/caixa-magica-operacao/sincronismo.json'
path_sincronismo_facial = '/home/pi/caixa-magica-operacao/sincronismo_facial.json'

HORA_DE = 10
HORA_ATE = 13

try:
    with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
        aux = json.load(json_data)
        HORA_DE = aux['hora_de_contingencia_contas']
        HORA_ATE = aux['hora_ate_contingencia_contas']
except:
    pass

try:
    executa = False
    conn = db.Conexao()

    # checamos se estamos no horário de execucao
    now = datetime.utcnow()
    hora = int(now.strftime("%H"))
    dat1 = now.strftime("%Y%m%d")

    # Se esta no intervalo de execucao
    if hora >= HORA_DE and hora <= HORA_ATE: 
        executa = True

        # Checamos no BD se ja houve uma execucao no dia
        dados = (dat1,)
        sql = """select 1 
                 from controle_execucoes_diarias 
                 where acao = 'CONTINGENCIA_CONTAS'
                   and data_acao = %s
              """
        result = conn.consultarComBind(sql, dados)
    
        for row in result:
            executa = False

    # Se permite executar
    if executa:
        with open(path_sincronismo) as dat:
            aux = json.load(dat)
            
            # Se estamos num domingo, aplicamos a contingencia de 7 dias
            if now.weekday() == 6:
                dias = 7
            else:
                dias = 1
            
            nova_sync = datetime.utcnow() - timedelta(days=dias)
            nova_sync = datetime.strftime((nova_sync), "%Y-%m-%d") + "T00:00:00"
            aux['lastSyncAtualizacao']= nova_sync

            sql = "insert into controle_execucoes_diarias (acao, data_acao) values (%s, %s)"
            dados = ('CONTINGENCIA_CONTAS', dat1,)
            conn.manipularComBind(sql, dados)

        try:
            with open(path_sincronismo, 'w') as f:
                f.write(json.dumps(aux))
                f.close()
        except:
            pass

    # Se esta no intervalo de execucao
    if hora >= HORA_DE and hora <= HORA_ATE: 
        executa = True

        # Checamos no BD se ja houve uma execucao no dia
        dados = (dat1,)
        sql = """select 1 
                 from controle_execucoes_diarias 
                 where acao = 'CONTINGENCIA_FACIAL'
                   and data_acao = %s
              """
        result = conn.consultarComBind(sql, dados)
    
        for row in result:
            executa = False

    # Se permite executar
    if executa:
        with open(path_sincronismo_facial) as dat:
            aux = json.load(dat)
            
            # Se estamos num domingo, aplicamos a contingencia de 7 dias
            if now.weekday() == 6:
                dias = 7
            else:
                dias = 1
            
            nova_sync = datetime.utcnow() - timedelta(days=dias)
            nova_sync = datetime.strftime((nova_sync), "%Y-%m-%d") + "T00:00:00"
            aux['lastUpdateTime']= nova_sync

            sql = "insert into controle_execucoes_diarias (acao, data_acao) values (%s, %s)"
            dados = ('CONTINGENCIA_FACIAL', dat1,)
            conn.manipularComBind(sql, dados)

        try:
            with open(path_sincronismo_facial, 'w') as f:
                f.write(json.dumps(aux))
                f.close()
        except:
            pass

    del conn
except Exception as e:
    print(str(e))

