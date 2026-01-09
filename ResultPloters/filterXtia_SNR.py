import matplotlib.pyplot as plt
import json
import numpy as np

with open("LTSpiceSimResults/fullN3_3000.json") as fs: data=json.load(fs)

usePredetermiedValues=True
# Values for N1
boundsValues=[[-8,48],[-22,20],[0,8]]
# Values for N2
boundsValues=[[-60,17],[-60,14],[6,14]]
# Values for N3
boundsValues=[[-115,-40],[-115,-40],[0.5,13]]

def GetValuesOfParameter(parameterName,turnToFloat=False):
    values=[]
    for key in data.keys():
        strValue=key.split(parameterName+"=")[1].split("/")[0]
        if turnToFloat: value=float(strValue)
        else: value=strValue
        if not value in values: values.append(value)
    return values

xValues=GetValuesOfParameter("X",True)
yValues=GetValuesOfParameter("Y",True)

# {"n_samples=10/dc=0.2/n_bits=1000/sig_amp=1.3e-06/noise_amp=0.0/lux=17.29/X=0.0/Y=0.0": 
#       [{"V(compideal)": 0.508, "V(compideal)_Trig": 0.0}],

def ExtractRoomSNR(noiseAmp,dc,ax,node,levels,use_dB=True):
    Z = np.zeros((len(yValues),len(xValues)))
    maxVal=-500
    minVal=100
    meanVal=0
    auxCount=0
    for ix,x in enumerate(xValues):
        for iy,y in enumerate(yValues):
            for key in data.keys():
                xValue=float(key.split("X=")[1].split("/")[0])
                yValue=float(key.split("Y=")[1].split("/")[0])
                DC=key.split("dc=")[1].split("/")[0]
                noise=key.split("noise_amp=")[1].split("/")[0]
                if xValue==x and yValue==y and DC==dc and noise==noiseAmp:
                    potencies=data[key][0]["Pot"]
                    if node=="input":
                        SNR=potencies["current_ideal"]/potencies["current_noise"]
                    elif node=="tia":
                        SNR=potencies["voltage_ideal"]/potencies["V(tia)_noise"]
                    elif node=="filter":
                        SNR=potencies["voltage_ideal_0"]/potencies["V(filtered)_noise"]
                    else:
                        print("---------------Mandou node errada------------------")
                        return
                    if use_dB: 
                        Z[iy,ix]=20*np.log10(SNR)
                    else:
                        Z[iy,ix]=SNR
                    if maxVal<20*np.log10(SNR): maxVal=20*np.log10(SNR)
                    if minVal>20*np.log10(SNR): minVal=20*np.log10(SNR)
                    meanVal+=20*np.log10(SNR)
                    auxCount+=1
                    break
    
    print("DC:",dc,"Node:",node)
    print("   max:",maxVal)
    print("   min:",minVal)
    print("   maen:",meanVal/auxCount)

    '''X=np.array(xValues)
    Y=np.array(yValues)

    plt.imshow(
        Z,
        origin='lower',
        extent=[min(X), max(X), min(Y), max(Y)],
        aspect='auto',
        cmap="plasma_r"
    )

    plt.colorbar(label="SNR")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")'''
    X=np.array(xValues)
    Y=np.array(yValues)

    if usePredetermiedValues:
        ims=ax.imshow(
            Z,
            origin='lower',
            extent=[min(X), max(X), min(Y), max(Y)],
            aspect='auto',
            cmap="plasma_r",
            vmin=levels[0],
            vmax=levels[1]
        )
    else:
        ims=ax.imshow(
        Z,
        origin='lower',
        extent=[min(X), max(X), min(Y), max(Y)],
        aspect='auto',
        cmap="plasma_r"
        )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")

    return ims

noiseAmps=GetValuesOfParameter("noise_amp")
dcs=GetValuesOfParameter("dc")

'''for noiseAmp in noiseAmps:
    for node in nodes:
        for DC in dcs:
            plt.figure()
            ExtractRoomBER(noiseAmp,DC,node)
            plt.title("Noise: "+noiseAmp+" / DC = "+DC+" / "+node)'''

for levels,node in zip(boundsValues,["input","tia","filter"]):
    for noiseAmp in noiseAmps:
        fig,axs=plt.subplots(1,3,figsize=(20,3.8))
        for iDC,DC in enumerate(dcs):
            ax=axs[iDC]
            ims=ExtractRoomSNR(noiseAmp,DC,ax,node,levels)
            clb=fig.colorbar(ims,ax=ax)
            clb.set_label("SNR")
            ax.set_title("Duty-Cicle: "+DC)
        #plt.tight_layout()
        plt.suptitle("Noise: "+noiseAmp+" / node ="+node)


amps=GetValuesOfParameter("sig_amp")

'''plt.figure()
for dc in dcs:
    ys=[]
    xs=[]
    for amp in amps:
        for key in data.keys():
            sigamp=key.split("sig_amp=")[1].split("/")[0]
            DC=key.split("dc=")[1].split("/")[0]
            if sigamp==amp and DC==dc:
                ys.append(data[key][0]["SNR"])
                xs.append(float(sigamp)*10**6)
    pairs=sorted(zip(xs, ys))  
    xs,ys=map(list,zip(*pairs))
    plt.plot(xs,ys,label="DC = "+dc)
plt.title("SNR x Amplitude de ")
plt.xlabel("Amplitude do sinal (uA)")
plt.ylabel("SNR")
plt.legend()

plt.show()
'''
plt.show()




