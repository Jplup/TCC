from threading import Thread
import numpy as np
import json
import os
from LTSpiceCleaner import Clean

Clean()

# General simulation parameter
paralelJsonPathPrefix="LTSpiceSimResults/ParalelResults/filterXtia"
mainCircuitName="circuit_filter"
maxSimsBeforeDeletion=1
nodes=[
    "V(comp_filter)",
    "V(comp_tia)"
]
trigger=2

# Paralel stuff
numOfThreads=2
paralelInfoToBeRefencedInEachScript={}
for n in range(numOfThreads):
    savePath=paralelJsonPathPrefix+str(n+1)+".json"
    if not os.path.exists(savePath):
        with open(savePath,'w') as fs: json.dump({},fs)
    circuitPath=mainCircuitName+str(n+1)+".asc"
    if not os.path.exists(circuitPath):
        print(circuitPath,"não encontrado, cria ele")
        input()
    paralelData={"simData":{},"itemData":[]}
    paralelData["simData"]["maxSimsBeforeDeletion"]=maxSimsBeforeDeletion
    paralelData["simData"]["nodes"]=nodes
    paralelData["simData"]["trigger"]=trigger
    paralelData["simData"]["circuit"]=circuitPath
    paralelData["simData"]["resultDir"]=savePath
    paralelData["simData"]["inputDir"]="fullCircuitInput"+str(n+1)+".txt"
    paralelInfoToBeRefencedInEachScript[str(n+1)]=paralelData

print("Lembrou de mudar o .txt de entrada de cada .asc?")
input()
    
# Parametros do sistema
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=1000 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período
noises=[1e-8,1e-7,5e-7]
DCExtremes=[0.2,0.8] # Valores máximo e minimo de duty-cycle
numDC=3 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle


# Load os dados do simulador
with open("Simulator/luxResults.json") as fs: simData=json.load(fs)
with open("Simulator/luxResultsVPPM2.json") as fs: vppm2=json.load(fs)
with open("Simulator/luxResultsILU_CSE.json") as fs: ilu1=json.load(fs)
with open("Simulator/luxResultsILU_CSD.json") as fs: ilu2=json.load(fs)

# Total simulation time info
xLen=len(list(simData.keys())) # Quantos valores diferentes em x serão simulados
yLen=len(list(simData[list(simData.keys())[0]].keys())) # Quantos valores diferentes em y serão simulados
totalNum=xLen*yLen*len(noises)*len(DCs) # Número total de simulações
print("Número total de simulações:",totalNum)

# Transforma segundos para o formato: x horas y minutos z segundos (ChatGPT)
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

def GenerateOtherWaves(X,Y):
    luxAmp=75*(10**(-9))
    addIlus=[]
    addIlus.append(ilu1[X][Y]*luxAmp)
    addIlus.append(ilu2[X][Y]*luxAmp)
    addIlus.append(vppm2[X][Y]*luxAmp)
    return addIlus
    

paralelCount=0
for noiseAmp in noises:
    for X_Distance in simData.keys():
        for Y_Distance in simData[list(simData.keys())[0]].keys():
            lux=simData[X_Distance][Y_Distance]
            for dc in DCs:
                params={}
                params["VPPMfreq"]=VPPMfreq
                params["numBits"]=numBits
                params["numPointsPerPeriod"]=numPointsPerPeriod
                params["numSamples"]=numSamples
                params["dc"]=dc
                params["X_Distance"]=X_Distance
                params["Y_Distance"]=Y_Distance
                params["lux"]=lux
                params["noiseAmp"]=noiseAmp
                params["addNoisesAmps"]=GenerateOtherWaves(X_Distance,Y_Distance)
                paralelInfoToBeRefencedInEachScript[str(paralelCount+1)]["itemData"].append(params)
                paralelCount+=1
                if paralelCount>=numOfThreads: paralelCount=0

for n in range(numOfThreads):
    with open("paralel"+str(n+1)+".json",'w') as fs: json.dump(paralelInfoToBeRefencedInEachScript[str(n+1)],fs)


'''from mainParalel1 import main as main1
from mainParalel2 import main as main2
from mainParalel3 import main as main3
from mainParalel4 import main as main4

# now run them both in parallel:
thread1=Thread(target=main1)
thread2=Thread(target=main2)
thread3=Thread(target=main3)
thread4=Thread(target=main4)

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()'''