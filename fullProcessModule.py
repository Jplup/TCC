import numpy as np
import random
import json
from LTSpiceRunner import Run as RunLTSpice
import matplotlib.pyplot as plt

luxToAmpConverter=75*(10**(-9))

class Module:
    def __init__(self,freq,numBits,numPointsPerPeriod,ampExp,amp,numSamples,noiseExp,noiseAmp,dutyCycle,distance=-1,SNR=[]):
        '''
        freq = Frequência do sinal VPPM
        numBits = Quantos bits de informação no sinal
        numPointsPerPeriod = Número de pontos gerados por período
        amp = Amplitude da onda
        ampExp = Exponent of wave (wave amp = 'amp'*10^'ampExp')
        numSamples = Número de samples em cada período
        noiseAmp = Amplitude do ruído
        noiseExp = Exponent of noise (noise amp = 'noiseAmp'*10^'noiseExp')
        dutyCycle = O dutyCycle do VPPM
        distance = A distancia até a luminária (use número <0 para usar 'amp')
        SNR = A relação sinal-ruído do sinal (não coloque valor para usar 'noiseAmp')
        '''
        self.freq=freq
        self.numBits=numBits
        self.numPointsPerPeriod=numPointsPerPeriod
        self.ampExp=ampExp
        self.amp=amp
        self.numSamples=numSamples
        self.noiseExp=noiseExp
        self.noiseAmp=noiseAmp
        self.dutyCycle=dutyCycle
        self.distance=distance
        self.SNR=SNR
        if distance>0: self.GetAmpFromDistance(distance)
        if not (type(SNR)==type([])): self.GetNoiseAmpFromSNR(SNR)

    def GetAmpFromDistance(self,distance):
        self.amp=(4.31/((distance-1.1)**2))*luxToAmpConverter
        self.ampExp=1
    
    def GetNoiseAmpFromSNR(self,SNR):
        self.noiseAmp=self.amp/(2*(10**(SNR/20)))
        self.noiseExp=self.ampExp
        '''print("Noise:",self.noiseAmp*(10**(-self.noiseExp)))
        print("Noise amp:",self.noiseAmp)
        print("SNR:",SNR)'''

    # -------------------------------- Modulação --------------------------------
    
    def GenerateData(self,dataType):
        # Geração de dados VPPM
        data=[]
        if dataType==1:
            for _ in range(int(self.numBits/2)):
                data.append(0)
                data.append(1)
        else:
            if dataType==2:
                for _ in range(int(self.numBits/4)):
                    data.append(0)
                    data.append(0)
                    data.append(1)
                    data.append(1)
            else:
                for _ in range(self.numBits):
                    data.append(random.randint(0,1))
        self.inputData=data

    # Gera a onda de sinal de corrente com dados VPPM
    def VPPMGenerator(self):
        '''
        numPoints = Número de pontos em cada período
        freq = Frequência do sinal VPPM
        amp = Amplitude da onda
        finalTime = Tempo final da onda (vai de 0 até esse valor)
        data = Vetor de dados a serem codificados
        dutyCycle = O dutyCycle do VPPM
        '''
        ys=[] # vetor de amplitudes
        T=1/self.freq # período
        ts=np.linspace(0,T*len(self.inputData),self.numPointsPerPeriod*len(self.inputData)) # vetor de tempos
        # Para cada valor de tempo:
        for t in ts:
            # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
            remainder=t%T
            vppmBin=t//T
            # Vê na lista de dados, qual o dado desse bin
            try: infoBit=self.inputData[int(vppmBin)]
            except:
                #print("Deu except no try")
                infoBit=self.inputData[-1]

            noise=(random.randint(-100,100)/100)*self.noiseAmp*(10**(-self.noiseExp))
            amplitude=self.amp*(10**(-self.ampExp))

            # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
            #   foi percorrida, considerando o dutyCycle
            if infoBit==0:
                if remainder>T*self.dutyCycle: ys.append(noise)
                else: ys.append(amplitude+noise)
            else:
                if remainder<T*(1-self.dutyCycle): ys.append(noise)
                else: ys.append(amplitude+noise)

        # Save input to .txt
        with open("testegenerate_1k.txt", "w") as f:
            for t, v in zip(ts,ys):
                f.write(f"{t:.6e}\t{v:.6e}\n")

    # -------------------------------- Demodulação --------------------------------

    # Recebe a onda de referência e retorna os indexes do vetor onde acontecem as 
    #   transições de um período para o outro
    def GetInterruptPoints(self,reference):
        interruptIndexes=[]
        for i in range(len(reference)-3):
            last=reference[i+2]
            current=reference[i+3]
            if current==1.65:
                interruptIndexes.append(i)
            if last<1.65 and current>1.65: 
                interruptIndexes.append(i)
        interruptIndexes.append(len(reference)-1)
        return interruptIndexes

    # Faz a demodulação
    def Demodulate(self,time,wave,reference):
        sampleIndexes=self.GetInterruptPoints(reference)
        bits=[]
        delays=np.linspace(0.1,0.9,self.numSamples)

        debugPrintLog=False
        if debugPrintLog:
            plt.figure()
            plt.plot(time,wave)
            for i in sampleIndexes:
                plt.plot([time[i],time[i]],[0,3.3],c='r')
        
        first=True
        for n in range(len(sampleIndexes)-1):
            a=sampleIndexes[n]
            b=sampleIndexes[n+1]
            xors=[]
            
            for delay in delays:
                targetTime=time[a]+(time[b]-time[a])*delay
                i=np.searchsorted(time, targetTime)
                if i>=len(wave): i=len(wave)-1
                
                ref=1 if np.sin(time[i]*2*np.pi*self.freq) > 0 else 0
                waveSat=1 if wave[i] > 1.65 else 0
                if debugPrintLog:
                    plt.scatter(time[i],wave[i],c='k')
                    plt.scatter(time[i],ref,c='g')
                    plt.scatter(time[i],waveSat,c='b')
                    if first:
                        print("Delay",delay)
                        print("  Ref:",ref)
                        print("  Wave sat:",waveSat)
                xors.append(ref ^ waveSat)
            if first and debugPrintLog:
                print("xors:",xors)
                print("mean:",np.mean(xors))
            first=False
            bits.append(0 if np.mean(xors) > 0.5 else 1)
        if debugPrintLog: plt.show()
        return bits
    
    # -------------------------------- Main --------------------------------
    
    def Run(self,dataType=3):
        '''
        dataType -> Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
        '''

        # Create input wave
        self.GenerateData(dataType)
        self.VPPMGenerator()
        print("Input wave generated")
        print("Dados gerados:",self.inputData[1:])

        # Run LTSpice
        outputWaves=RunLTSpice()

        # Demodulation
        time=outputWaves["t"]
        filtered=outputWaves["V(v_comp)"]
        reference=outputWaves["V(v_ref)"]
        result=self.Demodulate(time,filtered,reference)
        print("Result:     ",result)
        erros=0
        for o,d in zip(self.inputData[1:],result):
            if not (o-d)==0: erros+=1
        relativeError=erros/(self.numBits-1)

        print("Erros:",erros)
        print("Erro relativo:",relativeError)

        with open("results.json") as fs: oldResults=json.load(fs)
        simStr="n_samples="+str(self.numSamples)
        simStr+="/dc="+str(self.dutyCycle)
        simStr+="/n_bits="+str(self.numBits-1)
        simStr+="/sig_amp="+str(self.amp)+"e-"+str(self.ampExp)
        simStr+="/noise_amp="+str(self.noiseAmp)+"e-"+str(self.noiseExp)
        simStr+="/distance="+str(self.distance)
        simStr+="/SNR="+str(self.SNR)
        try:
            oldResults[simStr].append(relativeError)
        except: oldResults[simStr]=[relativeError]
        with open("results.json",'w') as fs: json.dump(oldResults,fs)

        print("Result saved")

        



        '''plt.plot(time,filtered,label="Comp")
        plt.plot(time,reference,label="Ref")
        plt.grid("true")
        plt.xlabel("Time (s)")
        plt.ylabel("Mag")
        plt.legend()
        plt.show()'''


