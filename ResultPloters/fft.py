import numpy as np
import matplotlib.pyplot as plt
import random

def VPPMGenerator(freq,bits,amp,noiseAmp,DC,numPointsPerPeriod):
        ys=[] # vetor de amplitudes
        T=1/freq # período
        #ts=np.linspace(0,T*len(bits),) # vetor de tempos
        ts=np.arange(numPointsPerPeriod*len(bits))*(T/numPointsPerPeriod)
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

            # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
            #   foi percorrida, considerando o dutyCycle
            if infoBit==0:
                if remainder>T*DC: ys.append((-amp/2)+noise)
                else: ys.append((amp/2)+noise)
            else:
                if remainder<T*(1-DC): ys.append((-amp/2)+noise)
                else: ys.append((amp/2)+noise)

        return ts,ys

def GetFFT(freq,dc,noise=0):
    # Parâmetros
    bits=[random.randint(0,1) for _ in range(1000)]
    t,x=VPPMGenerator(freq,bits,1,noise,dc,100)

    # FFT
    N = len(x)
    X = np.fft.fft(x)
    freqs = np.fft.fftfreq(N, t[1]-t[0])

    # Magnitude
    X_mag = np.abs(X)/N

    # Apenas frequências positivas
    mask = freqs >= 1

    return freqs[mask],X_mag[mask]

def PlotInSubplot(xs,ys,maxy=0.16):
    plt.plot([val/1000 for val in xs],ys)
    plt.xlabel("Frequência (kHz)")
    plt.ylabel("Magnitude")
    plt.xlim(0,125)
    plt.grid(True)
    plt.xticks([0,25,50,75,100,125])
    plt.ylim([0,maxy])

def PlotDC(dc,index):
    plt.subplot(3,1,index)
    f,m=GetFFT(50000,dc)
    PlotInSubplot(f,m)
    plt.title("Razão cíclica = "+str(dc))

count=1
for dc in np.linspace(0.2,0.8,3):
    PlotDC(dc,count)
    count+=1

plt.tight_layout()

plt.figure()
f,m=GetFFT(50000,0.5)
PlotInSubplot(f,m,0.03)
plt.xscale("log")
plt.xlim([1,100000])
plt.xticks([1,10,100,1000,10000,100000],["1","10","100","1k","10k","100k"])
plt.show()

