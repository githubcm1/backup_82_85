# Importa a biblioteca padrao do Python "os" (execucao de instrucoes do sistema operacional).
import os

# Funcao que retorna se esta maquina e uma Raspberry PI ou nao (valor booleano).
def getRaspPI():
    # Inicia uma instrucao "try-catch" para tratar possiveis erros nas proximas instrucoes.
    try:
        # Abre o arquivo "/proc/cpuinfo" no modo leitura (parametro "r") e cria uma referencia chamada "f" para ele.
        with open('/proc/cpuinfo', 'r') as f:
            # Para cada linha do arquivo aberto atribui o conteudo da linha a variavel "line".
            for line in f:
                # Se o conteudo da linha contiver a string "Raspberry"...
                if 'Raspberry' in line:
                    # Retorna "True", indicando que a maquina e uma Raspberry PI.
                    return True
    # Se ocorrer algum erro na abertura e leitura do arquivo "/proc/cpuinfo"...
    except:
        # Utiliza uma instrucao "pass" como "placeholder", para nao ocasionar erro no "try-catch" e poder
        # ser substituido por outra instrucao futuramente.
        pass
    
    # Se chegou ate aqui e porque ou ocorreu um erro na leitura do arquivo "/proc/cpuinfo" ou a string "Raspberry" nao
    # foi encontrada. Nesse caso, retorna "False", indicando que a maquina nao e uma Raspberry PI.
    return False


def getSerial():
    cpuserial = ''

    # Se for uma raspberry
    if getRaspPI():
        try:
            with open ('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        cpuserial = line[10:26]
                f.close()
        except:
            cpuserial = 'Error'
    # mas se for
    else:
        try:
            with open('/sys/class/net/eth0/address') as f:
                for line in f:
                    cpuserial = line.strip()
                    break
        except:
            pass

        if cpuserial == "":
            try:
                x= os.popen('cat /sys/class/net/enp1s0/address').read().strip()
                cpuserial = x.strip()
            except:
                pass

    cpuserial = cpuserial.replace(":","-")
    return cpuserial

