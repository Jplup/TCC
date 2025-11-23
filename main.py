from fullProcessModule import Module
import numpy as np
import json
import time
import os

debugLog=True

# Parametros do sistema
'''
        freq =  \n
        numBits =  \n
        numPointsPerPeriod = Número de pontos gerados por período \n
        numSamples = Número de samples em cada período \n
        X = Distância entre o sensor e a origem no eixo x \n
        Y = Distância entre o sensor e a origem no eixo y \n 
        dutyCycle = O dutyCycle do VPPM \n
        lux = O valor de pico em lux da onda de entrada \n
        SNR = A relação sinal-ruído do sinal \n
        manualAmplitudes = Caso queira valores arbitrários de amplitude de corrente use essa variável
            dessa forma -> [signal_amplitude,noise_amplitude] / Caso queria passar só um valor, coloque
            o outro como valor <0 \n
        '''
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=8 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período
noiseExtremes=[1e-8,1e-7] # Valores máximo e minimo de amplitude de ruído
numNoises=3 # Quantos valores diferentes de ruído serão simulados
noises=np.linspace(noiseExtremes[0],noiseExtremes[1],numNoises) # Vetor de valores de ruído
DCExtremes=[0.325,0.85] # Valores máximo e minimo de duty-cycle
numDC=5 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle
numRepetitions=2 # Quantas vezes serão repetidos os mesmos parâmetros com dados diferentes


# Load os dados do simulador
with open("Simulator\luxResults.json") as fs: simData=json.load(fs)

# Total simulation time info
xLen=len(list(simData.keys())) # Quantos valores diferentes em x serão simulados
yLen=len(list(simData[list(simData.keys())[0]].keys())) # Quantos valores diferentes em y serão simulados
print("Valores de X distintos:",xLen)
print("Valores de Y distintos:",yLen)
totalNum=xLen*yLen*numNoises*numRepetitions*numDC # Número total de simulações
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

for X_Distance in simData.keys():
    for Y_Distance in simData[list(simData.keys())[0]].keys():
        lux=simData[X_Distance][Y_Distance]
        if debugLog: print("X:",X_Distance,"Y:",Y_Distance," -> ",lux)
        for noiseAmp in noises:
            for dc in DCs:
                for n in range(numRepetitions):
                    t0=time.time()
                    obj=Module(VPPMfreq,numBits,numPointsPerPeriod,numSamples,dc,X_Distance,Y_Distance,lux,0,[-1,noiseAmp])
                    
                    # Antes de ser feita a simulação, o dict de resultados é conferido para ver quantas simulações
                    #   com esses parâmetros já foram feitas
                    with open("results.json") as fs: previousData=json.load(fs)
                    key=obj.GetDictKey()
                    try: num=len(previousData[key])
                    except: num=0
                    if debugLog:
                        print("Foram feitas",num,"simulações com os parametros da key:",key)

                    # Se não foram feitas simulações o suficiente, é feita mais uma simulação
                    if num<numRepetitions: obj.Run()
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
                    if countToDeletion>20:
                        countToDeletion=0
                        for path in ['circuit_1.log','circuit_1.net','circuit_1.op.raw','circuit_1.raw','circuit.net']:
                            if os.path.exists(path):
                                os.remove(path)
                    dt=time.time()-t0
                
                    

