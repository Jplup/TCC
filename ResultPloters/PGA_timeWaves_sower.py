import json
import matplotlib.pyplot as plt
import numpy as np
import os

pathPrefix="LTSpiceSimResults/PGA_timeWaves/"

allDirs=os.listdir(pathPrefix)
index=-1

def plot(path):
    print("Path:",path)
    with open(pathPrefix+path) as fs:
        data=json.load(fs)
    plt.figure(figsize=(5,4))
    
    colors=["tab:orange","b"]
    for col,key in enumerate(data.keys()):
        plt.subplot(2,1,col+1)
        time=[val*1000000 for val in data[key]["t"]]
        i0=np.searchsorted(time,100)
        i1=np.searchsorted(time,500)
        wave=data[key]["V(pga)"]
        plt.plot(time[i0:i1],wave[i0:i1],c=colors[col])
        plt.plot([time[i0],time[i1]],[1.65-1.4/2,1.65-1.4/2],'--',c='k',label="Limites inferiores")
        plt.plot([time[i0],time[i1]],[1.65+1.4/2,1.65+1.4/2],'--',c='k')
        #plt.plot([time[i0],time[i1]],[1.65-3.2/2,1.65-3.2/2],'--',c='k',label="Limites superiores")
        #plt.plot([time[i0],time[i1]],[1.65+3.2/2,1.65+3.2/2],'--',c='k')
        plt.ylim(-0.2,3.5)
        plt.yticks([0,1.65,3.3])
        plt.grid("true")
        plt.xlabel("Tempo (us)")
        plt.ylabel("Amplitude (V)")
        plt.title(key)
        plt.legend()
    plt.tight_layout()
    plt.show()

if index<0:
    for directory in allDirs: plot(directory)
else:
    try: plot(allDirs[index])
    except: print("Parametro incorreto")

