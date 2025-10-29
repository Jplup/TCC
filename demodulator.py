import matplotlib.pyplot as plt
import numpy as np
import json
from ReadData import vppm_to_bits as Bits
from ReadData import readFile

def GetInterruptPoints(reference):
    interruptIndexes=[]
    for i in range(len(reference)-3):
        last=reference[i+2]
        current=reference[i+3]
        if current==1.65:
            interruptIndexes.append(i)
        if last<1.65 and current>1.65: 
            interruptIndexes.append(i)
    return interruptIndexes

def SampleWithDelay(time,wave,sampleIndexes,delay):
    if delay>1: delay=delay/10
    values=[]
    debugLog=False

    plt.figure()
    plt.scatter(time,filtered)
    plt.scatter([time[i] for i in sampleIndexes],[filtered[i] for i in sampleIndexes])
    dt=0.001
    t=0
    while t<0.012:
        plt.plot([t,t],[0,3.3],c='r')
        t+=dt
    plt.show()
    indexes=[]
    for n in range(len(sampleIndexes)-1):

        currentI=sampleIndexes[n]
        nextI=sampleIndexes[n+1]
        di=nextI-currentI

        currentT=time[currentI]
        nextT=time[nextI]
        targetTime=((nextT-currentT)*delay)+currentT

        if debugLog: print("Current time:",currentT)
        if debugLog: print("Next time:",nextT)
        if debugLog: print("Target time:",targetTime)
        if debugLog: print("Delay:",delay)

        # Binary search
        a=currentI
        b=currentI+int(di*delay)
        c=nextI

        if debugLog: print("Começando busca binária")
        while True:
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])
            if debugLog: print("   Target:",targetTime)
            if time[b]<targetTime:
                if debugLog: print("   if1")
                a=b
            if time[b]==targetTime:
                if debugLog: print("   Achou, brekou")
                break
            if time[b]>targetTime:
                if debugLog: print("   if2")
                c=b
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])

            if (c-a)<2:
                if debugLog: print("   if3")
                if c==a:
                    b=a
                    if debugLog: print("   if4")
                    break
                else:
                    c=a+1
                    if debugLog: print("   if5")
                    break
            b=int(((c-a)/2)+a)
            if debugLog: print("   A =",a,"B =",b,"C =",c)
            if debugLog: print("   At =",time[a],"Bt =",time[b],"Ct =",time[c])
            if debugLog: print("------------------------------------------------")
        
        if debugLog: print("Busca acabou")
        if debugLog: print("Tempo achado:",time[b])
        if debugLog: print("Tempo target:",targetTime)
        if debugLog: print("Erro relativo:",(abs(time[b]-targetTime)/targetTime)*100)
        if debugLog: input()
            
        try:
            values.append(wave[b])
            indexes.append(b)
        except: pass

    plt.figure()
    plt.plot(time,filtered)
    plt.scatter([time[i] for i in indexes],[filtered[i] for i in indexes])
    dt=0.001
    t=0
    while t<0.012:
        plt.plot([t,t],[0,3.3],c='r')
        t+=dt
    
    
    return values
        
def Demodulate(time,filtered,senoidalRef,invertCheck=False):
    # Get interrupt times and indexes
    interruptIndexes=GetInterruptPoints(senoidalRef)
    sampledValues=SampleWithDelay(time,filtered,interruptIndexes,0.1)
    demodulatedData=[]
    for sampledValue in sampledValues:
        if invertCheck:
            if sampledValue>1.65: demodulatedData.append(0)
            else: demodulatedData.append(1)
        else:
            if sampledValue>1.65: demodulatedData.append(1)
            else: demodulatedData.append(0)
    return demodulatedData

def GetOutputWaves():
    pathOutput="outputVoltage.txt"
    outputData=readFile(pathOutput)
    time=outputData['time']
    filtro=outputData["V(v_comp)"]
    ref=outputData["V(v_ref)"]

    return time,filtro,ref

def GetInputInfo(DC,randIndex):
    if randIndex>0:
        if randIndex==1: sufix=""
        else: sufix=str(randIndex)
        pathInput="LTspiceInput/DC0"+str(DC)+"_rand"+sufix+".txt"
    else:
        pathInput="LTspiceInput/DC0"+str(DC)+"_01.txt"
    return readFile(pathInput,True)


time,filtered,reference=GetOutputWaves()
result=Demodulate(time,filtered,reference)

print("Result:",result)

plt.show()