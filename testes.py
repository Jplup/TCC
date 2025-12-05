import numpy as np
import matplotlib.pyplot as plt
import random

def VPPMGenerator(bits,DC,noiseAmp):
    ys=[] # vetor de amplitudes
    T=1/50000 # período
    ts=np.linspace(0,T*len(bits),1000*len(bits)) # vetor de tempos
    # Para cada valor de tempo:
    for t in ts:
        # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
        remainder=t%T
        vppmBin=t//T
        # Vê na lista de dados, qual o dado desse bin
        try: infoBit=bits[int(vppmBin)]
        except: infoBit=bits[-1]
        # Gera o ruído
        noise=np.random.normal(0,noiseAmp)
        amplitude=5

        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*DC: ys.append(noise)
            else: ys.append(amplitude+noise)
        else:
            if remainder<T*(1-DC): ys.append(noise)
            else: ys.append(amplitude+noise)
    return ts,ys

def NormalizeWave(wave):
    minVal=min(wave)
    amp=np.max(np.array(wave)-minVal)
    return [(val-minVal)/amp for val in wave]

ts,ys=VPPMGenerator([random.randint(0,1) for _ in range(10)],0.3,0.3)

plt.plot(ts,NormalizeWave(ys))
plt.show()

def Pot(signal): return np.mean(np.array(signal)**2)

plt.figure()
plt.plot([t*1000 for t in ts],ys,c='r')
plt.grid("true")
plt.title("Potência:"+str(Pot(ys)))
plt.xlabel("Tempo (us)")
plt.ylabel("Amplitude (A)")
plt.show()