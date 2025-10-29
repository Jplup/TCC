import json
import numpy as np
import matplotlib.pyplot as plt

with open("results.json") as fs: data=json.load(fs)

'''
def getStrFromIndex(key,i):
    info=key.split("/")
    return float(info[i].split("=")[1])

newData={}
for key,item in data.items():
    info=key.split("/")
    simStr=""+info[0]
    simStr+="/"+info[1]
    simStr+="/"+info[2]
    simStr+="/"+info[3]
    simStr+="/"+info[4]
    simStr+="/distance="+str(getStrFromIndex(key,5))
    simStr+="/SNR="+str(-getStrFromIndex(key,6))
    newData[simStr]=item

with open("results.json",'w') as fs: json.dump(newData,fs)

print("Resolveu")
input()'''
   

distances={}
for key,item in data.items():
    print("key:",key,"/ intem:",item)
    info=key.split("/")
    distance=float(info[5].split("=")[1])
    snr=float(info[6].split("=")[1])
    print("Distance:",distance,"/ SNR:",snr)
    ber=sum(item)/len(item)
    try:
        distances[str(distance)]["s"].append(snr)
        distances[str(distance)]["b"].append(ber)
    except:
        distances[str(distance)]={}
        distances[str(distance)]["s"]=[snr]
        distances[str(distance)]["b"]=[ber]


print("distances:",distances)
for key,item in distances.items():
    xs=np.array(item["s"])
    ys=np.array(item["b"])
    order=np.argsort(xs)
    x=xs[order]
    y=ys[order]
    plt.plot(x,y,label=key)
plt.xlabel("SNR (dB)")
plt.ylabel("BER")
plt.legend()
plt.grid("true")
plt.show()


