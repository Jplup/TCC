import numpy as np
import matplotlib.pyplot as plt
import random
import json
from ReadData import readFile

VPPMfreq=1000
numBits=20
numPointsPerPeriod=100
ampExp=6
amplitude=1*(10**(-ampExp))
delay=0.1

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
        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*dutyCycle: ys.append(0)
            else: ys.append(amp)
        else:
            if remainder<T*(1-dutyCycle): ys.append(0)
            else: ys.append(amp)
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
print("Data gerada:",data)

# Geração da forma de onda
time,amp=VPPMGenerator(numPointsPerPeriod,VPPMfreq,amplitude,data,0.5)
with open("testegenerate_1k.txt", "w") as f:
    for t, v in zip(time,amp):
        f.write(f"{t:.6e}\t{v:.6e}\n")

plt.plot(time,amp,label="Dados")

# Geração da referência
time,amp=VPPMGenerator(numPointsPerPeriod,VPPMfreq,amplitude,[0 for _ in range(numBits)],0.5)
'''with open("testegenerate_1kref.txt", "w") as f:
    for t, v in zip(time,amp):
        f.write(f"{t:.6e}\t{v:.6e}\n")'''

plt.plot(time,[a-1.2*amplitude for a in amp],label="Ref")
plt.grid("true")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (A)")
plt.legend()
plt.title("Onda gerada")


# -------------------------------- LTSpice --------------------------------


# -------------------------------- Demodulation --------------------------------


def GetInterruptPoints(reference):
    interruptIndexes=[]
    for i in range(len(reference)-3):
        last=reference[i+2]
        current=reference[i+3]
        if current==1.65:
            interruptIndexes.append(i)
        if last<1.65 and current>1.65: 
            interruptIndexes.append(i)
    return interruptIndexes

def SampleWithDelay(time,wave,sampleIndexes):
    values=[]
    debugLog=False
    indexes=[]
    for n in range(len(sampleIndexes)-1):

        currentI=sampleIndexes[n]
        nextI=sampleIndexes[n+1]
        di=nextI-currentI

        currentT=time[currentI]
        nextT=time[nextI]
        targetTime=((nextT-currentT)*delay)+currentT

        if debugLog: print("Current time:",currentT)
        if debugLog: print("Next time:",nextT)
        if debugLog: print("Target time:",targetTime)
        if debugLog: print("Delay:",delay)

        # Binary search
        a=currentI
        b=currentI+int(di*delay)
        c=nextI

        if debugLog: print("Começando busca binária")
        while True:
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])
            if debugLog: print("   Target:",targetTime)
            if time[b]<targetTime:
                if debugLog: print("   if1")
                a=b
            if time[b]==targetTime:
                if debugLog: print("   Achou, brekou")
                break
            if time[b]>targetTime:
                if debugLog: print("   if2")
                c=b
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])

            if (c-a)<2:
                if debugLog: print("   if3")
                if c==a:
                    b=a
                    if debugLog: print("   if4")
                    break
                else:
                    c=a+1
                    if debugLog: print("   if5")
                    break
            b=int(((c-a)/2)+a)
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])
            if debugLog: print("------------------------------------------------")
        
        if debugLog: print("Busca acabou")
        if debugLog: print("Tempo achado:",time[b])
        if debugLog: print("Tempo target:",targetTime)
        if debugLog: print("Erro relativo:",(abs(time[b]-targetTime)/targetTime)*100)
        if debugLog: input()
            
        try:
            values.append(wave[b])
            indexes.append(b)
        except: pass

    plt.figure()
    plt.plot(time,filtered)
    plt.scatter([time[i] for i in indexes],[filtered[i] for i in indexes])
    dt=1/VPPMfreq
    t=0
    while t<(1/VPPMfreq)*numBits:
        plt.plot([t,t],[0,3.3],c='r')
        t+=dt
    plt.title("Sampled output wave")

    return values
        
def Demodulate(time,filtered,senoidalRef,invertCheck=False):
    # Get interrupt times and indexes
    interruptIndexes=GetInterruptPoints(senoidalRef)
    sampledValues=SampleWithDelay(time,filtered,interruptIndexes)
    demodulatedData=[]
    for sampledValue in sampledValues:
        if invertCheck:
            if sampledValue>1.65: demodulatedData.append(0)
            else: demodulatedData.append(1)
        else:
            if sampledValue>1.65: demodulatedData.append(1)
            else: demodulatedData.append(0)
    return demodulatedData

def GetOutputWaves():
    pathOutput="outputVoltage.txt"
    outputData=readFile(pathOutput)
    time=outputData['time']
    filtro=outputData["V(v_comp)"]
    ref=outputData["V(v_ref)"]

    return time,filtro,ref

def GetInputInfo(DC,randIndex):
    if randIndex>0:
        if randIndex==1: sufix=""
        else: sufix=str(randIndex)
        pathInput="LTspiceInput/DC0"+str(DC)+"_rand"+sufix+".txt"
    else:
        pathInput="LTspiceInput/DC0"+str(DC)+"_01.txt"
    return readFile(pathInput,True)

input("Foi salva a forma de onda?")

time,filtered,reference=GetOutputWaves()
result=Demodulate(time,filtered,reference)
print("Result:     ",result)

erros=0
for o,d in zip(data[1:],result[1:]):
    if not (o-d)==0: erros+=1
relativeError=erros/(numBits-1)

print("Erros:",erros)
print("Erro relativo:",relativeError)

with open("results.json") as fs: oldResults=json.load(fs)
try:
    dic=oldResults[str(delay)+"/"+str(numBits-1)+"/"+str(ampExp)].append(relativeError)
except: oldResults[str(delay)+"/"+str(numBits-1)+"/"+str(ampExp)]=[relativeError]
with open("results.json",'w') as fs: json.dump(oldResults,fs) 
plt.show()