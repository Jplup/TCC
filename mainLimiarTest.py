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
DCExtremes=[0.2,0.8] # Valores máximo e minimo de duty-cycle
numDC=7 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle
midValues=np.linspace(0.009,0.050,15)

totalNum=numDC*len(midValues) # Número total de simulações
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
countToDeletion=3

dt=1 # Quanto tempo passou entre o começo e o final da última simulação
cont=0 # Contador de simulações para prever quanto tempo vai demorar para a acabar

circuit="circuit_LimiarTest.asc"
resultDir="limiarTest.json"

circuitName=circuit.split(".")[0]
sufixes=[".raw",".op.raw",".net",".log",".fail"]
deletionPaths=[]
for sufix in sufixes:
    deletionPaths.append(circuitName+sufix)
    deletionPaths.append(circuitName+"_1"+sufix)
maxSimsBeforeDeletion=2

nodes=[
    "V(compideal)"
]

trigger=2

'''obj=Module(VPPMfreq,100,numPointsPerPeriod,numSamples,0.5,1,1,20,[-1,0])
ts=obj.inputTime
sunLux=[1600*(75*(10**-9)) for _ in range(len(ts))]
obj.Run(circuit,nodes,False,{})
input()'''

def calculateMidResistor(midValue):
    r2=10000
    razao=(3.3/midValue)-1
    r1=int(r2*razao)
    lenth=len(str(r1))
    if lenth>4: newR1=str(int(r1/1000))+"k"
    else: newR1=str(r1)
    return newR1

for midValue in midValues:
    for dc in DCs:
        t0=time.time()
        obj=Module(VPPMfreq,100,numPointsPerPeriod,numSamples,dc,midValue,1,22,[-1,0])
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
        if num<1:
            # Full process run
            R1=calculateMidResistor(midValue)
            print("R1=",R1)
            simStr,errors=obj.Run(circuit,nodes,trigger,{"R_MID":R1})
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
        
        # Print de progresso total
        if not debugLog:
            print("Saved")

        # Deleta os arquivos de info do LTSpice caso o contador chegue no limite
        if countToDeletion>=maxSimsBeforeDeletion:
            countToDeletion=0
            Clean()
        dt=time.time()-t0

