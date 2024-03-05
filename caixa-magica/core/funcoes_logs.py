# Importa a biblioteca padrao do Python "sys" (execucao de funcoes especificas do sistema).
import sys

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Da biblioteca padrao do Python "datetime" importa apenas a classe "datetime" (manipulacao de datas e horarios).
from datetime import datetime

# Define o caminho do diretorio de arquivos de log do validador.
path_logs = "/home/pi/caixa-magica-logs/"

# Define o caminho do diretorio deste script.
path_atual = "/home/pi/caixa-magica/core"

# Insere nos paths do sistema o path do diretorio deste script.
# Caminho do diretorio: /home/pi/caixa-magica/core
sys.path.insert(1, str(path_atual))

# Do diretorio local "core" importa o arquivo "db.py".
import db

# Importa este proprio script com o alias "insere_logs", para permitir a chamada de funcoes deste script dentro de outras funcoes.
import funcoes_logs as insere_logs

# Do diretorio local "core" importa o arquivo "funcoes_serial.py".
# Caminho do script: /home/pi/caixa-magica/core/funcoes_serial.py
import funcoes_serial

# Abre uma conexao com o banco de dados PostgreSQL local.
conn = db.Conexao()

# Funcao que insere um registro na tabela de logs.
def insere_log(log, local, severidade = 0):
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Define a instrucao SQL que insere um registro na tabela "logs" do banco de dados PostgreSQL local, de acordo com os parametros
        # passados para a funcao.
        sql = "insert into public.logs (string_log, local, severidade) values ('{}', '{}', {})".format(str(log).replace("'", ""), str(local), str(severidade))
        
        # Executa a instrucao SQL de insercao do registro na tabela "logs".
        conn.manipular(sql)
    # Se ocorrer algum erro na insercao do registro na tabela "logs"...
    except:
        # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
        # ser substituido por outra instrucao futuramente.
        pass

# Rotina que busca dos logs registrados no BD, e gera a saida em arquivos separados
def gera_arqs_logs(local):
    insere_logs.insere_log("Iniciando gera_arqs_logs para arquivos de logs separados", local)

    serial = funcoes_serial.getSerial()
    insere_logs.insere_log("Serial obtido: " + str(serial), local )

    path_arqs = path_atual + "/../../caixa-magica-logs/"

    sql = """select l.id, 
                    to_char(l.dateinsert, 'yyyy-mm-dd hh24:mi:ss:ms') dat, 
                    l.string_log, 
                    concat(local, '.log') path_log 
             from logs l 
             where l.arq_log_exportado is null 
             order by 1"""
    result = conn.consultar(sql)
    insere_logs.insere_log("Resultado do sql: " + str(len(result)) + " registros.", local)

    for row in result:
        #insere_logs.insere_log("Lendo registro de log id " + str(row[0]), local)
        path_arquivo = path_arqs + row[3]
        string_linha = serial + ";" + row[1] + ";" + row[2] + "\n"

        try:
            with open(path_arquivo, "a") as arq:
                arq.write(string_linha)
            dados = (str(row[3]), str(row[0]), ) 
            sql = "update logs set arq_log_exportado=%s where id = %s"
            conn.manipularComBind(sql, dados)
        except Exception as e:
            insere_logs.insere_log("Erro ao inserir log em " + path_arquivo + ": " + str(e), local)

# Rotina que busca dos logs registrados no BD, e gera a saida log consolidado
# Notacao do LOG:
# serial;local do log;timestamp ocorrencia;ocorrencia
#
#
#
def gera_arq_log_unico(local):
    insere_logs.insere_log("Iniciando gera_arq_log_unico para arquivo de log unificado", local)

    serial = funcoes_serial.getSerial()
    insere_logs.insere_log("Serial obtido: " + str(serial), local )

    path_arqs = path_atual + "/../../caixa-magica-logs/"
    arquivo = "log_consolidado.log"

    sql = """select l.id, 
                    to_char(l.dateinsert, 'yyyy-mm-dd hh24:mi:ss:ms') dat, 
                    l.string_log, 
                    concat(local, '.log') path_log 
             from logs l 
             where l.arq_log_exportado is not null 
               and arq_log_exportado_unico is null 
             order by 1"""
    insere_logs.insere_log("Efetuando consulta sql: " + sql, local)
    result = conn.consultar(sql)
    insere_logs.insere_log("Resultado do sql: " + str(len(result)) + " registros.", local)

    for row in result:
        path_arquivo = path_arqs + arquivo
        string_linha = serial + ";" + row[3] + ";" + row[1] + ";" + row[2] + "\n"

        try:
            with open(path_arquivo, "a") as arq:
                arq.write(string_linha)
            
            dados=(str(arquivo), str(row[0]),)
            sql = "update logs set arq_log_exportado_unico=%s where id = %s"
            conn.manipularComBind(sql, dados)
        except Exception as e:
            insere_logs.insere_log("Erro ao inserir log em " + path_arquivo + ": " + str(e), local)

# Rotina que expurga logs com muito tempo sem uso
def expurga_logs_legados(local):
    expurga_logs_legados_files()

    insere_logs.insere_log("Iniciando expurgo logs legados", local)

    INTERVALO = 5 # EM DIAS

    try:
        with open(path_atual + "/../../caixa-magica-vars/config.json") as json_data:
            aux = json.load(json_data)
            INTERVALO = aux['intervalo_dias_expurgo_logs_legados']
    except:
        pass

    try:
        insere_logs.insere_log("Intervalo de dias para expurgo: " + str(INTERVALO), local)
        sql = "delete from logs where dateinsert < now() - interval '" + str(INTERVALO) + " days'"
        conn.manipular(sql)
        insere_logs.insere_log("Expurgo efetuado com comando SQL: " + sql, local)
    except:
        insere_logs.insere_log("Erro expurgo tabela logs: " + str(e), local)
    return

def expurga_logs_legados_files():
    try:
        os.system("sudo find /home/pi/caixa-magica-logs/*.tar.gz -mtime +7 -a -mtime -360 | sudo tee /home/pi/caixa-magica-logs/logs-del.txt")
        with open("/home/pi/caixa-magica-logs/logs-del.txt") as f:
            for line in f:
                os.system("sudo rm -f " + line.strip() )

        os.system("sudo rm -f /home/pi/caixa-magica-logs/logs-del.txt")
    except:
        pass

# Rotina que expurga os logs ja enviados
def expurga_logs_enviados(local):
    insere_logs.insere_log("Iniciando expurgo tabela logs (registros enviados para o servidor", local)

    try:
        insere_logs.insere_log("Abrindo conexao com o PostgreSQL", local)

        sql = "delete from logs where data_envio_servidor is not null"
        conn.manipular(sql)

        insere_logs.insere_log("Expurgo tabela logs efetuado com sucesso", local)
    except Exception as e:
        insere_logs.insere_log("Erro expurgo tabela logs: " + str(e), local)


# Rotina utilizada para determinar o nome do arquivo de log a ser gravado
def determina_nome_log(sufixo):
    now = datetime.utcnow()
    now_yyyymmdd = now.strftime("%Y%m%d")
    return path_logs + now_yyyymmdd + "_" + str(sufixo) + ".log"

# Rotina utilizada para registrar o log com fato
def registra_linha_log_arquivo(nome_arq, ocorrencia):
    registro = str(datetime.utcnow()) + "|" + str(ocorrencia).strip() + "\r\n"

    try:
        with open(nome_arq, "a") as f:
            f.write(registro)
    except Exception as e:
        pass
        #print(str(e))

