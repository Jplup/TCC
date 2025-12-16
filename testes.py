import numpy as np
import matplotlib.pyplot as plt
import random


tempoEntrada=[0,1,2,3,4]
tempoSaida=np.linspace(0,4.5,20)
ampEntrada=[0,1,0,1,0]
novaAmp=np.interp(tempoSaida, tempoEntrada, ampEntrada)

plt.plot(tempoEntrada,ampEntrada,label="Original")
plt.plot(tempoSaida,novaAmp,label="Novo")
plt.legend()
plt.show()

'''
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

def PlotFFT(freq,bits,dc,label,offSet,noise=0):
    # Parâmetros
    t,x=VPPMGenerator(freq,bits,1,noise,dc,1000)

    # FFT
    N = len(x)
    X = np.fft.fft(x)
    freqs = np.fft.fftfreq(N, t[1]-t[0])

    # Magnitude
    X_mag = np.abs(X)/N

    # Apenas frequências positivas
    mask = freqs >= 0

    plt.plot(freqs[mask],[val+offSet for val in X_mag[mask]],label=label)

bits=[random.randint(0,1) for _ in range(100)]
PlotFFT(50000,bits,0.5,"Rand DC=0.5",0)   
PlotFFT(50000,bits,0.2,"Rand DC=0.2",0.2) 
PlotFFT(50000,bits,0.8,"Rand DC=0.8",-0.2)
bits=[0 for _ in range(100)]  
PlotFFT(50000,bits,0.5,"0s DC=0.5",0)    
PlotFFT(50000,bits,0.2,"0s DC=0.2",0.5)  
PlotFFT(50000,bits,0.8,"0s DC=0.8",-0.5)
bits=[random.randint(0,1) for _ in range(100)]
PlotFFT(50000,bits,0.5,"50k",0)
PlotFFT(80000,bits,0.5,"80k",+0.2)
PlotFFT(30000,bits,0.5,"30k",-0.2)

plt.legend()
plt.xlabel("Frequência (Hz)")
plt.ylabel("Magnitude")
plt.xlim(0, 2000e3)
plt.grid(True)
plt.title("FFT do sinal")
plt.show()

'''