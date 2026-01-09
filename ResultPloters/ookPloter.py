import matplotlib.pyplot as plt
import numpy as np
import random


def CreateOOK(freq,numBits,numSamples):
    ts=np.linspace(0,numBits/freq,numSamples*numBits)
    T=1/freq
    amps=[]
    bits=[random.randint(0,1) for _ in range(numBits)]
    for t in ts:
        ookBin=t//T
        amps.append(bits[int(ookBin)])
    return ts,amps

numBits=10
freq=5000
t,y=CreateOOK(freq,numBits,100)

T=1/freq
for i in range(numBits+1):
    plt.plot([T*i,T*i],[-0.1,1.1],'--',c='k')
plt.plot(t,y,linewidth=2)
plt.xlabel("Tempo")
plt.ylabel("Amplitude")
plt.yticks([0,1])
plt.show()