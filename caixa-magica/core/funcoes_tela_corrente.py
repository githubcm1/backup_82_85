import sys
arq_status_tela = "/home/pi/caixa-magica-operacao/telaatual.txt"

def geraSaida(nome, conteudo):
    try:
        conteudo = str(conteudo)
        with open(arq_status_tela, "w") as fil:
            fil.write(conteudo)
    except Exception as e:
        pass

# registra em qual tela o sistema esta atualmente
def registraTelaAtual(nome_tela):
    try:
        geraSaida(arq_status_tela, nome_tela.strip())
    except:
        pass
