import numpy as np
import random
import matplotlib.pyplot as plt
from PyLTSpice import SimRunner, SpiceEditor, LTspice  
import ltspice
from pathlib import Path
from LTSpiceCleaner import Clean

def RunLTSPiceFrFr(circuit,valueChanges):
    asc_path = Path(__file__).parent / circuit

    runner = SimRunner(simulator=LTspice)
    editor = SpiceEditor(asc_path)

    for label,value in valueChanges.items():
        editor.set_component_value(label,str(value))

    raw_path, log_path = runner.run_now(editor)
    return raw_path

def RunLTSpice(circuit,nodeNames,valueChanges:dict={},run:bool=True):
    if run:
        try:
            raw_path=RunLTSPiceFrFr(circuit,valueChanges)
        except:
            print("--------------------------First dint work--------------------------")
            Clean()
            try:
                newValueChanges={key:val for key,val in valueChanges.items()}
                newValueChanges["R_DEBUG"]="1m"
                raw_path=RunLTSPiceFrFr(circuit,newValueChanges)
            except:
                print("--------------------------Second dint work--------------------------")
                Clean()
                try:
                    newValueChanges={key:val for key,val in valueChanges.items()}
                    newValueChanges["R_DEBUG"]="1"
                    raw_path=RunLTSPiceFrFr(circuit,newValueChanges)
                except:
                    print("--------------------------Pau no seu cu piranha--------------------------")
    else: raw_path=circuit.split(".")[0]+"_1.raw"

    l = ltspice.Ltspice(raw_path)
    l.parse()

    waves = {"t": l.get_time()}
    for nodeName in nodeNames:
        vals=l.getData(nodeName)
        if vals is None: print(f"Nó {nodeName} não encontrado")
        else: waves[nodeName]=vals

    return waves

luxToAmpConverter=75*(10**(-9))
debugLog=False

class Module:
    def __init__(self,freq,numBits,numPointsPerPeriod,numSamples,dutyCycle,X,Y,lux=0,manualAmplitudes=[],numPackets=1):
        '''
        freq = Frequência do sinal VPPM \n
        numBits = Quantos bits de informação no sinal \n
        numPointsPerPeriod = Número de pontos gerados por período \n
        numSamples = Número de samples em cada período \n
        X = Distância entre o sensor e a origem no eixo x \n
        Y = Distância entre o sensor e a origem no eixo y \n 
        dutyCycle = O dutyCycle do VPPM \n
        lux = O valor de pico em lux da onda de entrada \n
        manualAmplitudes = Caso queira valores arbitrários de amplitude de corrente use essa variável
            dessa forma -> [signal_amplitude,noise_amplitude,...] / Caso queria passar só um valor, coloque
            o outro como valor <0 \n
            Lista de amplitudes em ordem: \n
            \t Sinal \n
            \t Ruído branco \n
            \t Luz do Sol (dc) \n
            \t A partir desse index, é para outras VPPMs ou frequências artificiais adicionais
            dessa forma: [amplitude,frequência,é VPPM ou não (booleano)]. Exemplo desse parâmetro completo:\n
            \t \t [-1,1e-7,-1,[2e-6,40000,True],[4e-7,120,False]] \n
        numPackets = Quantos pacotes de 'numBits' serão enviados
        '''
        self.freq=freq
        self.numBits=numBits
        self.numPointsPerPeriod=numPointsPerPeriod
        self.numSamples=numSamples
        self.dutyCycle=dutyCycle
        self.X=X
        self.Y=Y
        self.lux=lux
        self.amp=self.lux*luxToAmpConverter
        self.numPackets=numPackets
        self.otherWaves=[]
        if len(manualAmplitudes)>0:
            if manualAmplitudes[0]>=0: self.amp=manualAmplitudes[0]
            try:
                if manualAmplitudes[1]>=0: self.noiseAmp=manualAmplitudes[1]
            except: pass
            try:
                if manualAmplitudes[2]>=0: self.sunlight=manualAmplitudes[2]
                else: self.sunlight=0
            except: pass
            try:
                for i in range(len(manualAmplitudes)-3): self.otherWaves.append(manualAmplitudes[i+3])
            except: pass
    
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
            print("   Amplitude do ruído branco:",self.noiseAmp,"A")

    # -------------------------------- Modulação --------------------------------
    
    def GenerateData(self,dataType):
        self.inputData=[0] # Primeiro bit é sempre descartado para esperar passar o transitório do circuito
        for _ in range(self.numPackets):
            # Geração de dados VPPM
            data=[0] # O primeiro bit de cada pacote é o de referencia para a demodulação
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
            for bit in data: self.inputData.append(bit)

    # Gera a onda de sinal de corrente com dados VPPM
    @staticmethod
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

    # -------------------------------- Demodulação --------------------------------

    # Recebe os valores de tempo e retorna os indexes do vetor onde acontecem as 
    #   transições de um período para o outro sem detecção de borda de subida
    def GetInterruptPoints(self,time):
        interruptIndexesSuper=[]
        for p in range(self.numPackets):
            interruptIndexes=[]
            for n in range(self.numBits+2):
                targetTime=((n/self.freq)+(p*(self.numBits+1))/self.freq)+(1/self.freq)
                i=np.searchsorted(time,targetTime)
                if i in interruptIndexes or i>=len(time): continue
                interruptIndexes.append(i)
            interruptIndexesSuper.append(interruptIndexes)
        return interruptIndexesSuper
    
    # Recebe os valores de tempo e amplitude e retorna os indexes do vetor onde acontecem as 
    #   transições de um período para o outro com detecção de borda de subida
    def GetInterruptIndexesTrig(self,time,wave):
        # É definido o index correspondente a 90% de um período como o ponto inicial para detectar a
        #   borda de subida (basicamente pula o primeiro bit)
        inicialIndex=np.searchsorted(time,0.9/self.freq)
        interruptIndexesSuper=[] # Lista de listas de transições de período (uma lista para cada pacote)
        # Faz um loop dentro de todos os valores de tempo do primeiro pacote até achar a primeira borda de subida
        for i in range(int(len(wave)/self.numPackets)):
            try:
                previous=wave[i+inicialIndex]
                current=wave[i+1+inicialIndex]
            except: return interruptIndexesSuper
            if previous<1.65 and current>1.65 or current==1.65:
                firstInterrupt=i+inicialIndex
                break

        for p in range(self.numPackets):
            timeOfFirstInterrupt=time[firstInterrupt]
            interruptIndexes=[]
            for n in range(self.numBits+2):
                targetTime=(n/self.freq)+timeOfFirstInterrupt+(p*(self.numBits+1))/self.freq
                i=np.searchsorted(time,targetTime)
                if i in interruptIndexes or i>=len(wave): continue
                interruptIndexes.append(i)            
            interruptIndexesSuper.append(interruptIndexes)
        return interruptIndexesSuper

    # Faz a demodulação
    def Demodulate(self,time,wave,title="",indexesFunc=""):
        if indexesFunc=="trig":
            try: sampleIndexes=self.GetInterruptIndexesTrig(time,wave) # Os indexes do vetor de tempo que contém transições de período
            except: return [[]]
        else: sampleIndexes=self.GetInterruptPoints(time)
        bits=[]
        delays=np.linspace(0.05,0.95,self.numSamples) # Os pontos de amostragem de um período
        
        if debugLog:
            plt.figure()
            plt.title("Onda de saída simulada"+title)
            plt.plot([t*1000 for t in time],wave,c='b')
            plt.grid("true")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (V)")
            maxAmp=max(wave)
            minAmp=min(wave)
            dA=maxAmp-minAmp
            colorIndex=0
            colors=['k','r','g']
            for sampleIndexesInPacket in sampleIndexes:
                for j in sampleIndexesInPacket:
                    plt.plot([time[j]*1000,time[j]*1000],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c=colors[colorIndex])
                colorIndex+=1
                if colorIndex>=len(colors): colorIndex=0


        maxPrints=5
        #targetTimes=[]
        # For each packet
        for sampleIndexesInPacket in sampleIndexes:
            firstBitOfPacket=True
            refValues0=[]
            refValuesUnsat=[]
            refValues1=[]
            printCount=0
            # For each symbol
            for n in range(len(sampleIndexesInPacket)-1):
                a=sampleIndexesInPacket[n]
                b=sampleIndexesInPacket[n+1]
                xors0=[]
                xors1=[]
                waveSats=[]

                # For each sample in 1 symbol
                for indexOfDelay,delay in enumerate(delays):
                    try: targetTime=time[a]+(time[b]-time[a])*delay
                    except: targetTime=time[a]+(time[-1]-time[a])*delay
                    #targetTimes.append(targetTime)
                    i=np.searchsorted(time,targetTime)
                    if i>=len(wave): i=len(wave)-1

                    if firstBitOfPacket:
                        refSat=1 if wave[i]>1.65 else 0
                        refValues0.append(refSat)
                        refValuesUnsat.append(wave[i])
                    else:
                        waveSat=1 if wave[i]>1.65 else 0
                        waveSats.append(waveSat)

                        # Calculation for 0 correlation
                        ref=refValues0[indexOfDelay]
                        xors0.append(ref^waveSat)
                        # Calculation for 1 correlation
                        ref=refValues1[indexOfDelay]
                        xors1.append(ref^waveSat)

                        if debugLog:
                            plt.scatter(time[i]*1000,wave[i],c='y')
                            plt.scatter(time[i]*1000,refValuesUnsat[indexOfDelay],marker='x',c='m')
                            lastX=[time[i]*1000,refValuesUnsat[indexOfDelay]]
                            lastDot=[time[i]*1000,wave[i]]
                
                if firstBitOfPacket:
                    refValues1=[v for v in refValues0]
                    refValues1.reverse()
                        
                if not firstBitOfPacket:
                    bits.append(1 if np.mean(xors1)<np.mean(xors0) else 0)
                    if debugLog:
                        if printCount<maxPrints:
                            print("-------------------------------------")
                            print("  Reference values0:",refValues0)
                            print("  Reference values1:",refValues1)
                            print("  Sampled values:   ",waveSats)
                            print("  xors0:            ",xors0)
                            print("  mean0:            ",np.mean(xors0))
                            print("  xors1:            ",xors1)
                            print("  mean1:            ",np.mean(xors1))
                            print("  Bit:              ",bits[-1])
                            printCount+=1
                        else: print("  Bit:",bits[-1])
                    
                firstBitOfPacket=False

        if debugLog:
            try: plt.scatter(lastDot[0],lastDot[1],c='y',label="Pontos de amostra")
            except: pass
            try: plt.scatter(lastX[0],lastX[1],marker='x',c='m',label="Referência")
            except: pass
            plt.legend()

        return bits
    
    # Faz a demodulação
    def Demodulate2(self,time,wave,title="",indexesFunc=""):
        if indexesFunc=="trig":
            try: sampleIndexes=self.GetInterruptIndexesTrig(time,wave) # Os indexes do vetor de tempo que contém transições de período
            except: return [[]]
        else: sampleIndexes=self.GetInterruptPoints(time)
        bits=[]
        delays=np.linspace(0.05,0.95,self.numSamples) # Os pontos de amostragem de um período
        
        if debugLog:
            plt.figure()
            plt.title("Onda de saída simulada"+title)
            plt.plot([t*1000 for t in time],wave,c='b')
            plt.grid("true")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (V)")
            maxAmp=max(wave)
            minAmp=min(wave)
            dA=maxAmp-minAmp
            colorIndex=0
            colors=['k','r','g']
            for sampleIndexesInPacket in sampleIndexes:
                for j in sampleIndexesInPacket:
                    plt.plot([time[j]*1000,time[j]*1000],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c=colors[colorIndex])
                colorIndex+=1
                if colorIndex>=len(colors): colorIndex=0

        maxPrints=5
        targetTimes=[]
        # For each packet
        for sampleIndexesInPacket in sampleIndexes:
            # For each symbol
            for n in range(len(sampleIndexesInPacket)-1):
                a=sampleIndexesInPacket[n]
                b=sampleIndexesInPacket[n+1]
                # For each sample in 1 symbol
                for indexOfDelay,delay in enumerate(delays):
                    try: targetTime=time[a]+(time[b]-time[a])*delay
                    except: targetTime=time[a]+(time[-1]-time[a])*delay
                    targetTimes.append(targetTime)
        targetIndexes=np.searchsorted(time,targetTimes)
        
        aux=0
        # For each packet
        for sampleIndexesInPacket in sampleIndexes:
            firstBitOfPacket=True
            refValues0=[]
            refValuesUnsat=[]
            refValues1=[]
            printCount=0
            # For each symbol
            for n in range(len(sampleIndexesInPacket)-1):
                a=sampleIndexesInPacket[n]
                b=sampleIndexesInPacket[n+1]
                xors0=[]
                xors1=[]
                waveSats=[]

                # For each sample in 1 symbol
                for indexOfDelay,delay in enumerate(delays):
                    i=targetIndexes[aux]
                    aux+=1
                    if i>=len(wave): i=len(wave)-1

                    if firstBitOfPacket:
                        refSat=1 if wave[i]>1.65 else 0
                        refValues0.append(refSat)
                        refValuesUnsat.append(wave[i])
                    else:
                        waveSat=1 if wave[i]>1.65 else 0
                        waveSats.append(waveSat)

                        # Calculation for 0 correlation
                        ref=refValues0[indexOfDelay]
                        xors0.append(ref^waveSat)
                        # Calculation for 1 correlation
                        ref=refValues1[indexOfDelay]
                        xors1.append(ref^waveSat)

                        if debugLog:
                            plt.scatter(time[i]*1000,wave[i],c='y')
                            plt.scatter(time[i]*1000,refValuesUnsat[indexOfDelay],marker='x',c='m')
                            lastX=[time[i]*1000,refValuesUnsat[indexOfDelay]]
                            lastDot=[time[i]*1000,wave[i]]
                
                if firstBitOfPacket:
                    refValues1=[v for v in refValues0]
                    refValues1.reverse()
                        
                if not firstBitOfPacket:
                    bits.append(1 if np.mean(xors1)<np.mean(xors0) else 0)
                    if debugLog:
                        if printCount<maxPrints:
                            print("-------------------------------------")
                            print("  Reference values0:",refValues0)
                            print("  Reference values1:",refValues1)
                            print("  Sampled values:   ",waveSats)
                            print("  xors0:            ",xors0)
                            print("  mean0:            ",np.mean(xors0))
                            print("  xors1:            ",xors1)
                            print("  mean1:            ",np.mean(xors1))
                            print("  Bit:              ",bits[-1])
                            printCount+=1
                        else: print("  Bit:",bits[-1])
                    
                firstBitOfPacket=False

        if debugLog:
            try: plt.scatter(lastDot[0],lastDot[1],c='y',label="Pontos de amostra")
            except: pass
            try: plt.scatter(lastX[0],lastX[1],marker='x',c='m',label="Referência")
            except: pass
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
        simStr+="/X="+str(self.X)
        simStr+="/Y="+str(self.Y)

        return simStr

    @staticmethod
    def RoundJP(string,decimalPlaces=2):
        try:
            numberAndExponent=string.split("e")
            return str(round(float(numberAndExponent[0]),decimalPlaces))+"e"+numberAndExponent[1]
        except:
            return str(round(float(string),decimalPlaces))
    
    def BER(self,outputBits):
        errors=0
        for i,iBit in enumerate(self.dataBits):
            try:
                oBit=outputBits[i]
                if not iBit==oBit: errors+=1
            except: errors+=1
        return errors/(len(self.dataBits))

    
    def Run(self,circuit,nodes,trigger=0,valueChanges:dict={},aditionalNoises=[]):
        '''
        dataType = Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
        '''

        # Create input wave
        self.GenerateData(3)
        ts,ys=self.VPPMGenerator(self.freq,self.inputData,self.amp,self.noiseAmp,self.dutyCycle,self.numPointsPerPeriod)
        self.inputTime=ts
        self.inputWave=ys

        for aditionalNoise in aditionalNoises:
            for i in range(len(self.inputWave)):
                self.inputWave[i]+=aditionalNoise[i]

            
        if True:
            # Save input to .txt
            with open("fullCircuitInput.txt", "w") as f:
                for t, v in zip(self.inputTime,self.inputWave):
                    f.write(f"{t:.6e}\t{v:.6e}\n")

        if debugLog:
            plt.figure()
            plt.plot([t*1000 for t in self.inputTime],self.inputWave,c='r')
            maxAmp=max(self.inputWave)
            minAmp=min(self.inputWave)
            dA=maxAmp-minAmp
            for n in range((self.numBits+1)*self.numPackets+2):
                periodTransition=n*1000/self.freq
                plt.plot([periodTransition,periodTransition],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c='k')
            plt.grid("true")
            plt.title("Onda de corrente gerada")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (A)")
        plt.show()
        # Cria uma versão da onda de entrada 
        self.pureTs,self.pureYs=self.VPPMGenerator(self.freq,self.inputData,self.amp,0,self.dutyCycle,self.numPointsPerPeriod)


        # Run LTSpice
        if debugLog: print("Running LTSpice")
        outputWaves=RunLTSpice(circuit,nodes,valueChanges,True)


        # Get only data bits
        dataBits=[]
        for i in range(len(self.inputData)-1):
            remainder=i%(self.numBits+1)
            if remainder==0: pass
            else: dataBits.append(self.inputData[i+1])
        self.dataBits=dataBits

        # Demodulation and BER calculation
        time=outputWaves["t"]
        errors={}
        for node in nodes:
            wave=outputWaves[node]
            if trigger==0:
                result=self.Demodulate(time,wave,node,"")
                BER=self.BER(result)
                errors[node]=BER
            elif trigger==1:
                resultTrig=self.Demodulate(time,wave,node+" trig","trig")
                BERtrig=self.BER(resultTrig)
                errors[node+"_Trig"]=BERtrig
            else:
                result=self.Demodulate(time,wave,node,"")
                BER=self.BER(result)
                errors[node]=BER
                resultTrig=self.Demodulate(time,wave,node+" trig","trig")
                BERtrig=self.BER(resultTrig)
                errors[node+"_Trig"]=BERtrig
            
        
        # Print results
        if debugLog:
            maxLen=max(len(label) for label in errors.keys())
            for label,value in errors.items():
                print(f"{label:<{maxLen}} : {value}")
            plt.show()
        


        '''if debugLog:
            plt.figure()
            plt.title("Comparação entre ondas com e sem PGA (gain"+str(int(gain))+") e sat")
            plt.plot([t*1000 for t in time],outputWaves["V(pga)"],c='r',label="PGA")
            plt.plot([t*1000 for t in time],outputWaves["V(filtered)"],c='b',label="Filtered")
            plt.plot([t*1000 for t in time],outputWaves["V(sat)"],c='g',label="Sat")
            for n in range((self.numBits+1)*self.numPackets+2):
                periodTransition=(1/self.freq)*n*1000
                plt.plot([periodTransition,periodTransition],[-0.1,1.1],'--',c='k')
            plt.legend()
            plt.grid("true")
            plt.xlabel("Tempo (us)")

        if debugLog:
            print("Resultado da demodulação:",result)
            plt.figure()
            plt.title("Comparação entre ondas de input e output")
            plt.plot([t*1000 for t in self.inputTime],self.NormalizeWave(self.inputWave),c='r',label="Input")
            plt.plot([t*1000 for t in time],self.NormalizeWave(filtered),c='b',label="Output")
            for n in range((self.numBits+1)*self.numPackets+2):
                periodTransition=(1/self.freq)*n*1000
                plt.plot([periodTransition,periodTransition],[-0.1,1.1],'--',c='k')
            plt.legend()
            plt.grid("true")
            plt.xlabel("Tempo (us)")'''

        

        simStr="n_samples="+str(self.numSamples)
        simStr+="/dc="+str(self.dutyCycle)
        simStr+="/n_bits="+str(self.numBits)
        simStr+="/sig_amp="+self.RoundJP(str(self.amp))
        simStr+="/noise_amp="+self.RoundJP(str(self.noiseAmp))
        simStr+="/lux="+self.RoundJP(str(self.lux))
        simStr+="/X="+str(self.X)
        simStr+="/Y="+str(self.Y)

        return simStr,errors



