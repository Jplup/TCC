import matplotlib.pyplot as plt
import numpy as np
import random


def CreatePWM(freq,numBits,numSamples,dc0,dc1):
    ts=np.linspace(0,numBits/freq,numSamples*numBits)
    T=1/freq
    ys=[]
    bits=[random.randint(0,1) for _ in range(numBits)]
    for t in ts:
        # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
        remainder=t%T
        vppmBin=t//T
        # Vê na lista de dados, qual o dado desse bin
        try: infoBit=bits[int(vppmBin)]
        except: infoBit=bits[-1]

        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*dc0: ys.append(0)
            else: ys.append(1)
        else:
            if remainder>T*dc1: ys.append(0)
            else: ys.append(1)
    return ts,ys


numBits=6
freq=5000
t,y=CreatePWM(freq,numBits,100,0.2,0.8)

T=1/freq
for i in range(numBits+1):
    plt.plot([T*i,T*i],[-0.1,1.1],'--',c='k')
plt.plot(t,y,linewidth=2)
plt.xlabel("Tempo")
plt.ylabel("Amplitude")
plt.yticks([0,1])
plt.show()