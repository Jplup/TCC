from fullProcessModule import Module
import numpy as np

VPPMfreq=50000
numBits=100
numPointsPerPeriod=100
numSamples=10

SNRoffset=1.81

for distance in np.linspace(1.5,3,4):
    for SNR in np.linspace(-5+SNRoffset,15+SNRoffset,10):
        for n in range(1):
            print("-------------------------------------------------------------")
            obj=Module(VPPMfreq,numBits,numPointsPerPeriod,0,0,numSamples,0,0,0.5,distance,SNR)
            obj.Run()
            '''print("AmpExp:",ampExp)
            print("NoiseExp:",noiseExp)
            print("Amp:",amp)
            print("NoiseAmp:",noiseAmp)'''
            print("Distance:",distance)
            print("SNR:",SNR)
            print("N:",n)
            #input()
                    

