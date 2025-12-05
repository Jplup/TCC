import numpy as np
import matplotlib.pyplot as plt
from PyLTSpice import SimRunner, SpiceEditor, LTspice  
import ltspice
from pathlib import Path
import time
import json

numData=10
paddingPediods=3
pointsPerPeriod=300


def Run(nodeNames):
    asc_path = Path(__file__).parent / "Comparator.asc"
    runner = SimRunner(simulator=LTspice)
    editor = SpiceEditor(asc_path)
    raw_path, log_path = runner.run_now(editor)

    l = ltspice.Ltspice(raw_path)
    l.parse()

    waves = {"t": [float(val) for val in l.get_time()]}
    for nodeName in nodeNames:
        try:
            waves[nodeName] = [float(val) for val in l.getData(nodeName)]
        except:
            print(f"Nó {nodeName} não encontrado")

    return waves

def Read(nodeNames):
    l = ltspice.Ltspice("AmpOps.raw")
    l.parse()

    waves = {"t": l.get_time()}
    for nodeName in nodeNames:
        try:
            waves[nodeName] = l.getData(nodeName)
        except:
            print(f"Nó {nodeName} não encontrado")

    return waves


def VPPMGenerator(dutyCycle,noise,amplitude):
    ys=[] # vetor de amplitudes
    T=1/50000 # período
    ts=np.linspace(0,T*(numData+paddingPediods),pointsPerPeriod*(numData+paddingPediods)) # vetor de tempos
    # Para cada valor de tempo:
    for t in ts:
        # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
        remainder=t%T
        # Vê na lista de dados, qual o dado desse bin
        infoBit=0
        # Gera o ruído
        noise=np.random.normal(0,noise)
        noise=0

        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*dutyCycle: ys.append(-amplitude+noise)
            else: ys.append(amplitude+noise)
        else:
            if remainder<T*(1-dutyCycle): ys.append(noise-amplitude)
            else: ys.append(amplitude+noise)

    return list(ts),ys

def SaveWaveInTxt(ts,ys):
    # Save input to .txt
    with open("comparatorWave.txt", "w") as f:
        for t, v in zip(ts,ys):
            f.write(f"{t:.6e}\t{v:.6e}\n")

def GetInterruptIndexes(wave):
    interruptIndexes=[]
    for i in range(len(wave)-1):
        previous=wave[i]
        current=wave[i+1]
        if previous<1.65 and current>1.65 or current==1.65:
            interruptIndexes.append(i)
    return interruptIndexes

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

DCs=np.linspace(0.01,0.99,20)

noiseExps=[]
ampExps=[]

ts,ys=VPPMGenerator(0.5,0.001,0.01)
nodeNames=['V(p1)','V(m1)']

cont=0
dt=0

t0=time.time()
    

'''waves=Run(nodeNames)
timeVector=waves["t"]

with open("AmpOpData/"+str(round(DC,3))+".json",'w') as fs: json.dump(waves,fs) 

idealInterruptTimes=[timeVector[i] for i in GetInterruptIndexes(waves['V(vin)'])]

perWaveResult={}
for waveName in nodeNames:
    if waveName=='V(vin)': continue
    wave=waves[waveName]
    indexes=interruptPoints=GetInterruptIndexes(wave)
    times=[timeVector[i] for i in indexes]
    difs=[]
    for t_ideal,t_interrupt in zip(idealInterruptTimes,times): difs.append((t_ideal-t_interrupt)*50000*10)
    perWaveResult[waveName]=difs

with open("AmpOpTestResults.json") as fs: OldData=json.load(fs)

OldData[DC]=perWaveResult

with open("AmpOpTestResults.json",'w') as fs: json.dump(OldData,fs)

dt=time.time()-t0
    
percent=round((100*cont)/len(DCs),4)
timeToFinish=dt*(len(DCs)-cont)
print(percent,"% / Time to finish:",format_time(timeToFinish)," DC saved:",DC)
cont+=1
'''
    