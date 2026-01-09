import time
from LTSpiceCleaner import Clean
import os
import numpy as np
import random
import matplotlib.pyplot as plt
from PyLTSpice import SimRunner, SpiceEditor, LTspice  
import ltspice
from pathlib import Path
import json

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
            return
    else: raw_path=circuit.split(".")[0]+"_1.raw"

    l = ltspice.Ltspice(raw_path)
    l.parse()

    waves = {"t": l.get_time()}
    for nodeName in nodeNames:
        vals=l.getData(nodeName)
        if vals is None: print(f"Nó {nodeName} não encontrado")
        else: waves[nodeName]=vals

    for key in waves.keys():
        waves[key]=[float(val) for val in waves[key]]
    return waves

luxToAmpConverter=75*(10**(-9))
debugLog=False
numDummyBits=5

class Module:
    def __init__(self,freq,numBits,numPointsPerPeriod,numSamples,dutyCycle,X,Y,lux=0,manualAmplitudes=[],numPackets=1,useRealComp=False):
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
        self.inputWave=[]
        self.useRealComp=useRealComp
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
    
    def GenerateData(self,dataType=3):
        inputData=[0 for _ in range(numDummyBits)] # Primeiro bit é sempre descartado para esperar passar o transitório do circuito
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
            for bit in data: inputData.append(bit)
        return inputData

    # Gera a onda de sinal de corrente com dados VPPM
    @staticmethod
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

        return ts,ys,power

    # -------------------------------- Main --------------------------------
    
    def GenerateInput(self):
        # Create input wave
        self.inputData=self.GenerateData()
        self.inputTime,self.inputWave,self.pureWavePower=self.VPPMGenerator(self.freq,self.inputData,self.amp,self.dutyCycle,self.numPointsPerPeriod)
        self.noisyInput=[max(y+np.random.normal(0,self.noiseAmp),0) for y in self.inputWave]
    
    def Run(self,circuit:str,nodes,trigger=0,valueChanges:dict={},aditionalNoises=[],LTSpiceInputDir="fullCircuitInput.txt"):
        '''
        dataType = Se os dados gerados devem ser 0101...(1) ou 00110011...(2) ou random(3)
        '''
        
        if len(self.inputWave)<1: self.GenerateInput()


        for aditionalNoise in aditionalNoises:
            for i in range(len(self.inputWave)):
                self.noisyInput[i]+=aditionalNoise[i]
        
            
        if True:
            # Save input to .txt
            with open(LTSpiceInputDir, "w") as f:
                for t, v in zip(self.inputTime,self.noisyInput):
                    f.write(f"{t:.6e}\t{v:.6e}\n")

        if debugLog:
            plt.figure()
            plt.plot([t*1000 for t in self.inputTime],self.noisyInput,c='r')
            maxAmp=max(self.noisyInput)
            minAmp=min(self.noisyInput)
            dA=maxAmp-minAmp
            for n in range((self.numBits+1)*self.numPackets+2):
                periodTransition=n*1000/self.freq
                plt.plot([periodTransition,periodTransition],[minAmp-0.1*dA,maxAmp+0.1*dA],'--',c='k')
            plt.grid("true")
            plt.title("Onda de corrente gerada")
            plt.xlabel("Tempo (us)")
            plt.ylabel("Amplitude (A)")

        # Run small LTSpice sim to calculate gain
        smallCircuit=circuit.split(".asc")[0]+"_small.asc"
        outputWavesSmall=RunLTSpice(smallCircuit,["V(filtered)"],{},True)
        firstIndex=np.searchsorted(outputWavesSmall["t"],0.2/1000)
        cropedWave=outputWavesSmall["V(filtered)"][firstIndex:]
        dVFilter=max(cropedWave)-min(cropedWave)
        print("dVMesured:",dVFilter)
        print("Caculated value:",self.lux*luxToAmpConverter*45000*40)
        realGain=min(2**np.ceil(np.log2(1.4/(dVFilter))),128)
        r1=10000*(realGain-1)
        if r1<100: r1=100
        print("Gain:",realGain,"R1:",r1)
    
        # Run LTSpice
        outputWavesPGA=RunLTSpice(circuit,nodes["BER"],{"R_PGA":int(r1)},True)
        print("Finalizou PGA run, esperando 3 segundos")
        time.sleep(3)
        outputWaves=RunLTSpice(circuit,nodes["BER"],{},True)
    
        return {"no":outputWaves,"PGA":outputWavesPGA}


debugLog=False

# Parametros do sistema
VPPMfreq=50000 # Frequência do sinal VPPM
numBits=20 # Quantos bits de informação no sinal
numPointsPerPeriod=100 # Número de pontos gerados por período
numSamples=10 # Número de samples em cada período

# Load os dados do simulador
with open("Simulator/luxResults.json") as fs: simData=json.load(fs)
with open("Simulator/luxResultsVPPM2.json") as fs: vppm2=json.load(fs)
with open("Simulator/luxResultsILU_CSE.json") as fs: ilu1=json.load(fs)
with open("Simulator/luxResultsILU_CSD.json") as fs: ilu2=json.load(fs)
with open("sunlight.json") as fs: theSun=json.load(fs)


# Transforma segundos para o formato: x horas y minutos z segundos (ChatGPT)
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

def GenerateOtherWaves(X,Y,obj:Module,addSun=False):
    luxAmp=75*(10**(-9))

    # VPPM lum
    #vppm2Lux=vppm2[X][Y]
    #tsss,vppm2Wave,poewr=obj.VPPMGenerator(100000,obj.GenerateData(),vppm2Lux*luxAmp,0.5,obj.numPointsPerPeriod)

    tss=np.array(obj.inputTime)
    # Ilu 1
    ilu1Amp=ilu1[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu1Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu1Amp)

    # Ilu 2
    ilu2Amp=ilu2[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu2Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu2Amp)

    # Ilu 3
    ilu3Amp=vppm2[X][Y]*luxAmp
    faseOffset=np.random.randint(-100,100)/100
    ilu3Wave=np.abs(np.sin(tss*2*np.pi*60+faseOffset)*ilu3Amp)
    if not addSun:
        return [ilu1Wave,ilu2Wave,ilu3Wave]
    else:
        sunStrenth=theSun[X][Y]
        sunLight=[sunStrenth*luxAmp for _ in tss]
        return [ilu1Wave,ilu2Wave,ilu3Wave,sunLight]

# Percebi que se deixar o script rodando por muito tempo alguma coisa para de funcionar, então criei
#   esse contador que exclui todos os arquivos de dados do LTSpice depois de um certo número de iterações.
#   Isso concerta o problema
countToDeletion=0
dt=1 # Quanto tempo passou entre o começo e o final da última simulação
cont=0 # Contador de simulações para prever quanto tempo vai demorar para a acabar

positions=[
    [1,1],
    [7,7],
    [-2,-2]
]
print("Keys:",simData.keys())
input()

for position in positions:
    X=list(simData.keys())[position[0]]
    Y=list(simData[X])[position[1]]

    print("Keys:",simData.keys())

    print("Position:",position,"X:",X,"Y:",Y)
    lux=simData[X][Y]

    print("Lux:",lux)
    #input()

    circuit="circuit_full_real_15.asc"
    resultDir="LTSpiceSimResults/PGA_timeWaves/X-"+X+"_Y-"+Y+".json"
    maxSimsBeforeDeletion=1
    BER_nodes=["V(pga)"]
    nodes={"BER":BER_nodes}
    trigger=1

    obj=Module(VPPMfreq,numBits,numPointsPerPeriod,numSamples,0.5,X,Y,lux,[-1,1e-7],1,True)
    # Antes de ser feita a simulação, o dict de resultados é conferido para ver quantas simulações
    #   com esses parâmetros já foram feitas
    if not os.path.exists(resultDir):
        with open(resultDir,"w") as fs: json.dump({},fs)


    Clean()
    # Full process run
    obj.GenerateInput()
    addicionalNoises=GenerateOtherWaves(X,Y,obj,True)
    waves=obj.Run(circuit,nodes,trigger,{},addicionalNoises)

    with open(resultDir,'w') as fs: json.dump(waves,fs)
    if debugLog: print("Resultados salvos")




                        
