import sys
sys.path.insert(1,'/home/pi/caixa-magica/core/')
import funcoes_elastic

print("Removendo indices faciais")
funcoes_elastic.remove_indices_faciais()
print("Reovidos indices faciais")
