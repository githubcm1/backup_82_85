import json
import os

path_json = '/home/pi/caixa-magica-operacao/mensagem_process_core.json'
path_json_core = '/home/pi/caixa-magica-operacao/status_core.json'
path_status_placa = "/home/pi/caixa-magica-operacao/status_serial.json"


# Zera status da placa
def zera_status_placa():
    comando = "sudo echo '{\"status\": \"OFF\"}' | sudo tee " + path_status_placa
    os.system(comando)

# obtem conteudo da mensagem
def obtem_status_placa():
    try:
        with open(path_status_placa) as json_data:
            vars1 = json.load(json_data)
            mensagem = vars1['status']
    except Exception as e:
        mensagem = 'ON'
        pass

    return mensagem

# Muda status da placa
def atualiza_status_placa(status):
    try:
        with open(path_status_placa) as json_data:
            vars1 = json.load(json_data)
            vars1['status'] = status

            with open(path_status_placa, "w") as saida:
                json.dump(vars1, saida)
    except Exception as e:
        #print(str(e))
        pass



# Zera status do core
def zera_status_core():
    comando = "sudo echo '{\"status\": \"OFF\"}' | sudo tee " + path_json_core
    os.system(comando)

# obtem conteudo da mensagem
def obtem_status_core():
    try:
        with open(path_json_core) as json_data:
            vars1 = json.load(json_data)
            mensagem = vars1['status']
    except Exception as e:
        mensagem = 'OFF'
        pass

    return mensagem

# Muda status do core
def atualiza_status_core(status):
    try:
        with open(path_json_core) as json_data:
            vars1 = json.load(json_data)
            vars1['status'] = status

            with open(path_json_core, "w") as saida:
                json.dump(vars1, saida)
    except Exception as e:
        #print(str(e))
        pass

# Zera arquivo de mensagem
def zera_mensagem_process():
    comando = "sudo echo '{\"mensagem\": \"\"}' | sudo tee " + path_json
    os.system(comando)

# obtem conteudo da mensagem
def obtem_mensagem_process():
    try:
        with open(path_json) as json_data:
            vars1 = json.load(json_data)
            mensagem = vars1['mensagem']
    except Exception as e:
        mensagem = ''
        pass

    return mensagem

# determina conteudo da mensagem
def atualiza_mensagem_process(mensagem):
    try:
        with open(path_json) as json_data:
            vars1 = json.load(json_data)
            vars1['mensagem'] = mensagem

            with open(path_json, "w") as saida:
                json.dump(vars1, saida)
    except Exception as e:
        pass

