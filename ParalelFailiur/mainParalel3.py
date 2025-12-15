from fullProcessModule import Module
import json
import time
import numpy as np
from LTSpiceCleaner import Clean
import os

# Transforma segundos para o formato: x horas y minutos z segundos (ChatGPT)
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"

def GenerateOtherWaves(inputTime,addNoises):
    tss=np.array(inputTime)
    newWaves=[]
    for addNoise in addNoises:
        amp=addNoise
        newWaves.append(np.abs(np.sin(tss*2*np.pi*60)*amp))
    return newWaves

def main():
    # Percebi que se deixar o script rodando por muito tempo alguma coisa para de funcionar, então criei
    #   esse contador que exclui todos os arquivos de dados do LTSpice depois de um certo número de iterações.
    #   Isso concerta o problema
    countToDeletion=0
    dt=1 # Quanto tempo passou entre o começo e o final da última simulação
    cont=0 # Contador de simulações para prever quanto tempo vai demorar para a acabar

    with open("paralel3.json") as fs: paralelData=json.load(fs)

    totalNum=len(paralelData["itemData"]) # Número total de simulações
    print("3: Número total de simulações:",totalNum)

    circuit=paralelData["simData"]["circuit"]
    resultDir=paralelData["simData"]["resultDir"]
    maxSimsBeforeDeletion=paralelData["simData"]["maxSimsBeforeDeletion"]
    nodes=paralelData["simData"]["nodes"]
    trigger=paralelData["simData"]["trigger"]
    ltspiceInputDir=paralelData["simData"]["inputDir"]

    if not os.path.exists(resultDir): 
        with open(resultDir,'w') as fs: json.dump({},fs)


    for item in paralelData["itemData"]:
        VPPMfreq=item["VPPMfreq"]
        numBits=item["numBits"]
        numPointsPerPeriod=item["numPointsPerPeriod"]
        numSamples=item["numSamples"]
        dc=item["dc"]
        X_Distance=item["X_Distance"]
        Y_Distance=item["Y_Distance"]
        lux=item["lux"]
        noiseAmp=item["noiseAmp"]
        addicionalNoisesAmps=item["addNoisesAmps"]
        t0=time.time()
        obj=Module(VPPMfreq,numBits,numPointsPerPeriod,numSamples,dc,X_Distance,Y_Distance,lux,[-1,noiseAmp],1)
        # Antes de ser feita a simulação, o dict de resultados é conferido para ver quantas simulações
        #   com esses parâmetros já foram feitas
        with open(resultDir) as fs: previousData=json.load(fs)
        key=obj.GetDictKey()
        try: num=len(previousData[key])
        except: num=0

        # Print de progresso total
        percent=round((100*cont)/totalNum,4)
        timeToFinish=dt*(totalNum-cont)
        print("3:",percent,"% / Time to finish:",format_time(timeToFinish),"key runnig:",obj.GetDictKey())
        cont+=1

        # Se não foram feitas simulações o suficiente, é feita mais uma simulação
        if num<1:
            # Full process run
            obj.GenerateInput()
            addicionalNoises=GenerateOtherWaves(obj.inputTime,addicionalNoisesAmps)
            simStr,errors,SNR=obj.Run(circuit,nodes,trigger,{},addicionalNoises,ltspiceInputDir)
            errors["SNR"]=SNR
            # Save results
            with open(resultDir) as fs: oldResults=json.load(fs)
            try: oldResults[simStr].append(errors)
            except: oldResults[simStr]=[errors]
            with open(resultDir,'w') as fs: json.dump(oldResults,fs)
            print("3: Erros:",[errors])
            countToDeletion+=1

        print("3: Saved")

        # Deleta os arquivos de info do LTSpice caso o contador chegue no limite
        if countToDeletion>maxSimsBeforeDeletion:
            countToDeletion=0
            Clean()
        dt=time.time()-t0