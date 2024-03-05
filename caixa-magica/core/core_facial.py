import sys
from datetime import datetime

path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_logs
import cobranca


def process_facial(data):
    if (data['type'] == 'facial' and not PROCESSANDO_IMAGEM and not PROCESSANDO_PAGAMENTO and not PROCESSANDO_BOTAO):
        PROCESSANDO_IMAGEM = True
        PROCESSANDO_PAGAMENTO = True
        global initial

        initial = datetime.datetime.now()

        try:
            metricas = recog.get_metricas(data['path'])
            permite_cobranca_facial = False

            dt_rec_facial_initial = datetime.datetime.now()
            user = database.get_user(metricas)
            dt_rec_facial_final = datetime.datetime.now()
            funcoes_logs.insere_log("Info do usuario: " + str(user), local, 2)

            rate = database.get_rate(user)
            range_analise = user[2]

            # insere na tabela de controle de testes
            foto_path = data['path']

            if (rate == 1 and user and PROCESSANDO_IMAGEM and PROCESSANDO_PAGAMENTO):
                funcoes_logs.insere_log("Pessoa identificada na base de dados.", local, 2)

                if CHECK_MASK == True:
                    if check_mouth.check_mouth_exists(data['path']) == True:
                        funcoes_logs.insere_log("Boca detectada na imagem " + data['path'], local, 2)
                        permite_cobranca_facial = True
                    else:
                        funcoes_logs.insere_log("Boca não detectada na imagem " + data['path'],local, 2)
                        permite_cobranca_facial = False
                else:
                    funcoes_logs.insere_log("Flag de mascara não ativo em config.json. Análise da mascara não sera efetuada na checagem da foto.",local, 2)
                    permite_cobranca_facial = True

                if permite_cobranca_facial == False:
                    funcoes_logs.insere_log("Cobrança não permitida para usuario " + str(user) + ". Boca não detectada na imagem " + data['path'], local, 2)
                else:
                    with open(data['path'], 'rb') as img:
                        string = base64.b64encode(img.read())

                    idConta = user[1]
                    funcoes_logs.insere_log("Entrando em getLiberadoSaldo",local, 2)
                    liberado = cobranca.getLiberadoSaldo(idConta)

                    nomeExibicao = str(user[0]).split(" ")

                    if liberado:
                        # Cria um objeto tkinter para iniciar a saudacao
                        root = inicia_show_saudacao()
                        saudacao = retorna_saudacao()

                        if not EXIBE_NOME_CATRACA:
                            nomeExibicao[0] = ""

                        # Mostra o saldo
                        if EXIBE_SALDO_CATRACA:
                            saudacao2 =cobranca.formaMensagemSaldoPosPassagem(idConta)
                        else:
                            saudacao2 = ""

                        # Exibe a tela
                        show_saudacao(root, "green2", "white",saudacao, nomeExibicao[0], 300,36,"green2", saudacao2)

                        funcoes_logs.insere_log("Checando liberacao catraca", local, 2)
                        passou = database.liberar( )

                        # Se a catraca foi girada, entao aqui aplicamos a cobranca
                        if passou:
                            funcoes_logs.insere_log("Cliente liberado: "+ str(user[0]) + " imagem: " + data['path'], local, 2)
                            fluxo_cobranca(FLAG_CATRACA_TIMEOUT,idConta,ULTIMO_IDWEB,string,True, metricas, range_analise )

                        # Fecha a tela de saudacao
                        encerra_show_saudacao(root)

                        FLAG_CATRACA_TIMEOUT = not passou
                        ULTIMO_IDWEB = user[1]

                        sleep(2)
                    else:
                        if EXIBE_NOME_SALDO_INSUFICIENTE:
                            compl_saldo_insuf = "\n\n" + nomeExibicao[0]
                        else:
                            compl_saldo_insuf = ""

                        funcoes_logs.insere_log("Usuario sem saldo, mostrando tela de bloqueio", local, 2)
                        cfgTelas("red2","white","Saldo Insuficiente" + compl_saldo_insuf,"",350,3000,32,"red2")
                        sleep(2)

            elif rate == 2:
                count += 1
                if count == 4:
                    funcoes_logs.insere_log("Erro de leitura facial, necessário QR CODE", local,3)
                    cfgTelas("orange red", "white", "Nao conseguimos\nidentificar voce no\nnosso sistema\n\n\nPor favor, utilize\no QR Code gerado\npelo App", "", 350, 3500, 28, "orange red")
                    count  = 0
                    sleep(6)
                sleep(0.001)

            elif rate == 3:
                count += 1
                if count == 2:
                    funcoes_logs.insere_log("Face não consta no banco de dados", local, 3)
                    cfgTelas("red2","white","Nao consta no banco de dados","",350,3000,32,"red2")
                    count = 0
                    sleep(3)
                sleep(0.001)
        except Exception as e:
            funcoes_logs.insere_log("Erro no reconhecimento ou na consulta " + str(e), local, 3 )
            print("Erro: " + str(e))
        PROCESSANDO_IMAGEM = False
        PROCESSANDO_PAGAMENTO = False


process_facial([])
