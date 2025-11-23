import matplotlib.pyplot as plt
import numpy as np
import json

with open("temporalResults.json") as fp:
    signals=json.load(fp)      #obtem todos os dados do arquivos json (dados no tempo em todos os ptos)

luxResults={}

#print("Signal keys:")
lenKey1=len(list(signals.keys()))
lenKey2=len(list(signals[list(signals.keys())[0]].keys()))
size=lenKey1*lenKey2
cont=0
for key in signals.keys():
    #print("   ",key)
    
    luxResults[key]={}
    for key2 in signals[key].keys():
        #print("       ",key2)
        dados=signals[key][key2]
        luxResults[key][key2]=max(dados)
        percent=round((100*cont)/size,1)
        print(percent,"%")
        cont+=1

        '''plt.title("X:"+key+" / Y:"+key2+" -> "+str(luxResults[key][key2]))
        plt.plot(np.linspace(0,len(dados)/100e5,len(dados)),dados)
        plt.grid("true")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (lx)")
        plt.show()'''

with open("luxResults.json",'w') as fs: json.dump(luxResults,fs)