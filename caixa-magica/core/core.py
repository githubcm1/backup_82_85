'''
Core da caixa mágica
'''
import multiprocessing
import sys
path_atual = "/home/pi/caixa-magica/core"
sys.path.insert(1, path_atual)
import funcoes_tela_corrente
import funcoes_core
import funcoes_matrizes_memoria

# Zera mensagem de tela
funcoes_core.zera_mensagem_process()

# Mudamos o status do core para OFF
funcoes_core.zera_status_core()

import socket
import json
import recog
import operacoes as database

import threading
import datetime
import cobranca

import os
import base64
import check_mouth
import db
import funcoes_qrcode
import funcoes_logs
import funcoes_viagem
import funcoes_camera
import funcoes_elastic
from time import sleep

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import *

sys.path.insert(2, path_atual + "/../tela/")

sys.path.insert(3, path_atual + "/../discord/")
import functions_discord

global PROCESSANDO_IMAGEM
global PROCESSANDO_PAGAMENTO
global PROCESSANDO_BOTAO
PROCESSANDO_IMAGEM = False
PROCESSANDO_PAGAMENTO = False
PROCESSANDO_BOTAO = False
global count
count = 0

global FLAG_CATRACA_TIMEOUT
global ULTIMO_IDWEB
FLAG_CATRACA_TIMEOUT = False
ULTIMO_IDWEB = 0

local = 'core.py'
funcoes_logs.insere_log("Iniciando " + local, local, 2)

# Ativa o processo dos botoes de gratuidade e dinheiro
os.system("sudo pkill -9 -f botoes.py")
os.system("sudo python3 "+path_atual+"/../botoes.py &")

# remove o lock logico da catraca, para que os botoes funcionem novamente
database.remove_espera_catraca()

# Busca o id do ultimo usuario da viagem
aux_registro_viagem_id  = funcoes_viagem.get_viagem_atual()

# Busca o id da linha atual
idLinha = funcoes_viagem.get_linha_atual()

# Pega o ultimo ID de cliente que passou pela catraca nesta viagem
if aux_registro_viagem_id != "":
    connAux  =db.Conexao()

    sql  = """select coalesce(max(co.contaid),0)
              from cobrancas co
              where co.id in 
              (
	        select max(id) id
	        from cobrancas c 
	        where c.viagemid = %s
	          and c.contaid is not null
              )"""
    dados = (str(aux_registro_viagem_id), )
    result = connAux.consultarComBind(sql, dados)

    for row in result:
        ULTIMO_IDWEB = row[0]
    del connAux

# Definimos aqui se a ultima passagem foi de um PCD
global ULTIMO_PASSAGEIRO_PCD
ULTIMO_PASSAGEIRO_PCD = False

# Checamos no BD se o ultimo passageiro DESTA VIAGEM foi um PCD
ULTIMO_PASSAGEIRO_PCD = funcoes_viagem.get_ultimo_passageiro_pcd()

# Cria diretorio
os.system("sudo mkdir -p /home/pi/caixa-magica-img-rec/")

CHECK_MASK = False

# Abre arquivo de configuracoes, de forma a identificar os limites da viagem
with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    config = json.load(json_data)

    # Obtem flag de checagem de mascara
    try:
        CHECK_MASK = config['rec_facial']['check_mask']
    except:
        pass

    try:
        EXIBE_NOME_CATRACA = config['exibe_nome_catraca']
    except:
        EXIBE_NOME_CATRACA = False

    try:
        EXIBE_SALDO_CATRACA = config['exibe_saldo_catraca']
    except:
        EXIBE_SALDO_CATRACA= False

    try:
        EXIBE_NOME_SALDO_INSUFICIENTE = config['exibe_nome_saldo_insuficiente']
    except:
        EXIBE_NOME_SALDO_INSUFICIENTE = False

    try:
        ID_CONTA_MOCK_REC_FACIAL = config['id_conta_mock_rec_facial']
    except:
        ID_CONTA_MOCK_REC_FACIAL = ""

#################################################################
#  funcao tem por objetivo definir o padrao de tela
#  parametro: background - cor de fundo
#                   foreground   - core de primeiro plano
#                   texto1  - primeira linha de texto a ser impressa
#                   texto2  - segunda linha de texto a ser impressa
#################################################################
def cfgTelas(background,foreground,texto1, texto2,ipady = 350,tempo = 3000, tamanho = 36, fundo = "green2"):
    root = Tk()
    widget = Frame(root)
    root.configure(background = fundo)
    root.attributes("-fullscreen",True)
    widget.pack()
    localString = texto1

    if (len(texto2)>0):
        localString +=  '\n ' + texto2

    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana',tamanho,'bold'))

    msg.grid(row=0,column=1,ipady=ipady)
    root.after(tempo, lambda: root.destroy())
    root.mainloop()


#################################################################
#  funcao tem por objetivo retornar a saudacao referente ao periodo de 24h
#  00h00 - 11h59        bom dia
#  12h00 - 17h59        boa tarde
#  18h00 - 23h59        boa noite
#################################################################
def retorna_saudacao():
    now = datetime.datetime.now()
    saudacao = ""
    if (now.hour < 12):
        saudacao = "Bom Dia"
    elif(now.hour < 18):
        saudacao = "Boa Tarde"
    else:
        saudacao = "Boa Noite"
    return saudacao

def inicia_show_saudacao():
    root = Tk()
    return root

def show_saudacao(root, background,foreground,texto1, texto2,ipady = 350, tamanho = 36, fundo = "green2", texto3 = ""):
    funcoes_logs.insere_log("Exibindo tela show_saudacao()", local, 2)

    funcoes_tela_corrente.registraTelaAtual("TELA_SAUDACAO_CLIENTE")

    global aux_catraca
    aux_catraca = True
    widget = Frame(root)
    root.configure(background = fundo)
    root.attributes("-fullscreen",True)
    widget.pack()
    localString = texto1

    if (len(texto2)>0):
        localString +=  '\n ' + texto2

    if (len(texto3) > 0):
        localString += '\n' + texto3

    localString += "\n\nCatraca liberada"

    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana',tamanho,'bold'))
    msg.grid(row=0,column=1,ipady=ipady)
    root.update()

def show_catraca_liberada(background,foreground,ipady = 350, tamanho = 36, fundo = "light blue"):
    if not CONFIG['exibe_catraca_liberada']:
        return
    root = inicia_show_saudacao()
    funcoes_logs.insere_log("Exibindo tela show_catraca_liberada()", local, 2)
    global aux_catraca
    aux_catraca = True
    widget = Frame(root)
    root.configure(background = fundo)
    root.attributes("-fullscreen",True)
    widget.pack()
    localString = "Catraca liberada"

    msg = Label(widget, text= localString,fg=foreground,bg=background,font=('Verdana',tamanho,'bold'))
    msg.grid(row=0,column=1,ipady=ipady)

    root.after(2000, lambda: root.destroy())
    root.mainloop()


def encerra_show_saudacao(root):
    try:
        root.destroy()
    except:
        pass

    try:
        root.update()
    except:
        pass

def fluxo_cobranca(f_catraca_timeout,contaId,ultimo_usuario,foto,por_valor, matriz_facial, range_analise):
    global ULTIMO_PASSAGEIRO_PCD
    usuario_atual = contaId

    if not f_catraca_timeout: 
    #Se não houve timeout da catraca na última utilizacao
    #Cobrar
        cobranca.cobrar({'idConta':contaId, 'porValor':por_valor, 'id_web': contaId, 'tipoIdentificacao': 3, 'foto': foto.decode('utf-8'), 'matriz_facial': matriz_facial, 'range_analise': range_analise})
        funcoes_logs.insere_log("Cobranca Realizada", local, 2)
    
    # Efetuamos a cobranca
    else: 
        cobranca.cobrar({'idConta':contaId, 'porValor':por_valor, 'id_web': contaId, 'tipoIdentificacao': 3, 'foto': foto.decode('utf-8'), 'matriz_facial': matriz_facial, 'range_analise': range_analise})
        funcoes_logs.insere_log("Cobranca Realizada", local, 2)                 

def fluxo_cobrancaQRcode(f_catraca_timeout,ultimo_usuario,data):
    # se a pessoa for acompanhante e o ultimo usuario for um pcd, entao este caso nao deve gerar cobranca
    
    if not f_catraca_timeout: 
    #Se não houve timeout da catraca na última utilizacao
    #Cobrar
        cobranca.cobrarQRcode(data)
        funcoes_logs.insere_log("Cobranca Realizada", local, 2)
        return
    else: 
        cobranca.cobrarQRcode(data)
        funcoes_logs.insere_log("Cobranca Realizada", local, 2)                 
        return

def process(data):
    global PROCESSANDO_IMAGEM
    global PROCESSANDO_PAGAMENTO
    global PROCESSANDO_BOTAO
    global FLAG_CATRACA_TIMEOUT
    global ULTIMO_IDWEB
    global count

    # Se o semaforo estiver ativo, quer dizer que tem algum processamento facial ou de QR Code.
    # Neste caso, travar as demais acoes
    if funcoes_viagem.semaforo_ativo():
        return
    
    # Se ainda esta processando a cobranca, nao prosseguimos aqui
    if funcoes_camera.get_status_cobranca():
        return

    rate = 0

    if (data['type'] == 'facial' and not PROCESSANDO_IMAGEM and not PROCESSANDO_PAGAMENTO and not PROCESSANDO_BOTAO):
        global initial
        initial = datetime.datetime.now()
        
        try:
            funcoes_core.atualiza_mensagem_process("OBTENDO INFO FACIAL, AGUARDE...")

            if ID_CONTA_MOCK_REC_FACIAL == "":
                #print(str(data['var_sessao']) + " " + str(datetime.datetime.now())+ " Ini Metricas")
                metricas = recog.get_metricas(data['path'])
                print("Tamanho metrica: " + str(len(metricas)))
                #print(",".join(map(str,metricas)))

                permite_cobranca_facial = False
                #print(str(data['var_sessao']) + " " + str(datetime.datetime.now())+ " Fim Metricas: " + str(metricas))

                # Inclui as metricas na checagem de matrizes e calcula a media de proximidade
                #media_proximidade = funcoes_matrizes_memoria.calcula_dist_matrizes(metricas, 2, 0.1, 0.38)
                #print("Media prox: " + str(media_proximidade))
                
                #if media_proximidade < 0.22:
                #   return
                #return

            # Atraves da imagem, checamos se foi possivel obter as metricas
            if ID_CONTA_MOCK_REC_FACIAL != "":
                funcoes_core.atualiza_mensagem_process("IDENTIFICANDO PESSOA, AGUARDE...")
                user = []
                user.append("") # Nome
                user.append(ID_CONTA_MOCK_REC_FACIAL) # id da conta
                user.append(1) # range
                rate = 1
                
                # insere na tabela de controle de testes
                foto_path = data['path']

                # Registra em tela o reconhecimento
                funcoes_core.atualiza_mensagem_process("PESSOA IDENTIFICADA, AGUARDE...")

                #Forca um sleep com o tempo aproximado do rec facial dlib (0.15s) + retorno elastic (0.15s)
                sleep(0.3)

            elif len(metricas) > 0:
                funcoes_core.atualiza_mensagem_process("IDENTIFICANDO PESSOA, AGUARDE...")
                dt_rec_facial_initial = datetime.datetime.now()
                
                # Atraves da metrica obtida, analisamos dentro do Elastic Search para encontrar a pessoa
                retorno_user = funcoes_elastic.consulta_matriz_facial_thread(metricas, idLinha)
                print("Retorno User: " + str(retorno_user) )

                # Se encontrou a pessoa na base de dados
                if len(retorno_user) > 0:
                    range_analise = retorno_user[0][3] # MUDAR DEPOIS
                    user = []
                    user.append(retorno_user[0][5]) # Nome
                    user.append(retorno_user[0][0]) # id da conta
                    user.append(range_analise) # range
                    rate = 1

                    # insere na tabela de controle de testes
                    foto_path = data['path']

                    # Registra em tela o reconhecimento
                    funcoes_core.atualiza_mensagem_process("PESSOA IDENTIFICADA, AGUARDE...")
            else:
                rate = 2

                # Registra em tela o nao reconhecimento
                funcoes_core.atualiza_mensagem_process("PESSOA NAO IDENTIFICADA")

            if (rate == 1 and user): # and PROCESSANDO_IMAGEM and PROCESSANDO_PAGAMENTO):
                if CHECK_MASK == True:
                    if check_mouth.check_mouth_exists(data['path']) == True:
                        funcoes_logs.insere_log("Boca detectada na imagem " + data['path'], local, 2)
                        permite_cobranca_facial = True
                    else:
                        funcoes_logs.insere_log("Boca não detectada na imagem " + data['path'],local, 2)
                        permite_cobranca_facial = False
                else:
                    permite_cobranca_facial = True

                if permite_cobranca_facial == False:
                    funcoes_logs.insere_log("Cobrança não permitida para usuario " + str(user) + ". Boca não detectada na imagem " + data['path'], local, 2)
                else:
                    idConta = user[1]

                    # Registra em tela o reconhecimento
                    funcoes_core.atualiza_mensagem_process("CHECANDO SALDO, AGUARDE...")

                    funcoes_logs.insere_log("Entrando em getLiberadoSaldo",local, 2)
                    liberado = cobranca.getLiberadoSaldo(idConta)

                    PROCESSANDO_IMAGEM = True
                    PROCESSANDO_PAGAMENTO = True

                    nomeExibicao = str(user[0]).split(" ")

                    if liberado:
                        # Inicia o status da cobranca
                        funcoes_camera.grava_processamento_cobranca(True, False)

                        # Cria um objeto tkinter para iniciar a saudacao
                        root = inicia_show_saudacao() 
                        saudacao = retorna_saudacao()

                        if not EXIBE_NOME_CATRACA:
                            nomeExibicao[0] = ""

                        # Mostra o saldo
                        if EXIBE_SALDO_CATRACA:
                            saudacao2 =cobranca.formaMensagemSaldoPosPassagem(idConta)
                        else:
                            saudacao2 = "Seja bem vindo"

                        # Checamos novamente se o semaforo ja esta ativo por outra transacao. Estando, nao seguimos com esta operacao
                        if funcoes_viagem.semaforo_ativo():
                            passou = False
                        else:
                            # Exibe a tela
                            show_saudacao(root, "green2", "white",saudacao, nomeExibicao[0], 200,36,"green2", saudacao2)
                            passou = database.liberar()

                        # Se a catraca foi girada, entao aqui aplicamos a cobranca
                        if passou:
                            with open(data['path'], 'rb') as img:
                                string = base64.b64encode(img.read())

                            funcoes_logs.insere_log("Cliente liberado: "+ str(user[0]) + " imagem: " + data['path'], local, 2)
                            fluxo_cobranca(FLAG_CATRACA_TIMEOUT,idConta,ULTIMO_IDWEB,string,True, metricas, range_analise )
                           
                            encerra_show_saudacao(root)
                            show_catraca_liberada("light blue","white", 200, 36)

                        # Fecha a tela de saudacao
                        encerra_show_saudacao(root)

                        FLAG_CATRACA_TIMEOUT = not passou
                        ULTIMO_IDWEB = user[1]

                        # Indica que a cobranca foi finalizada. Porem, aguarda alguns segundos antes de mudar o status
                        # Motivo: evitar delays com a camera, para que uma segunda cobranca nao seja feita indevidamente
                        # Para a pessoa na catraca
                        funcoes_camera.grava_processamento_cobranca(False)

                        # vincula o registro de conta na linha atual
                        funcoes_elastic.copia_matriz_facial_para_linha_passagem(idConta, idLinha)
                    else:
                        if EXIBE_NOME_SALDO_INSUFICIENTE:
                            compl_saldo_insuf = "\n\n" + nomeExibicao[0]
                        else:
                            compl_saldo_insuf = ""

                        funcoes_tela_corrente.registraTelaAtual("TELA_SALDO_INSUFICIENTE_CLIENTE")
                        funcoes_logs.insere_log("Usuario sem saldo, mostrando tela de bloqueio", local, 3)
                        cfgTelas("red2","white","Saldo Insuficiente" + compl_saldo_insuf,"",200,3000,32,"red2")

            elif rate == 2:
                count += 1
                if count == 99:
                    funcoes_tela_corrente.registraTelaAtual("TELA_ERRO_REC_FACIAL_CLIENTE")
                    funcoes_logs.insere_log("Erro de leitura facial, necessário QR CODE", local, 3)
                    cfgTelas("orange red", "white", "Nao conseguimos\nidentificar voce no\nnosso sistema\n\nPor favor, utilize\no QR Code gerado\npelo App", "", 200, 3500, 28, "orange red")
                    count  = 0

            elif rate == 3:
                count += 1
                if count == 2:
                    funcoes_tela_corrente.registraTelaAtual("TELA_NAO_EXISTE_BD_CLIENTE")
                    funcoes_logs.insere_log("Face não consta no banco de dados", local, 3)
                    cfgTelas("red2","white","Nao consta no banco de dados","",200,3000,32,"red2")
                    count = 0
        except Exception as e:
            # Caso tenha ocorrido um erro de comunicacao com a tela, entao devemos forcar a reboot apenas do CORE
            if 'connect to display' in str(e):
                funcoes_logs.insere_log("Reiniciando core, problema comunicacao com tela", local, 5)
                os.system("sudo pkill -9 -f core.py")
                return
        
        PROCESSANDO_IMAGEM = False
        PROCESSANDO_PAGAMENTO = False

    if (data['type'] == 'dinheiro' or data['type'] == 'gratuidade'):
        PROCESSANDO_PAGAMENTO = False
        PROCESSANDO_BOTAO = True
        
        funcoes_logs.insere_log("entrei no pagamento por dinheiro ou gratuidade******", local, 2)
        tipo = {
            'dinheiro': 5,
            'gratuidade': 8
        }
        t = tipo[data['type']]

        # Inicia o status da cobranca
        funcoes_camera.grava_processamento_cobranca(True)

        # Apresentamos a saudacao e aguardamos a catraca ser girada
        # se foi girada, geramos a cobranca. caso contrario, nao geramos a cobranca
        # Cria um objeto tkinter para iniciar a saudacao
        root = inicia_show_saudacao()
        saudacao = retorna_saudacao()

        # Exibe a tela
        show_saudacao(root, "green2", "white",saudacao, "", 200,36,"green2")

        passou = database.liberar()
        if passou:
            cobranca.cobrar({ 'id_web':0, 'tipoIdentificacao': t,'foto':'', 'idConta': 0})
            encerra_show_saudacao(root)
            show_catraca_liberada("light blue","white", 200, 36)

        encerra_show_saudacao(root)
        PROCESSANDO_BOTAO = False

        # Marca que a cobranca foi finalizada
        funcoes_camera.grava_processamento_cobranca(False)

    if (data['type'] == 'qrcode'):
        funcoes_logs.insere_log("Passando por QR Code", local, 2)
        PROCESSANDO_PAGAMENTO = False
        data['foto'] = ''
        PROCESSANDO_IMAGEM = True
        
        idConta = data['contaid']
        
        # Checa se esta apto a passar
        liberado = cobranca.getLiberadoSaldo(idConta)
        nome = cobranca.getConta(idConta)
        nome = str(nome[0])

        try:
            nome = str(nome).split(" ")
            nomeExibicao = nome[0]
        except:
            nomeExibicao = ""

        if liberado:
            qrcode = data['qrcode']
            data['porValor'] = True #saldo[2]
            data['contaId'] = idConta #saldo[3]
            data['tipoIdentificacao'] = 4

            if funcoes_viagem.semaforo_ativo():
                passou = False
            else:
                # Inicia o status da cobranca
                funcoes_camera.grava_processamento_cobranca(True)

                # Cria um objeto tkinter para iniciar a saudacao
                root = inicia_show_saudacao()
                saudacao = retorna_saudacao()

                if not EXIBE_NOME_CATRACA:
                    nomeExibicao = ""

                if EXIBE_SALDO_CATRACA:
                    # Mostra o saldo
                    saudacao2 =cobranca.formaMensagemSaldoPosPassagem(idConta)
                else:
                    saudacao2 = ""

                # Exibe a tela
                show_saudacao(root, "green2", "white",saudacao, nomeExibicao, 200,36,"green2", saudacao2)
                passou = database.liberar()

            # Se a catraca foi girada, ai sim aplicamos a regra de cobranca
            if passou:
                funcoes_logs.insere_log("Cliente liberado: "+ str(nome[0]), local, 2)
                
                # Marcamos o uso do qrcode, caso tenha passado pela catraca
                funcoes_qrcode.registra_qrcode_utilizado(qrcode)

                fluxo_cobrancaQRcode(FLAG_CATRACA_TIMEOUT,ULTIMO_IDWEB,data)

                encerra_show_saudacao(root)
                show_catraca_liberada("light blue","white", 200, 36)
            encerra_show_saudacao(root)
            
            FLAG_CATRACA_TIMEOUT = not passou
            ULTIMO_IDWEB = idConta
        
            # Encerra a cobranca
            funcoes_camera.grava_processamento_cobranca(False)
        else:
            if EXIBE_NOME_SALDO_INSUFICIENTE:
                compl_saldo_insuf = "\n\n"+ nomeExibicao
            else:
                compl_saldo_insuf = ""

            funcoes_logs.insere_log("Saldo insuficiente",local, 3)
            cfgTelas("red2","white","Saldo insuficiente" + compl_saldo_insuf,"",200,3000,32,"red2")

        PROCESSANDO_IMAGEM = False

    funcoes_core.zera_mensagem_process()

with open('/home/pi/caixa-magica-vars/config.json') as json_data:
    CONFIG = json.load(json_data)

try:
    timeout_rec_facial = CONFIG['timeout_rec_facial']
except:
    timeout_rec_facial = 30

funcoes_logs.insere_log("Core escutando na porta " + str(CONFIG['core']['port']), local,2)

# Ligamos aqui o core
funcoes_core.atualiza_status_core("ON")

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CONFIG['core']['host'], CONFIG['core']['port']))
            s.listen()
            conn, addr = s.accept()
            with conn:
                while True:
                    try:
                        pkg = conn.recv(CONFIG['core']['bufsize'])
                        if pkg:
                            '''
                                json:
                                {
                                    type: 'facial',
                                    path: '/path/to/image.jpg'
                                }
                            '''
                            data = json.loads(pkg.decode('utf-8'))
                        
                            if data['type'] != 'healthcheck':
                                # Criamos um processo que aguarda X segundos. Se o reconhecimento facial nao ocorrer nesse prazo, entao expiramos o processo
                                p = multiprocessing.Process(target=process, args=(data,))
                                p.start()
                                p.join(timeout_rec_facial)

                                if p.is_alive():
                                    try:
                                        p.terminate()
                                    except:
                                        pass
                                    PROCESSANDO_IMAGEM = False
                                    PROCESSANDO_PAGAMENTO = False
                                    PROCESSANDO_BOTAO = False

                                    funcoes_core.atualiza_mensagem_process("")
        
                                    funcoes_tela_corrente.registraTelaAtual("TELA_ERRO_REC_FACIAL_CLIENTE")
                                    funcoes_logs.insere_log("Erro de leitura facial, necessário QR CODE", local, 3)
                                    cfgTelas("orange red", "white", "Nao conseguimos\nidentificar voce no\nnosso sistema\n\nPor favor, utilize\no QR Code gerado\npelo App", "", 200, 3500, 28, "orange red")

                        else:
                            break 
                        conn.sendall(pkg)
                    except Exception as e:
                        funcoes_logs.insere_log("Erro core rcv - " + str(e), local,4)
    except Exception as e:
        funcoes_logs.insere_log("Erro no core - " + str(e), local, 4)
