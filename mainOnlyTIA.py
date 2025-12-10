from fullProcessModule import Module
import numpy as np
import json
import time
from LTSpiceCleaner import Clean

debugLog=False

# Parametros do sistema
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=1000 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período
noiseExtremes=[0,1e-8] # Valores máximo e minimo de amplitude de ruído
numNoises=2 # Quantos valores diferentes de ruído serão simulados
noises=np.linspace(noiseExtremes[0],noiseExtremes[1],numNoises) # Vetor de valores de ruído
DCExtremes=[0.2,0.8] # Valores máximo e minimo de duty-cycle
numDC=3 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle
numRepetitions=1 # Quantas vezes serão repetidos os mesmos parâmetros com dados diferentes
numPackets=1

# Load os dados do simulador
with open("Simulator/luxResults.json") as fs: simData=json.load(fs)

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

circuit="circuit_Simple.asc"
resultDir="LTSpiceSimResults/result_TIA.json"

circuitName=circuit.split(".")[0]
sufixes=[".raw",".op.raw",".net",".log",".fail"]
deletionPaths=[]
for sufix in sufixes:
    deletionPaths.append(circuitName+sufix)
    deletionPaths.append(circuitName+"_1"+sufix)
maxSimsBeforeDeletion=3

nodes=[
    "V(compideal)"
]

trigger=2

'''obj=Module(VPPMfreq,1000,numPointsPerPeriod,numSamples,0.2,1,1,17.29,[-1,0])
ts=obj.inputTime
sunLux=[1600*(75*(10**-9)) for _ in range(len(ts))]
simStr,errors=obj.Run(circuit,nodes,2)
print("Erros:",errors)
input()'''

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
                    
                    # Print de progresso total
                    if not debugLog:
                        percent=round((100*cont)/totalNum,4)
                        timeToFinish=dt*(totalNum-cont)
                        print(percent,"% / Time to finish:",format_time(timeToFinish),"key runnig:",obj.GetDictKey())
                        cont+=1

                    # Se não foram feitas simulações o suficiente, é feita mais uma simulação
                    if num<numRepetitions:
                        # Full process run
                        simStr,errors=obj.Run(circuit,nodes,trigger)
                        # Save results
                        with open(resultDir) as fs: oldResults=json.load(fs)
                        try: oldResults[simStr].append(errors)
                        except: oldResults[simStr]=[errors]
                        with open(resultDir,'w') as fs: json.dump(oldResults,fs)
                        if debugLog: print("Resultados salvos")
                        print("Erros:",[errors])
                        countToDeletion+=1
                    else:
                        if debugLog: print("Skiped")

                    if not debugLog:
                        print("Saved")

                    # Deleta os arquivos de info do LTSpice caso o contador chegue no limite
                    if countToDeletion>maxSimsBeforeDeletion:
                        countToDeletion=0
                        Clean()
                    dt=time.time()-t0