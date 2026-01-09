import matplotlib.pyplot as plt
import numpy as np
import json

nodes=["V(filtered)_M_Trig","V(tia)_M_Trig","V(pga)_M_Trig"]
nodeLabels=["Filtro","TIA","PGA"]

def openNoiseData(n:int) -> dict:
    with open("LTSpiceSimResults/fullN"+str(n)+"_3_2.json") as fs: data=json.load(fs)
    return data

def getValFromKey(val:str,key:str) -> str:
    return key.split(val+"=")[1].split("/")[0]

def GetValuesOfParameter(data:dict,parameterName:str,turnToFloat=False) -> list:
    values=[]
    for key in data.keys():
        strValue=getValFromKey(parameterName,key)
        if turnToFloat: value=float(strValue)
        else: value=strValue
        if not value in values: values.append(value)
    return values

def GetCurvesFromN(n):
    data=openNoiseData(n)

    luxValues=GetValuesOfParameter(data,"lux",True)
    luxValues.sort()

    plt.figure(figsize=(2.5,2.5))
    plt.title("Nível de ruído "+str(n))

    for node,nodeLabel in zip(nodes,nodeLabels):
        valuePairs={node:{"lux":[],"BER":[]}}
        for lux in luxValues:
            soma=0
            count=0
            for key in data.keys():
                luxVal=float(getValFromKey("lux",key))
                if luxVal==lux:
                    soma+=data[key][0][node]
                    count+=1
            soma=soma/count
            valuePairs[node]["lux"].append(lux)
            valuePairs[node]["BER"].append(soma)
        plt.plot(valuePairs[node]["lux"],valuePairs[node]["BER"],label=nodeLabel)
    plt.grid("true")
    plt.xlabel("Iluminância (lx)")
    plt.ylabel("BER")
    plt.xticks([1,4,7,10,13,16,19,22])
    plt.legend()

GetCurvesFromN(1)
GetCurvesFromN(2)
GetCurvesFromN(3)
plt.show()
  