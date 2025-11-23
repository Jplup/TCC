import numpy as np
import random
import json
from LTSpiceRunner import Run as RunLTSpice
import matplotlib.pyplot as plt

luxToAmpConverter=75*(10**(-9))
debugLog=True

class Module:
    def __init__(self,freq,numBits,numPointsPerPeriod,numSamples,dutyCycle,X,Y,lux=0,SNR=0,manualAmplitudes=[]):
        '''
        freq = Frequência do sinal VPPM \n
        numBits = Quantos bits de informação no sinal \n
        numPointsPerPeriod = Número de pontos gerados por período \n
        numSamples = Número de samples em cada período \n
        X = Distância entre o sensor e a origem no eixo x \n
        Y = Distância entre o sensor e a origem no eixo y \n 
        dutyCycle = O dutyCycle do VPPM \n
        lux = O valor de pico em lux da onda de entrada \n
        SNR = A relação sinal-ruído do sinal \n
        manualAmplitudes = Caso queira valores arbitrários de amplitude de corrente use essa variável
            dessa forma -> [signal_amplitude,noise_amplitude] / Caso queria passar só um valor, coloque
            o outro como valor <0 \n
        '''
        self.freq=freq
        self.numBits=numBits
        self.numPointsPerPeriod=numPointsPerPeriod
        self.numSamples=numSamples
        self.dutyCycle=dutyCycle
        self.SNR=SNR
        self.X=X
        self.Y=Y
        self.lux=lux
        self.amp=self.lux*luxToAmpConverter
        self.noiseAmp=self.amp/(2*(10**(SNR/20)))
        if len(manualAmplitudes)>0:
            if manualAmplitudes[0]>0: self.amp=manualAmplitudes[0]
            if manualAmplitudes[1]>0: self.noiseAmp=manualAmplitudes[1]
            self.SNR=20*np.log10(self.amp/self.noiseAmp)
        if debugLog:
            print("----------------------------------------------------")
            print("Objeto gerado com esses parâmetros:")
            print("   Frequência VPPM:",freq,"Hz")
            print("   Número de bits de informação:",numBits)
            print("   Número de pontos gerados por período:",numPointsPerPeriod)
            print("   Número de amostras por período",numSamples)
            print("   Duty-cycle do VPPM:",dutyCycle)
            print("   Distância entre o sensor e a origem no eixo x:",X,"m")
            print("   Distância entre o sensor e a origem no eixo y:",Y,"m")
            if len(manualAmplitudes)>0 and manualAmplitudes[0]>0: print("   Pico de lux no sensor: +-",self.amp/luxToAmpConverter)
            else: print("   Pico de lux no sensor:",lux)
            print("   Amplitude de sinal:",self.amp,"A")
            print("   Amplitude do ruído:",self.noiseAmp,"A")
            print("   SNR:",self.SNR,"dB")

    # -------------------------------- Modulação --------------------------------
    
    def GenerateData(self,dataType):
        # Geração de dados VPPM
        data=[0,0] # Primeiro bit é sempre descartado para esperar passar o transitório do circuito e o segundo é o de referencia para a demodulação
        if dataType==1:
            for _ in range(int((self.numBits-2)/2)):
                data.append(0)
                data.append(1)
        else:
            if dataType==2:
                for _ in range(int((self.numBits-2)/4)):
                    data.append(0)
                    data.append(0)
                    data.append(1)
                    data.append(1)
            else:
                for _ in range(self.numBits):
                    data.append(random.randint(0,1))
        self.inputData=data
        if debugLog: print("Bits de sinal gerados:",self.inputData)

    # Gera a onda de sinal de corrente com dados VPPM
    def VPPMGenerator(self):
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
            except: infoBit=self.inputData[-1]
            # Gera o ruído
            noise=np.random.normal(0,self.noiseAmp)
            amplitude=self.amp

            # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
            #   foi percorrida, considerando o dutyCycle
            if infoBit==0:
                if remainder>T*self.dutyCycle: ys.append(noise)
                else: ys.append(amplitude+noise)
            else:
                if remainder<T*(1-self.dutyCycle): ys.append(noise)
                else: ys.append(amplitude+noise)
        self.inputTime=ts
        self.inputWave=ys

        # Save input to .txt
        with open("testegenerate_1k.txt", "w") as f:
            for t, v in zip(ts,ys):
                f.write(f"{t:.6e}\t{v:.6e}\n")

        if debugLog:
            plt.figure()
            plt.plot([t/1000 for t in ts],ys,c='r')
            maxAmp=max(ys)
            minAmp=min(ys)
            dA=maxAmp-minAmp
            for n in range(self.numBits+3):
                periodTransition=T*n/1000
                plt.plot([periodTransition,periodTransition],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c='k')
            plt.grid("true")
            plt.title("Onda de corrente gerada")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (A)")

    # -------------------------------- Demodulação --------------------------------

    # Recebe a onda de referência e retorna os indexes do vetor onde acontecem as 
    #   transições de um período para o outro
    def GetInterruptPoints(self,time):
        interruptIndexes=[]
        for n in range(self.numBits+2):
            targetTime=(n+1)/self.freq
            i=np.searchsorted(time,targetTime)
            interruptIndexes.append(i)
        
        return interruptIndexes

    # Faz a demodulação
    def Demodulate(self,time,wave,title=""):
        sampleIndexes=self.GetInterruptPoints(time) # Os indexes do vetor de tempo que contém transições de período
        bits=[]
        delays=np.linspace(0.05,0.95,self.numSamples) # Os pontos de amostragem de um período

        if debugLog:
            plt.figure()
            plt.title("Onda de saída simulada"+title)
            plt.plot([t/1000 for t in time],wave,c='b')
            plt.grid("true")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (V)")
            maxAmp=max(wave)
            minAmp=min(wave)
            dA=maxAmp-minAmp
            for i in sampleIndexes:
                plt.plot([time[i]/1000,time[i]/1000],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c='k')
        
        firstBit=True
        refValues=[]
        refValuesUnsat=[]
        printCount=0
        for n in range(len(sampleIndexes)-1):
            a=sampleIndexes[n]
            b=sampleIndexes[n+1]
            xors=[]
            waveSats=[]
            for iD,delay in enumerate(delays):
                try:
                    targetTime=time[a]+(time[b]-time[a])*delay
                except:
                    targetTime=time[a]+(time[-1]-time[a])*delay
                i=np.searchsorted(time, targetTime)
                if i>=len(wave): i=len(wave)-1

                if firstBit:
                    refSat=1 if wave[i] > 1.65 else 0
                    refValues.append(refSat)
                    refValuesUnsat.append(wave[i])
                else:
                    ref=refValues[iD]
                    waveSat=1 if wave[i] > 1.65 else 0
                    waveSats.append(waveSat)
                    if debugLog:
                        plt.scatter(time[i]/1000,wave[i],c='g')
                        plt.scatter(time[i]/1000,refValuesUnsat[iD],marker='x',c='r')
                        lastX=[time[i]/1000,refValuesUnsat[iD]]
                        lastDot=[time[i]/1000,wave[i]]
                    xors.append(ref ^ waveSat)
            if not firstBit:
                bits.append(1 if np.mean(xors) > 0.5 else 0)
                if debugLog and printCount<15:
                    print("-------")
                    print("  Reference values:",refValues)
                    print("  Sampled values:  ",waveSats)
                    print("  xors:            ",xors)
                    print("  mean:            ",np.mean(xors),"-> Bit:",bits[-1])
                    printCount+=1
            firstBit=False
        if debugLog:
            plt.scatter(lastDot[0],lastDot[1],c='g',label="Pontos de amostra")
            plt.scatter(lastX[0],lastX[1],marker='x',c='r',label="Referência")
            plt.legend()
        return bits
    
    # -------------------------------- Main --------------------------------

    def GetDictKey(self):
        simStr="n_samples="+str(self.numSamples)
        simStr+="/dc="+str(self.dutyCycle)
        simStr+="/n_bits="+str(self.numBits)
        simStr+="/sig_amp="+self.RoundJP(str(self.amp))
        simStr+="/noise_amp="+self.RoundJP(str(self.noiseAmp))
        simStr+="/lux="+self.RoundJP(str(self.lux))
        simStr+="/SNR="+self.RoundJP(str(self.SNR))
        simStr+="/X="+str(self.X)
        simStr+="/Y="+str(self.Y)

        return simStr
    
    @staticmethod
    def NormalizeWave(wave):
        minValue=min(wave)
        maxLoweredValue=max([a-minValue for a in wave])
        return [(a-minValue)/maxLoweredValue for a in wave]

    @staticmethod
    def RoundJP(string,decimalPlaces=2):
        try:
            numberAndExponent=string.split("e")
            return str(round(float(numberAndExponent[0]),decimalPlaces))+"e"+numberAndExponent[1]
        except:
            return str(round(float(string),decimalPlaces))
    
    def Run(self,dataType=3):
        '''
        dataType = Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
        '''

        # Create input wave
        self.GenerateData(dataType)
        self.VPPMGenerator()

        # Run LTSpice
        if debugLog: print("Running LTSpice")
        gain=2**np.ceil(np.log2(1.4/(self.amp*700000)))
        outputWaves=RunLTSpice(['V(v_comp)','V(v_comp_sat)','V(v_comp_pga)','V(filtered)','V(amp)','V(sat)'],gain)

        # Demodulation
        time=outputWaves["t"]
        filtered=outputWaves["V(v_comp)"]
        filteredSat=outputWaves["V(v_comp_sat)"]
        filteredPGA=outputWaves["V(v_comp_pga)"]

        result=self.Demodulate(time,filtered," só filtro")
        resultSat=self.Demodulate(time,filteredSat," Saturado")
        resultPGA=self.Demodulate(time,filteredPGA," com PGA")

        if debugLog:
            plt.figure()
            plt.title("Comparação entre ondas com e sem PGA (gain"+str(int(gain))+") e sat")
            plt.plot([t/1000 for t in time],outputWaves["V(amp)"],c='r',label="PGA")
            plt.plot([t/1000 for t in time],outputWaves["V(filtered)"],c='b',label="Filtered")
            plt.plot([t/1000 for t in time],outputWaves["V(sat)"],c='g',label="Sat")
            for n in range(self.numBits+3):
                periodTransition=(1/self.freq)*n/1000
                plt.plot([periodTransition,periodTransition],[-0.1,1.1],'--',c='k')
            plt.legend()
            plt.grid("true")
            plt.xlabel("Tempo (us)")

        if debugLog:

            print("Resultado da demodulação:",result)
            print("Bits enviados:           ",self.inputData[2:])
            plt.figure()
            plt.title("Comparação entre ondas de input e output")
            plt.plot([t/1000 for t in self.inputTime],self.NormalizeWave(self.inputWave),c='r',label="Input")
            plt.plot([t/1000 for t in time],self.NormalizeWave(filtered),c='b',label="Output")
            for n in range(self.numBits+3):
                periodTransition=(1/self.freq)*n/1000
                plt.plot([periodTransition,periodTransition],[-0.1,1.1],'--',c='k')
            plt.legend()
            plt.grid("true")
            plt.xlabel("Tempo (us)")

        # Cálculo da BER
        erros=0
        for o,d in zip(self.inputData[2:],result):
            if not (o-d)==0: erros+=1
        relativeError=erros/(self.numBits-2)

        # Cálculo da BER
        errossat=0
        for o,d in zip(self.inputData[2:],resultSat):
            if not (o-d)==0: errossat+=1
        relativeErrorsat=errossat/(self.numBits-2)

        # Cálculo da BER
        errospga=0
        for o,d in zip(self.inputData[2:],resultPGA):
            if not (o-d)==0: errospga+=1
        relativeErrorpga=errospga/(self.numBits-2)


        if debugLog:
            print("Erros:",erros)
            print("Erro relativo (BER):",relativeError)
            print("Erros:",errospga)
            print("Erro relativo (BER):",relativeErrorpga)
            print("Erros:",errossat)
            print("Erro relativo (BER):",relativeErrorsat)
            plt.show()

        with open("results.json") as fs: oldResults=json.load(fs)
        simStr="n_samples="+str(self.numSamples)
        simStr+="/dc="+str(self.dutyCycle)
        simStr+="/n_bits="+str(self.numBits)
        simStr+="/sig_amp="+self.RoundJP(str(self.amp))
        simStr+="/noise_amp="+self.RoundJP(str(self.noiseAmp))
        simStr+="/lux="+self.RoundJP(str(self.lux))
        simStr+="/SNR="+self.RoundJP(str(self.SNR))
        simStr+="/X="+str(self.X)
        simStr+="/Y="+str(self.Y)

        try: oldResults[simStr].append([relativeError,relativeErrorpga,relativeErrorsat])
        except: oldResults[simStr]=[[relativeError,relativeErrorpga,relativeErrorsat]]
        with open("results.json",'w') as fs: json.dump(oldResults,fs)

        if debugLog: print("Resultados salvos")



