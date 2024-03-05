from datetime import datetime
from scipy import spatial
import statistics
import os

TOLERANCIA_SEGUNDOS_ARQ = 1

arq_matrizes = '/home/pi/caixa-magica-operacao/matrizes_comp.txt'

# Zera o arquivo de matrizes a comparar
def cria_arquivo_matrizes():
    try:
        with open(arq_matrizes, "w") as f:
            f.write("")
        f.close()
    except:
        pass

# elimina o arquivo, caso o arquivo nao tenha sido atualizado dentro da tolerancia
def elimina_arquivo_matrizes():
    if diff_segundos_agora_ultima_mod() > TOLERANCIA_SEGUNDOS_ARQ:
        try:
            with open(arq_matrizes,"w") as f:
                f.write("")
            f.close()
        except:
            pass
    else:
        return

# Retorna data de modificacao do arquivo
def ultima_mod_arquivo_matrizes():
    aux = os.path.getmtime(arq_matrizes)
    return aux

# Retorna diferenca de segundos em relacao a criacao do arq x data atual
def diff_segundos_agora_ultima_mod():
    val1 = datetime.now().timestamp()
    val2 = ultima_mod_arquivo_matrizes()
    return val1 - val2

# Adiciona uma matriz no arquivo
def adiciona_matriz(matriz):
    try:
        string_gravar = str(datetime.utcnow())
        string_gravar = string_gravar + "|" + (",".join(map(str,matriz))) + "\n"

        with open(arq_matrizes, "a") as f:
            f.write(string_gravar)
        f.close()
    except:
        pass

# Mantem no arquivo apenas as ultimas linhas determinadas
def persiste_arquivo(ultimos_regs):
    try:
        ultimos_regs_aux = ultimos_regs * -1

        a_file = open(arq_matrizes, "r")
        lines = a_file.readlines()
        last_lines = lines[ultimos_regs_aux:]
        a_file.close()

        a_file = open(arq_matrizes, "w")
        a_file.write("")
        a_file.close()

        a_file = open(arq_matrizes, "a")
        for linha in last_lines:
            a_file.write(linha)
        a_file.close()
    except Exception as e:
        pass

# Calcula a distancia entre as ultimas X matrizes
def calcula_dist_matrizes(matriz_parametro, ultimos_regs, dist_minima, dist_maxima):
    media= 0
    try:
        if len(matriz_parametro) <= 0:
            return media

        ultimos_regs_aux = ultimos_regs * -1

        a_file = open(arq_matrizes, "r")
        lines = a_file.readlines()
        last_lines = lines[ultimos_regs_aux:]
    
        arr_calculos = []

        matriz_comparar = matriz_parametro
        for linha in last_lines:
            arr_linha = linha.split("|")
            matriz_aux_string = arr_linha[1].replace("\n", "")
            matriz_datetime = arr_linha[0]

            # Transforma o conteudo texto da matriz em uma matriz Python
            list_aux = matriz_aux_string.split(",")
            matriz_conv = list(map(float, list_aux))
            #print(matriz_conv)
            #print(matriz_parametro)

            # Efetua o calculo da distancia cosine entre a matriz base x a que consta no arquivo
            result = spatial.distance.euclidean(matriz_conv, matriz_comparar)
            print("result: " + str(result))
            arr_aux = []
            arr_aux.append(matriz_comparar)
            arr_aux.append(matriz_conv)
            arr_aux.append(result)
            arr_calculos.append(arr_aux)

            matriz_comparar = matriz_conv

        # Calculamos a media entre os registros
        arr_cosine = []
        for row in arr_calculos:
            if row[2] >= dist_minima and row[2] <= dist_maxima:
                arr_cosine.append(row[2])
            else:
                media = 0
                arr_cosine = []
                cria_arquivo_matrizes()
                return media

        print(arr_cosine)
        if len(arr_cosine) >= ultimos_regs:
            media = statistics.mean(arr_cosine)
        else:
            media = 0
        
        print("Media: " + str(media))
        # Adiciona a matriz na base de calculos
        adiciona_matriz(matriz_parametro)

        # mantemos no arquivo apenas os ultimos X registros
        persiste_arquivo(ultimos_regs)
    except Exception as e:
        media = 0

    if media == None:
        media = 0

    #if media <= 0:
    #    cria_arquivo_matrizes()
    
    return media

matriz = [-0.14287069439888,0.08772103488445282,0.12679512798786163,-0.014134850353002548,-0.07363145798444748,-0.005051434971392155,-0.004104746505618095,-0.08439341932535172,0.06703031063079834,-0.06066805124282837,0.24626056849956512,0.046026986092329025,-0.24326461553573608,-0.011687062680721283,-0.13079868257045746,0.13160543143749237,-0.12681607902050018,-0.07876452803611755,-0.18819481134414673,-0.05915898084640503,0.04922929033637047,0.11067052185535431,0.018416618928313255,-0.03743704780936241,-0.1702926605939865,-0.3140350580215454,-0.09638194739818573,-0.056364960968494415,0.10636091232299805,-0.08007077872753143,0.047714896500110626,-0.011393141001462936,-0.13723665475845337,-0.024628659710288048,0.03920070827007294,0.04090920835733414,-0.1153540387749672,-0.0322125218808651,0.25268492102622986,0.11083770543336868,-0.18422390520572662,0.18146809935569763,0.03635783493518829,0.3228020668029785,0.2298804372549057,0.05312880873680115,0.03417515009641647,-0.06597331166267395,0.05744628608226776,-0.30538210272789,0.06938041746616364,0.10851950198411942,0.19623315334320068,0.07763922214508057,0.16098441183567047,-0.17340967059135437,-0.04178645461797714,0.14730393886566162,-0.20660342276096344,0.13710255920886993,-0.006066972389817238,-0.1275673359632492,-0.0003367941826581955,-0.04674310237169266,0.10415586084127426,0.09127107262611389,-0.14641378819942474,-0.08901702612638474,0.2651881277561188,-0.16292375326156616,-0.007869824767112732,0.0773974135518074,-0.02923930063843727,-0.1357591450214386,-0.2545897662639618,0.07467294484376907,0.39480915665626526,0.1766049563884735,-0.23294098675251007,-0.047457583248615265,-0.021359143778681755,-0.006230294704437256,0.00945588480681181,0.056311238557100296,-0.11281313002109528,-0.10963431000709534,-0.04506923258304596,-0.035760704427957535,0.13308018445968628,0.028342438861727715,-0.044802356511354446,0.26135149598121643,0.05799912288784981,-0.005857011303305626,0.07367407530546188,0.014267119579017162,-0.1873292177915573,-0.08431936055421829,-0.08474133908748627,-0.02195260301232338,-0.03134344518184662,-0.13667918741703033,0.051998429000377655,0.10974152386188507,-0.0944669246673584,0.22607263922691345,-0.06184473633766174,-0.04463723674416542,-0.003753179684281349,0.0694684386253357,-0.07611961662769318,0.030874574556946754,0.16346004605293274,-0.2585209310054779,0.2705330550670624,0.21484079957008362,-0.04359635338187218,0.09992756694555283,0.14095649123191833,0.027496710419654846,-0.009388544596731663,0.08158357441425323,-0.13745655119419098,-0.16227750480175018,-0.0176619291305542,-0.1414598673582077,0.06969687342643738,0.034902505576610565]

#print(datetime.utcnow())
#calcula_dist_matrizes(matriz, 2)
#print(datetime.utcnow())

#print(diff_segundos_agora_ultima_mod())
#elimina_arquivo_matrizes()
