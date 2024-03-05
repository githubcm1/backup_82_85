# Importa a biblioteca do PyPI "psycopg2" (integracao com banco de dados PostegreSQL).
import psycopg2

# Importa a biblioteca padrao do Python "json" (encode e decode de arquivos JSON).
import json

# Da biblioteca padrao do Python "datetime" importa apenas a classe "datetime" (manipulacao de datas e horarios).
from datetime import datetime

# import json

# Da biblioteca padrao do Python "time" importa apenas a funcao "sleep".
from time import sleep

# Define o caminho do arquivo JSON de configuracao da aplicacao.
path = "/home/pi/caixa-magica-vars/config.json"

# Define o tempo de delay (interrupcao na execucao do script) com valor "0.005 segundos".
delay = 0.005

# Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
try:
    # Abre o arquivo JSON de configuracao da aplicacao e armazena o conteudo na variavel "json_data".
    with open(path) as json_data:
        # Converte o conteudo do arquivo JSON de configuracao da aplicacao em um array de nome "aux".
        aux = json.load(json_data)

        # Armazena o numero maximo de tentativas de execucao de uma instrucao SQL e armazena na variavel "num_tries".
        num_tries = aux['num_tentativas_db']
# Se ocorrer algum erro na abertura do arquivo JSON de configuracao da aplicacao...
except:
    # Considera como 3 o numero maximo de tentativas de execucao de uma instrucao SQL no banco de dados PostgreSQL local.
    num_tries = 3

# Classe de conexao com o banco de dados PostgreSQL local (do validador). 
class Conexao(object):
    # Inicializa a conexao com o banco de dados com valor "None" (sem valor).
    _db = None    
    
    # Metodo construtor da classe, chamado pelo metodo "__start__" quando a classe e instanciada.
    # (metodos com "__" no inicio e fim do nome sao os metodos especiais da classe e sao chamados automaticamente quando necessarios,
    # nao podendo ser chamados explicitamente pelo usuario).
    def __init__(self):
        # Abre uma conexao com o banco de dados PostgreSQL local e armazena no atributo "_db".
        self._db = psycopg2.connect(host="localhost", database="magica", user="postgres",  password="b2ml", options="-c statement_timeout=300000")

    # Metodo que grava as mensagens de erro geradas por esta classe no arquivo de log.
    def log_transacao(self, sql, dados, error):
        # Abre o arquivo de log de banco de dados no modo "append" e seta uma referencia a ela na variavel "fil".
        with open("/home/pi/caixa-magica-logs/logs_db.txt", "a") as fil:
            # Define o texto a ser adicionado ao arquivo de log com a data e hora atuais (UTC), a instrucao SQL executada,
            # os dados passados para a query e a mensagem de erro gerada.
            string = str(datetime.utcnow()) + " - Comando SQL: " + str(sql) + ", dados: " + str(dados) + ", exception: " + str(error)
            
            # Retira as quebras de linha do texto definido acima.
            string = string.replace('\\n', string)

            # Grava o texto definido acima no arquivo de log.
            fil.write(string)

            # Fecha a referencia ao arquivo de log.
            fil.close()

    def manipularComBind(self, sql, data):
        cnt = 0
        while cnt < num_tries:
            try:
                cur=self._db.cursor()
                cur.execute(sql, data)
                cur.close()
                self._db.commit()
                return True
            except Exception as e:
                cur.execute("rollback")
                self.log_transacao(sql, data, e)
                cnt = cnt +1
                sleep(delay)
        return False
    
    # Metodo para execucao de uma instrucao SQL de manipulacao de dados (insert, update, delete).
    def manipular(self, sql):
        # Inicializa o contador de tentativas de execucao da instrucao SQL com valor zero.
        cnt = 0

        # Enquanto o contador de tentativas de execucao da instrucao SQL for menor que o numero maximo de tentativas permitido...
        while cnt < num_tries:
            # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
            try:
                # Cria um cursor para a conexao com o banco de dados, o qual permitira executar as instrucoes SQL.
                cur=self._db.cursor()

                # Executa a instrucao SQL passada como parametro para o metodo.
                cur.execute(sql)

                # Fecha o cursor aberto acima.
                cur.close()

                # Executa o commit da transacao no banco de dados.
                self._db.commit()

                # Retorna true, indicando que a instrucao SQL foi executada corretamente.
                return True
            # Se ocorrer algum erro na execucao da instrucao SQL...
            except Exception as e:
                # Executa o rollback da transacao no banco de dados.
                cur.execute("rollback")

                # Grava a instrucao SQL e a mensagem de erro no arquivo de log de banco de dados.
                self.log_transacao(sql, "", e)

                # Soma um ao contador de tentativas de execucao da instrucao SQL.
                cnt = cnt + 1

                # Interrompe a execucao do script pelo tempo definido no inicio deste script.
                sleep(delay)
        
        # Se chegou aqui, e porque o numero de tentativas de execucao da instrucao SQL ja chegou ao limite. Neste caso,
        # retorna false, indicando que a instrucao SQL nao foi executada corretamente.
        return False
    
    # Metodo para execucao de uma instrucao SQL de consulta de dados (select).
    def consultar(self, sql):
        # Inicializa a variavel de resultset retornado pelo metodo com valor "None" (equivalente ao "null" no Python).
        rs = None

        # Inicializa o contador de tentativas de execucao da instrucao SQL com valor zero. 
        cnt = 0

        # Enquanto o contador de tentativas de execucao da instrucao SQL for menor que o limite de tentativas permitidas...
        while cnt < num_tries:
            # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
            try:
                # Cria um cursor para a conexao com o banco de dados, o qual permitira executar as instrucoes SQL.
                cur = self._db.cursor()
                
                # Executa a instrucao SQL passada como parametro para o metodo.
                cur.execute(sql)

                # Atribui a variavel de resultset todas os registros retornados pela execucao da instrucao SQL.
                rs = cur.fetchall()

                # Retorna o resultset.
                return rs
            # Se houve algum erro na execucao da instrucao SQL...
            except Exception as e:
                # Executa o rollback da transacao no banco de dados.
                cur.execute("rollback")

                # Grava a instrucao SQL e a mensagem de erro no arquivo de log de banco de dados.
                self.log_transacao(sql, "", e)

                # Soma um ao contador de tentativas de execucao da instrucao SQL.
                cnt = cnt + 1

                # Interrompe a execucao do script pelo tempo definido no inicio deste script.
                sleep(delay)
        
        # Se chegou aqui, e porque o numero de tentativas de execucao da instrucao SQL ja chegou ao limite. Neste caso,
        # retorna None, indicando que a instrucao SQL nao foi executada corretamente.
        return None
	
    def proximaPK(self, tabela, chave):
        sql='select max('+chave+') from '+tabela
        rs = self.consultar(sql)
        pk = rs[0][0]  
        return pk+1
    
    def fechar(self):
        self._db.close()

    def consultarComBind(self, sql, data):
        rs=None
        cnt = 0

        while cnt < num_tries:
            try:
                cur=self._db.cursor()
                cur.execute(sql, data)
                rs=cur.fetchall()
                return rs
            except Exception as e:
                cur.execute("rollback")
                self.log_transacao(sql, data, e)
                cnt = cnt + 1
                sleep(delay)
        return None
