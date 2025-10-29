import numpy as np
import random
import json
from LTSpiceRunner import Run
import matplotlib.pyplot as plt

VPPMfreq=50000
numBits=20
numPointsPerPeriod=100
ampExp=6
amplitude=1*(10**(-ampExp))
numSamples=10
noiseExp=7
noiseAmp=0


# -------------------------------- Modulação --------------------------------

# Gera a onda de sinal de corrente com dados VPPM
def VPPMGenerator(numPoints,freq,amp,data,dutyCycle):
    '''
    numPoints = Número de pontos em cada período
    freq = Frequência do sinal VPPM
    amp = Amplitude da onda
    finalTime = Tempo final da onda (vai de 0 até esse valor)
    data = Vetor de dados a serem codificados
    dutyCycle = O dutyCycle do VPPM
    '''
    ys=[] # vetor de amplitudes
    T=1/freq # período
    ts=np.linspace(0,T*len(data),numPoints*len(data)) # vetor de tempos
    # Para cada valor de tempo:
    for t in ts:
        # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
        remainder=t%T
        vppmBin=t//T
        # Vê na lista de dados, qual o dado desse bin
        try: infoBit=data[int(vppmBin)]
        except:
            #print("Deu except no try")
            infoBit=data[-1]

        noise=(random.randint(-100,100)/100)*noiseAmp*(10**(-noiseExp))

        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*dutyCycle: ys.append(noise)
            else: ys.append(amp+noise)
        else:
            if remainder<T*(1-dutyCycle): ys.append(noise)
            else: ys.append(amp+noise)
    return ts,ys

# Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
dataType=3

# Geração de dados VPPM
data=[]
if dataType==1:
    for n in range(int(numBits/2)):
        data.append(0)
        data.append(1)
else:
    if dataType==2:
        for n in range(int(numBits/4)):
            data.append(0)
            data.append(0)
            data.append(1)
            data.append(1)
    else:
        for n in range(numBits):
            data.append(random.randint(0,1))
print("Data gerada:",data[1:])

# Geração da forma de onda
time,amp=VPPMGenerator(numPointsPerPeriod,VPPMfreq,amplitude,data,0.5)
with open("testegenerate_1k.txt", "w") as f:
    for t, v in zip(time,amp):
        f.write(f"{t:.6e}\t{v:.6e}\n")

# Geração da referência
time,amp=VPPMGenerator(numPointsPerPeriod,VPPMfreq,amplitude,[0 for _ in range(numBits)],0.5)


# -------------------------------- LTSpice --------------------------------
outputWaves=Run()

# -------------------------------- Demodulação --------------------------------

# Recebe a onda de referência e retorna os indexes do vetor onde acontecem as 
#   transições de um período para o outro
def GetInterruptPoints(reference):
    interruptIndexes=[]
    for i in range(len(reference)-3):
        last=reference[i+2]
        current=reference[i+3]
        if current==1.65:
            interruptIndexes.append(i)
        if last<1.65 and current>1.65: 
            interruptIndexes.append(i)
    interruptIndexes.append(len(reference)-1)
    return interruptIndexes

# Faz a demodulação
def Demodulate(time,wave,reference):
    sampleIndexes=GetInterruptPoints(reference)
    bits=[]
    delays=np.linspace(0.1,0.9,numSamples)

    debugPrintLog=False
    if debugPrintLog:
        plt.figure()
        plt.plot(time,wave)
        for i in sampleIndexes:
            plt.plot([time[i],time[i]],[0,3.3],c='r')
    
    first=True
    for n in range(len(sampleIndexes)-1):
        a=sampleIndexes[n]
        b=sampleIndexes[n+1]
        xors=[]
        
        for delay in delays:
            targetTime=time[a]+(time[b]-time[a])*delay
            i=np.searchsorted(time, targetTime)
            if i>=len(wave): i=len(wave)-1
            
            ref=1 if np.sin(time[i]*2*np.pi*VPPMfreq) > 0 else 0
            waveSat=1 if wave[i] > 1.65 else 0
            if debugPrintLog:
                plt.scatter(time[i],wave[i],c='k')
                plt.scatter(time[i],ref,c='g')
                plt.scatter(time[i],waveSat,c='b')
                if first:
                    print("Delay",delay)
                    print("  Ref:",ref)
                    print("  Wave sat:",waveSat)
            xors.append(ref ^ waveSat)
        if first and debugPrintLog:
            print("xors:",xors)
            print("mean:",np.mean(xors))
        first=False
        bits.append(0 if np.mean(xors) > 0.5 else 1)
    if debugPrintLog: plt.show()
    return bits
        
'''def GetOutputWaves():
    pathOutput="circuit.txt"
    outputData=readFile(pathOutput)
    time=outputData['time']
    filtro=outputData["V(v_comp)"]
    ref=outputData["V(v_ref)"]

    return time,filtro,ref'''

time=outputWaves["t"]
filtered=outputWaves["V(v_comp)"]
reference=outputWaves["V(v_ref)"]
'''plt.plot(time,filtered,label="Comp")
plt.plot(time,reference,label="Ref")
plt.grid("true")
plt.xlabel("Time (s)")
plt.ylabel("Mag")
plt.legend()
plt.show()'''
result=Demodulate(time,filtered,reference)
print("Result:     ",result)

erros=0
for o,d in zip(data[1:],result):
    if not (o-d)==0: erros+=1
relativeError=erros/(numBits-1)

print("Erros:",erros)
print("Erro relativo:",relativeError)

with open("results.json") as fs: oldResults=json.load(fs)
simStr="s="+str(numSamples)+"/b="+str(numBits-1)+"/a=1e-"+str(ampExp)+"/n="+str(noiseAmp)+"e-"+str(noiseExp)
try:
    dic=oldResults[simStr].append(relativeError)
except: oldResults[simStr]=[relativeError]
with open("results.json",'w') as fs: json.dump(oldResults,fs) 
