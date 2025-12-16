from fullProcessModule import Module
import numpy as np
import json
import time
from LTSpiceCleaner import Clean

debugLog=True

# Parametros do sistema
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=1000 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período
noiseExtremes=[1e-8,1e-7] # Valores máximo e minimo de amplitude de ruído
numNoises=2 # Quantos valores diferentes de ruído serão simulados
noises=np.linspace(noiseExtremes[0],noiseExtremes[1],numNoises) # Vetor de valores de ruído
noises=[1e-8,1e-7,5e-7]
DCExtremes=[0.2,0.8] # Valores máximo e minimo de duty-cycle
numDC=3 # Quantos valores diferentes de duty-cycle serão simulados
DCs=np.linspace(DCExtremes[0],DCExtremes[1],numDC) # Vetor de valores de duty-cycle
numRepetitions=1 # Quantas vezes serão repetidos os mesmos parâmetros com dados diferentes
numPackets=1

# Load os dados do simulador
with open("Simulator/luxResults.json") as fs: simData=json.load(fs)
with open("Simulator/luxResultsVPPM2.json") as fs: vppm2=json.load(fs)
with open("Simulator/luxResultsILU_CSE.json") as fs: ilu1=json.load(fs)
with open("Simulator/luxResultsILU_CSD.json") as fs: ilu2=json.load(fs)

# Total simulation time info
xLen=len(list(simData.keys())) # Quantos valores diferentes em x serão simulados
yLen=len(list(simData[list(simData.keys())[0]].keys())) # Quantos valores diferentes em y serão simulados
print("Valores de X distintos:",xLen)
print("Valores de Y distintos:",yLen)
totalNum=xLen*yLen*len(noises)*numRepetitions*len(DCs)*numPackets # Número total de simulações
print("Número total de simulações:",totalNum)

# Transforma segundos para o formato: x horas y minutos z segundos (ChatGPT)
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

def GenerateOtherWaves(X,Y,obj:Module):
    luxAmp=75*(10**(-9))

    # VPPM lum
    #vppm2Lux=vppm2[X][Y]
    #tsss,vppm2Wave,poewr=obj.VPPMGenerator(100000,obj.GenerateData(),vppm2Lux*luxAmp,0.5,obj.numPointsPerPeriod)

    tss=np.array(obj.inputTime)
    # Ilu 1
    ilu1Amp=ilu1[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu1Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu1Amp)

    # Ilu 2
    ilu2Amp=ilu2[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu2Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu2Amp)

    # Ilu 3
    ilu3Amp=vppm2[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu3Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu3Amp)
    return [ilu1Wave,ilu2Wave,ilu3Wave]

# Percebi que se deixar o script rodando por muito tempo alguma coisa para de funcionar, então criei
#   esse contador que exclui todos os arquivos de dados do LTSpice depois de um certo número de iterações.
#   Isso concerta o problema
countToDeletion=0
dt=1 # Quanto tempo passou entre o começo e o final da última simulação
cont=0 # Contador de simulações para prever quanto tempo vai demorar para a acabar

circuit="circuit_filter.asc"
resultDir="LTSpiceSimResults/filterXtiaN1.json"
maxSimsBeforeDeletion=1
BER_nodes=[
    "V(comp_filter)",
    "V(comp_tia)"
]
Pot_nodes=[
    "V(tia)",
    "V(filtered)"
]
nodes={"BER":BER_nodes,"Pot":Pot_nodes}
trigger=2

'''obj=Module(VPPMfreq,1000,numPointsPerPeriod,numSamples,0.2,0,0,17.5,[-1,1e-8])
obj.GenerateInput()
addicionalNoises=GenerateOtherWaves("0.0","0.0",obj)
simStr,errors,SNR=obj.Run(circuit,nodes,trigger,{},addicionalNoises)
#print("Erros:",errors)
input()'''

for noiseAmp in noises:
    for X_Distance in simData.keys():
        for Y_Distance in simData[list(simData.keys())[0]].keys():
            lux=simData[X_Distance][Y_Distance]
            if debugLog: print("X:",X_Distance,"Y:",Y_Distance," -> ",lux)
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
                        obj.GenerateInput()
                        #addicionalNoises=GenerateOtherWaves(X_Distance,Y_Distance,obj)
                        simStr,errors,potencies=obj.Run(circuit,nodes,trigger)
                        errors["Pot"]=potencies
                        print("Erros:",errors)
                        currentSNR=potencies["current_ideal"]/potencies["current_noise"]
                        tiaSNR=potencies["voltage_ideal"]/potencies["V(tia)_noise"]
                        filterSNRDCless=potencies["voltage_ideal_0"]/potencies["V(filtered)_noise"]
                        #filterSNR165=potencies["voltage_ideal_0"]/potencies["V(filtered)_noise2"]
                        '''print("SNRs:")
                        print("  input:",currentSNR,"=",20*np.log10(currentSNR),"dB")
                        print("  tia:",tiaSNR,"=",20*np.log10(tiaSNR),"dB")
                        print("  filter DCless:",filterSNRDCless,"=",20*np.log10(filterSNRDCless),"dB")'''
                        #print("  filter 165:",filterSNR165,"=",20*np.log10(filterSNR165),"dB")
                        errors["SNR"]={
                            "input":currentSNR,
                            "tia":tiaSNR,
                            "filter":filterSNRDCless
                        }
                        # Save results
                        with open(resultDir) as fs: oldResults=json.load(fs)
                        try: oldResults[simStr].append(errors)
                        except: oldResults[simStr]=[errors]
                        with open(resultDir,'w') as fs: json.dump(oldResults,fs)
                        if debugLog: print("Resultados salvos")
                        
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