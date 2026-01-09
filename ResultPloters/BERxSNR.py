import matplotlib.pyplot as plt
import json
import numpy as np

with open("LTSpiceSimResults/fullN3_3_2.json") as fs: data=json.load(fs)


def getFromDCandNode(dc,nodeIndex):
    if nodeIndex==0:
        print("Não tem BER de corrente de entrada")
    elif nodeIndex==1:
        node="V(tia)_M_Trig"
        snrNode="tia"
    elif nodeIndex==2:
        node="V(filtered)_M_Trig"
        snrNode="filter"
    elif nodeIndex==3:
        node="V(pga)_M_Trig"
        snrNode="filter"
    SNRs=[]
    BERs=[]
    for key in data.keys():
        dcVal=key.split("dc=")[1].split("/")[0]
        if str(dc)==dcVal:
            SNR=data[key][0]["SNR"][snrNode]
            BER=data[key][0][node]
            SNRs.append(float(20*np.log10(SNR)))
            BERs.append(float(BER))
            '''print(data[key])
            print("BER:",BER)
            print("SNR:",SNR)
            input()'''
    
    pares_ordenados=sorted(zip(SNRs,BERs))
    SNRs,BERs=map(list, zip(*pares_ordenados))

    plt.figure()
    plt.plot(SNRs,BERs)
    plt.title("DC = "+str(dc)+" / Node = "+node)

    return SNRs,BERs


fullSNRs=[]
fullBERs=[]
for nodeI in [2]:
    for dc in [0.2,0.5,0.8]:
        SNRs,BERs=getFromDCandNode(dc,nodeI)
        for snr,ber in zip(SNRs,BERs):
            fullSNRs.append(snr)
            fullBERs.append(ber)

pares_ordenados=sorted(zip(fullSNRs,fullBERs))
fullSNRs,fullBERs=map(list, zip(*pares_ordenados))
plt.figure()
plt.plot(fullSNRs,fullBERs)
plt.title("All")
plt.show()
