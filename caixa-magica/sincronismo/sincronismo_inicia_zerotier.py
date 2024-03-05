import json
from time import sleep
import os

path_config = "/home/pi/caixa-magica-vars/config_zerotier.json"
path_instalacao = "/home/pi/caixa-magica-operacao/instalacao.json"
path_zerotier = "/home/pi/caixa-magica/zerotier/"
file_zerotier = path_zerotier + "/redes_empresas.txt"
path_git = "https://github.com/githubcm1/zerotier_redes.git"
path_arq_operacao = "/home/pi/caixa-magica-operacao/rede_zerotier.txt"
comando_assoc_rede = "sudo zerotier-cli join "

comando_git = "sudo git clone " + path_git + " " + path_zerotier

NOVA_TENTATIVA = 600

while True:
    os.system("sudo rm -rf " + path_zerotier)
    rede_usar = ""

    try:
        with open(path_config) as fil:
            aux = json.load(fil)
            download_client = aux['download_client']
    except:
        download_client = ""

    # Se ha o link definido para o zerotier, tentamos baixar o cliente novamente
    if download_client != "":
        os.system(download_client)
        
        # Checamos se existe o arquivo de rede ja configurado
        # Se tiver, nao sera preciso efetuar novo request para conexao na rede
        if not os.path.exists(path_arq_operacao):
            # Em posse do arquivo de redes, checamos qual rede deve se aplicar nesta maquina
            try:
                with open(path_instalacao) as inst:
                    aux = json.load(inst)
                    operadoraid = aux['operadora']
            except:
                operadoraid = ""

            # Se existir empresa associada, ai sim efetuamos a checagem
            if operadoraid != "":
                # Se nao existe a conf local, tentamos baixar do github a lista de redes
                os.system(comando_git)

                lines= []
                # Abrimos o arquivo de comandos
                try:
                    with open(file_zerotier) as fil:
                        lines = fil.readlines()
                        lines = [line.strip() for line in lines]

                        for line in lines:
                            line_split = line.split("|")
                            operadora_arquivo = line_split[0]

                            if str(operadora_arquivo) == str(operadoraid):
                                rede_usar = line_split[1]
                                break
                except:
                    pass
                
                # Se encontrou a rede
                if rede_usar != "":
                    # Enviamos o comando de associacao ao servidor
                    comando_assoc_rede_executar = comando_assoc_rede + " " + str(rede_usar)
                    os.system(comando_assoc_rede_executar)

                    # Gravamos no arquivo local a rede associada
                    os.system("sudo echo '" + str(rede_usar) + "' | sudo tee " + path_arq_operacao)

            os.system("sudo rm -rf " + path_zerotier)

    sleep(NOVA_TENTATIVA)
