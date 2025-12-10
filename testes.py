import numpy as np
import matplotlib.pyplot as plt
import random

xs = [3, 1, 2]
ys = [4, 23, 111]

pairs = sorted(zip(xs, ys))  
xs, ys = map(list, zip(*pairs))

print(xs)  
print(ys) 

input()

def VPPMGenerator(freq,bits,amp,noiseAmp,DC,numPointsPerPeriod):
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
            # Gera o ruído
            noise=np.random.normal(0,noiseAmp)

            # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
            #   foi percorrida, considerando o dutyCycle
            if infoBit==0:
                if remainder>T*DC: ys.append(noise)
                else: ys.append(amp+noise)
            else:
                if remainder<T*(1-DC): ys.append(noise)
                else: ys.append(amp+noise)

        return ts,ys

# Parâmetros

t,x=VPPMGenerator(50000,[random.randint(0,1) for _ in range(100)],2,0,0.5,1000)

t=[val-0.5 for val in t]

# FFT
N = len(x)
X = np.fft.fft(x)
freqs = np.fft.fftfreq(N, 1/(50000*1000))

# Magnitude
X_mag = np.abs(X)/N

# Apenas frequências positivas
mask = freqs >= 0

plt.figure()
plt.plot(freqs[mask], X_mag[mask])
plt.title("FFT do sinal")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.show()
