import matplotlib.pyplot as plt
import numpy as np

def VPPMGenerator(freq,bits,amp,DC,numPointsPerPeriod):
    ys=[] # vetor de amplitudes
    T=1/freq # período
    ts=np.linspace(0,T*len(bits),numPointsPerPeriod*len(bits)) # vetor de tempos
    # Para cada valor de tempo:
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
            if remainder>T*DC: ys.append(0)
            else: ys.append(amp)
        else:
            if remainder<T*(1-DC): ys.append(0)
            else: ys.append(amp)
    power=np.mean(np.array(ys)**2)

    return ts[:-1],ys[:-1],power

freq=50000
T=1/freq
bits=[0,1,1,0,1]
numSamples=8
dc=0.2
refValues=[0 if val>0.5 else 1 for val in np.linspace(0,1,numSamples)]

colors={
    'signal':'grey',
    'samples':'mediumspringgreen',
    'ref':'mediumblue'
}

times,signal,power=VPPMGenerator(freq,bits,1,dc,100)
plt.plot([val*1000000 for val in times],signal,c=colors["signal"])
for n in range(len(bits)-1):
    t=T*(n+1)*1000000
    plt.plot([t,t],[-0.1,1.1],'--',c='k')

for n in range(len(bits)):
    t0=T*n
    t1=T*(n+1)
    delays=np.linspace(0.1,0.9,numSamples)*T
    for k,delay in enumerate(delays):
        i=np.searchsorted(times,delay+t0)
        plt.scatter(times[i]*1000000,signal[i],marker='o',c=colors['samples'])
        plt.scatter(times[i]*1000000,refValues[k],facecolor='none',edgecolor=colors['ref'])

plt.scatter(times[i]*1000000,signal[i],marker='o',c=colors['samples'],label="Amostras")
plt.scatter(times[i]*1000000,refValues[k],facecolor='none',edgecolor=colors['ref'],label="Referência")
plt.legend()
plt.xlabel("Tempo (us)")
plt.ylabel("Nível lógico")
plt.yticks([0,1])
plt.show()
