import sys
import json
import os
sys.path.insert(1,'/home/pi/caixa-magica/core')
import endpoints
import subprocess

folder = "/home/pi/releases/"
json_token = '/home/pi/caixa-magica-updates/token_update.json'

paths_deploy = ['/home/pi/upload-github/', '/home/pi/upload-github-infra-compiled']

def checa_permite_update(param):
    ret = []

    ATUALIZA=False

    # Checamos se a maquina em questao eh uma maquina de dev
    # Nunca uma maquina de dev deve ser considerada para estes updates
    for path in paths_deploy:
        if os.path.isdir(path):
            ret.append(False)
            ret.append("Esta é uma maquina de DESENVOLVIMENTO.\n\nProibida ação de atualização.")
            ret.append("")
            return ret

    try:
        with open(json_token) as json_data:
            aux = json.load(json_data)
            token = aux['token']
    except:
        ret.append(False)
        ret.append("Checar se o arquivo '" + json_token + "' consta nesta maquina." )
        ret.append("")
        return ret


    # Primeiro, limpamos o diretorio de releases
    try:
        os.system("sudo rm -rf " + folder)
        os.system("sudo mkdir -p " + folder)

        # Pegamos o ambiente atual
        ambiente = endpoints.getEnv()

        if ambiente == "PROD":
            ambiente = "prod"
        if ambiente == "HOMOLOG":
            ambiente="hom"
        if ambiente == "DEV":
            ambiente="dev"

        # Atraves da instalacao, identificamos o id da operadora
        with open("/home/pi/caixa-magica-operacao/instalacao.json") as jsondata:
            aux = json.load(jsondata)
            operadoraid=aux['operadora']

        comando = "sudo git clone  https://" + token + "@github.com/githubcm1/release_validador_" + ambiente + "_"+ str(operadoraid) +".git " + folder
        #output = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=False)
        os.system(comando)

        # Checamos o diretorio inde os arquivos foram baixados
        conteudo_folder = os.listdir(folder)

        if len(conteudo_folder) <= 0:
            ret.append(False)
            ret.append("Sem conteudo de atualizacao.\n\nPossiveis causas:\n- Checar o token de acesso com o administrador\n-Checar sua conexao de internet\n-Checar repositorio de atualizacao no servidor.\n\n")
            ret.append("")
            return ret

        # Pegamos a versao atual da aplicacao
        with open("/home/pi/caixa-magica/version.txt") as fil:
            conteudo = fil.readlines()
            versao = conteudo[0].strip()

        # Para cada item do folder
        for arquivo_folder in conteudo_folder:
            if param in arquivo_folder:
                pos_ = arquivo_folder.rfind("_")
                arquivo_exec = arquivo_folder
                arquivo_folder = arquivo_folder[0:pos_].strip()

                # Se a versao atual  desta maquina estiver no mesmo release do servidor, nao devemos atualizar. caso contrario, atualiza
                ATUALIZA = True
                if versao == arquivo_folder:
                    ATUALIZA = False
                    ret.append(False)
                    ret.append("Ja esta na ultima versao (" + versao + ")")
                    ret.append("")
                    return ret

        if ATUALIZA:
            ret.append(True)
            ret.append("Atualizacao permitida")
            comando = 'sudo ' +folder + arquivo_exec
            ret.append(comando)
        else:
            ret.append(False)
            ret.append("Sem conteudo no repositorio.")
            ret.append("")
        return ret
    except Exception as e:
        ret.append(False)
        ret.append("Checar conexao de internet. Erro: " + str(e))
        ret.append("")
        return ret

def executa_atualiza(comando):
    print("Executando comando: " + comando)
    try:
        os.system(comando)
    except:
        pass
    return
