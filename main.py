from fullProcessModule import Module
import numpy as np
import json
import time
import os

debugLog=False

# Parametros do sistema
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=1000 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período
noiseExtremes=[1e-8,1e-7] # Valores máximo e minimo de amplitude de ruído
numNoises=3 # Quantos valores diferentes de ruído serão simulados
noises=np.linspace(noiseExtremes[0],noiseExtremes[1],numNoises) # Vetor de valores de ruído
DCExtremes=[0.2,0.8] # Valores máximo e minimo de duty-cycle
numDC=3 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle
numRepetitions=1 # Quantas vezes serão repetidos os mesmos parâmetros com dados diferentes
numPackets=1

# Load os dados do simulador
with open("Simulator\luxResults.json") as fs: simData=json.load(fs)

# Total simulation time info
xLen=len(list(simData.keys())) # Quantos valores diferentes em x serão simulados
yLen=len(list(simData[list(simData.keys())[0]].keys())) # Quantos valores diferentes em y serão simulados
print("Valores de X distintos:",xLen)
print("Valores de Y distintos:",yLen)
totalNum=xLen*yLen*numNoises*numRepetitions*numDC*numPackets # Número total de simulações
print("Número total de simulações:",totalNum)

# Transforma segundos para o formato: x horas y minutos z segundos (ChatGPT)
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

# Percebi que se deixar o script rodando por muito tempo alguma coisa para de funcionar, então criei
#   esse contador que exclui todos os arquivos de dados do LTSpice depois de um certo número de iterações.
#   Isso concerta o problema
countToDeletion=0

dt=1 # Quanto tempo passou entre o começo e o final da última simulação
cont=0 # Contador de simulações para prever quanto tempo vai demorar para a acabar

circuit="circuitR.asc"
resultDir="resultados.json"

circuitName=circuit.split(".")[0]
sufixes=[".raw",".op.raw",".net",".log",".fail"]
deletionPaths=[]
for sufix in sufixes:
    deletionPaths.append(circuitName+sufix)
    deletionPaths.append(circuitName+"_1"+sufix)
maxSimsBeforeDeletion=3

'''for path in deletionPaths:
    if os.path.exists(path):
        os.remove(path)
input("Removeu as coisas")'''

nodes=[
    "V(comp_pga)",
    "V(comp_real)",
    "V(filtered)",
    "V(tia)"
]

'''nodes=[
    "V(v_comp)",
    "V(v_comp_pga)",
    "V(v_comp_sat)"
]
'''

'''obj=Module(VPPMfreq,5,numPointsPerPeriod,numSamples,0.2,1,1,1,[(0.3*(10**-6)),0])
obj.Run(circuit,nodes,False)
input("Teste")'''

for X_Distance in simData.keys():
    for Y_Distance in simData[list(simData.keys())[0]].keys():
        lux=simData[X_Distance][Y_Distance]
        if debugLog: print("X:",X_Distance,"Y:",Y_Distance," -> ",lux)
        for noiseAmp in noises:
            for dc in DCs:
                for n in range(numRepetitions):
                    t0=time.time()
                    obj=Module(VPPMfreq,numBits,numPointsPerPeriod,numSamples,dc,X_Distance,Y_Distance,lux,[-1,noiseAmp],numPackets)
                    # Antes de ser feita a simulação, o dict de resultados é conferido para ver quantas simulações
                    #   com esses parâmetros já foram feitas
                    with open(resultDir) as fs: previousData=json.load(fs)
                    key=obj.GetDictKey()
                    try: num=len(previousData[key])
                    except: num=0
                    if debugLog:
                        print("Foram feitas",num,"simulações com os parametros da key:",key)

                    # Se não foram feitas simulações o suficiente, é feita mais uma simulação
                    if num<numRepetitions:
                        # Full process run
                        simStr,errors=obj.Run(circuit,nodes,True)
                        # Save results
                        with open(resultDir) as fs: oldResults=json.load(fs)
                        try: oldResults[simStr].append(errors)
                        except: oldResults[simStr]=[errors]
                        with open(resultDir,'w') as fs: json.dump(oldResults,fs)
                        if debugLog: print("Resultados salvos")
                    else:
                        if debugLog: print("Skiped")

                    # Print de progresso total
                    if not debugLog:
                        percent=round((100*cont)/totalNum,4)
                        timeToFinish=dt*(totalNum-cont)
                        print(percent,"% / Time to finish:",format_time(timeToFinish),"key saved:",obj.GetDictKey())
                        cont+=1

                    # Deleta os arquivos de info do LTSpice caso o contador chegue no limite
                    countToDeletion+=1
                    if countToDeletion>maxSimsBeforeDeletion:
                        countToDeletion=0
                        for path in deletionPaths:
                            if os.path.exists(path):
                                os.remove(path)
                    dt=time.time()-t0

'''for X_Distance in simData.keys():
    for Y_Distance in simData[list(simData.keys())[0]].keys():
        lux=simData[X_Distance][Y_Distance]
        if debugLog: print("X:",X_Distance,"Y:",Y_Distance," -> ",lux)
        for noiseAmp in noises:
            for dc in DCs:
                for n in range(numRepetitions):
                    t0=time.time()
                    obj=Module(VPPMfreq,numBits,numPointsPerPeriod,numSamples,dc,X_Distance,Y_Distance,lux,0,[-1,noiseAmp],numPackets)
                    
                    # Antes de ser feita a simulação, o dict de resultados é conferido para ver quantas simulações
                    #   com esses parâmetros já foram feitas
                    with open("results.json") as fs: previousData=json.load(fs)
                    key=obj.GetDictKey()
                    try: num=len(previousData[key])
                    except: num=0
                    if debugLog:
                        print("Foram feitas",num,"simulações com os parametros da key:",key)

                    # Se não foram feitas simulações o suficiente, é feita mais uma simulação
                    if num<numRepetitions: obj.Run(circuit,nodes,True)
                    else:
                        if debugLog: print("Skiped")

                    # Print de progresso total
                    if not debugLog:
                        percent=round((100*cont)/totalNum,4)
                        timeToFinish=dt*(totalNum-cont)
                        print(percent,"% / Time to finish:",format_time(timeToFinish),"key saved:",obj.GetDictKey())
                        cont+=1

                    # Deleta os arquivos de info do LTSpice caso o contador chegue no limite
                    countToDeletion+=1
                    if countToDeletion>maxSimsBeforeDeletion:
                        countToDeletion=0
                        for path in ['circuitRR_1.log','circuitRR_1.net','circuitRR_1.op.raw','circuitRR_1.raw','circuitRR.net','circuitRR.raw']:
                            if os.path.exists(path):
                                os.remove(path)
                    dt=time.time()-t0
                '''
                    

