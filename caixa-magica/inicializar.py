import sys
import json
import time
import base64
sys.path.insert(1, '/home/pi/caixa-magica/')

from sincronismo import req as sincronismo

def inicializar():
   global dados
   global nome_responsavel
   global veiculo
   global id_linha
   global nome_linha
   global dia_semana
   global horario
   global motivo_viagem
   global tipo_viagem
   dias_semana = ['DOMINGO', 'SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO']
   tipos_viagem = ['Normal', 'Emergencial']
   #aguarde.show()   
   try:
      r = sincronismo.inicializacao()
      dados = r.json()

      nome_responsavel = dados['viagem']['motorista']['usuario']['nome']
      veiculo = dados['veiculo']
      # id_linha = dados['viagem']]']['id']
      id_linha = ''
      nome_linha = dados['linha']['nome']
      dia_semana = dias_semana[dados['horarioViagem']['diaSemana']]
      horario = dados['horarioViagem']['horario']
      #motivo_viagem = dados['viagem']['motivo']
      motivo_viagem = 1
      tipo_viagem = tipos_viagem[dados['viagem']['tipo'] - 1]

   except Exception as e:
      print(e)
      dados = None


def inicializar_completo():
   global dados
   dados = None
   while dados == None:
      print("Tentando inicializar")
      inicializar()
      #aguarde.hide()
      try:
         f = open('/home/pi/caixa-magica-operacao/inicializacao.json', 'w+')
         f.write(json.dumps(dados))
         f.close()
      except Exception as e:
         print(e)
         dados = None
      time.sleep(15)

inicializar_completo()
