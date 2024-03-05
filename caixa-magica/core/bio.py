import logging
import sys
sys.path.insert(1, '/home/pi/caixa-magica/pd/')
from CommandsBiometric import CommandsBiometric
import Constants

global resultado_load_lib

def load_library():
    global resultado_load_lib
    biometrics = CommandsBiometric()
    resultado_load = biometrics.init_cis()
    return resultado_load

def ler_biometria():
    global resultado_load_lib
    amostra = bytes(b'\x00')*Constants.TAM_TMP_FINGERPRINT
    if resultado_load_lib==Constants.COMANDO_EXECUTADO_COM_SUCESSO:
        biometrics = CommandsBiometric()
        amostra = biometrics.enroll_fingerprint_cis()
        if len(amostra) > 1: 
            biometria = biometrics.check_template_fingerprint(amostra)
            if len(biometria)>1:
                logging.warning("Digital encontrada com sucesso")
                if biometria == Constants.RESPONSAVEL:
                    return "responsavel"
                else:           
                    return biometria                        
            else:
                return False
        return False
    return False



resultado_load_lib = load_library()
