import matplotlib.pyplot as plt
import numpy as np
import json
import os

files=[file for file in os.listdir() if "temporalResults" in file and not "Params" in file]

for file in files:
    with open(file) as fp: signals=json.load(fp)
    luxResults={}
    lenKey1=len(list(signals.keys()))
    lenKey2=len(list(signals[list(signals.keys())[0]].keys()))
    size=lenKey1*lenKey2
    cont=0
    for key in signals.keys():
        luxResults[key]={}
        for key2 in signals[key].keys():
            dados=signals[key][key2]
            luxResults[key][key2]=max(dados)
            percent=round((100*cont)/size,1)
            print(percent,"%")
            cont+=1
    sufix=file.split("temporal")[1]
    with open("lux"+sufix,'w') as fs: json.dump(luxResults,fs)