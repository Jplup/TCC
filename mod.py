import numpy as np
import matplotlib.pyplot as plt
import random

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
            print("Deu except no try")
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

frequencia=1000
numDados=10
numPointsPerPeriod=100
amplitude=1.125e-6

# Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
dataType=3

# Geração de dados VPPM
data=[]
if dataType==1:
    for n in range(int(numDados/2)):
        data.append(0)
        data.append(1)
else:
    if dataType==2:
        for n in range(int(numDados/4)):
            data.append(0)
            data.append(0)
            data.append(1)
            data.append(1)
    else:
        for n in range(numDados):
            data.append(random.randint(0,1))
print("Data:",data)

# Geração da forma de onda
time,amp=VPPMGenerator(numPointsPerPeriod,frequencia,amplitude,data,0.5)
with open("testegenerate_1k.txt", "w") as f:
    for t, v in zip(time,amp):
        f.write(f"{t:.6e}\t{v:.6e}\n")

plt.plot(time,amp,label="Dados")

# Geração da referência
time,amp=VPPMGenerator(numPointsPerPeriod,frequencia,amplitude,[0 for _ in range(numDados)],0.5)
with open("testegenerate_1kref.txt", "w") as f:
    for t, v in zip(time,amp):
        f.write(f"{t:.6e}\t{v:.6e}\n")

plt.plot(time,[a-1.2*amplitude for a in amp],label="Ref")
plt.grid("true")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (A)")
plt.legend()
plt.show()



