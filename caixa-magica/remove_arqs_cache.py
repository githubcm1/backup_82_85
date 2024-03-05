import os
from glob import glob
import pathlib

path_base = '/home/pi/caixa-magica/'

extensoes_eliminar = ['.swo', '.swp', '.swk','.sux', '.sre', '.svr', 
                      '.sto', '.stv','.sqe', '.suq', '.ssk', '.sqq', 
                      '.ssr', '.ssc', '.sry','.swh', '.srn', '.suh', 
                      '.sra', '.stx', '.svo', '.sri', '.sqd', '.sro',
                      '.sqk', '.spu', '.stc','.stq', '.sue', '.svi', 
                      '.swb', '.ssy', '.suk', '.svu', '.srk', '.sqy', 
                      '.swn', '.swa', '.sqz', '.spz', '.stf', '.svv', 
                      '.svc', '.sqp', '.stt', '.suj', '.srw', '.suz', 
                      '.ssw', '.srl', '.sqw', '.swj', '.srx', '.svk', 
                      '.sus', '.sta', '.stb', '.stz', '.swg', '.sub', 
                      '.sun', '.sti', '.sqj', '.ssf', '.ssg', '.suc', 
                      '.sqx', '.svp', '.ssm', '.ssn', '.sth', '.sup', 
                      '.sss', '.ssx', '.svz', '.squ', '.spt', '.stg', 
                      '.sva', '.stl', '.sts', '.suu', '.suw', '.ssp', 
                      '.sum', '.sqm', '.srj', '.sru', '.svw', '.svd', 
                      '.stm', '.srt', '.stw', '.svl', '.srq', '.ssd', 
                      '.svt', '.svn', '.suf', '.suv', '.sve', '.svg', 
                      '.sqi', '.sqa', '.svj', '.svq', '.spv', '.sug', 
                      '.ssa', '.swl', '.ssz', '.suo', '.srd', '.svx', 
                      '.ssj', '.swm', '.sqt', '.spx', '.srh', '.sui', 
                      '.ssv', '.srr', '.srm', '.srf', '.srz', '.stj', 
                      '.stp', '.swf', '.sst', '.srb', '.sqb', '.sqc', 
                      '.swd', '.svm', '.sud', '.sty', '.stk', '.svh', 
                      '.sqv', '.swi', '.stn', '.sqh', '.srs', '.srg', 
                      '.swc', '.swe', '.ssu', '.sqg', '.sqn', '.sua', 
                      '.suy', '.sur', '.svs', '.str', '.spy', '.ste', 
                      '.sse', '.ssq', '.std', '.svb', '.sul', '.svf', 
                      '.ssb', '.sqo', '.spw', '.svy', '.srp', '.ssi', 
                      '.sqf', '.sqs', '.sqr', '.sut', '.stu', '.src',
                      '.bkp','.ssl','.sso', '.srv']
extensoes_identificadas = []

comando_del_prefix = "sudo rm -f "
arquivos = []
arquivos_del = []
diretorios = glob(path_base + "*/", recursive=True)
diretorios.append(path_base)

# para cada diretorios
for dire in diretorios:
    # pega os arquivos
    arquivos_aux = os.listdir(dire)

    # Para cada arquivo do diretorio, incluimos na lista de arquivos geral
    for arquivo in arquivos_aux:
        if not os.path.isdir(arquivo):
            arquivo = dire + arquivo
            arquivos.append(arquivo)

# Com a lista de arquivos, checamos quais deles possuem extensoes invalidas
for arquivo in arquivos:
    extensao = pathlib.Path(arquivo).suffix

    if not extensao in extensoes_identificadas:
        extensoes_identificadas.append(extensao)

    if extensao in extensoes_eliminar:
        arquivos_del.append(arquivo)
    

arquivos = []
print(extensoes_identificadas)

# Por fim, para cada arquivo marcado para exclusao, elimina-lo via linha de comando
for arquivo in arquivos_del:
    comando = comando_del_prefix + arquivo
    os.system(comando)
