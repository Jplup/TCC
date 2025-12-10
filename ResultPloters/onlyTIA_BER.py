import matplotlib.pyplot as plt
import json
import numpy as np

with open("LTSpiceSimResults/result_TIA.json") as fs: data=json.load(fs)

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

def ExtractRoomBER(noiseAmp,dc,node):
    Z = np.zeros((len(yValues),len(xValues)))
    for ix,x in enumerate(xValues):
        for iy,y in enumerate(yValues):
            for key in data.keys():
                xValue=float(key.split("X=")[1].split("/")[0])
                yValue=float(key.split("Y=")[1].split("/")[0])
                DC=key.split("dc=")[1].split("/")[0]
                noise=key.split("noise_amp=")[1].split("/")[0]
                if xValue==x and yValue==y and DC==dc and noise==noiseAmp:
                    Z[iy,ix]=data[key][0][node]
                    break

    X=np.array(xValues)
    Y=np.array(yValues)

    plt.imshow(
        Z,
        origin='lower',
        extent=[min(X), max(X), min(Y), max(Y)],
        aspect='auto',
        vmin=0,
        vmax=1,
        cmap="RdYlGn_r"
    )

    plt.colorbar(label="BER")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")

noiseAmps=GetValuesOfParameter("noise_amp")
dcs=GetValuesOfParameter("dc")

nodes=["V(compideal)","V(compideal)_Trig"]
nodes=["V(compideal)_Trig"]

for noiseAmp in noiseAmps:
    for node in nodes:
        for DC in dcs:
            plt.figure()
            ExtractRoomBER(noiseAmp,DC,node)
            plt.title("Noise: "+noiseAmp+" / DC = "+DC+" / "+node)

def ExtractRoomBER(noiseAmp,dc,node,ax):
    Z = np.zeros((len(yValues),len(xValues)))
    for ix,x in enumerate(xValues):
        for iy,y in enumerate(yValues):
            for key in data.keys():
                xValue=float(key.split("X=")[1].split("/")[0])
                yValue=float(key.split("Y=")[1].split("/")[0])
                DC=key.split("dc=")[1].split("/")[0]
                noise=key.split("noise_amp=")[1].split("/")[0]
                if xValue==x and yValue==y and DC==dc and noise==noiseAmp:
                    Z[iy,ix]=data[key][0][node]
                    break

    X=np.array(xValues)
    Y=np.array(yValues)

    ims=ax.imshow(
        Z,
        origin='lower',
        extent=[min(X), max(X), min(Y), max(Y)],
        aspect='auto',
        vmin=0,
        vmax=1,
        cmap="RdYlGn_r"
    )

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")

    return ims


for noiseAmp in noiseAmps:
    for node in nodes:
        fig,axs=plt.subplots(1,3)
        for iDC,DC in enumerate(dcs):
            ax=axs[iDC]
            ims=ExtractRoomBER(noiseAmp,DC,node,ax)
            clb=fig.colorbar(ims,ax=ax)
            clb.set_label("BER")
            ax.set_title("Duty-Cicle: "+DC)
        plt.tight_layout()
        plt.suptitle("Noise: "+noiseAmp+" / "+node)


amps=GetValuesOfParameter("sig_amp")

nodes=["V(compideal)","V(compideal)_Trig"]
for node in nodes:
    plt.figure()
    for dc in dcs:
        ys=[]
        xs=[]
        for amp in amps:
            for key in data.keys():
                sigamp=key.split("sig_amp=")[1].split("/")[0]
                DC=key.split("dc=")[1].split("/")[0]
                if sigamp==amp and DC==dc:
                    ys.append(data[key][0][node])
                    xs.append(float(sigamp)*10**6)
        pairs=sorted(zip(xs, ys))  
        xs,ys=map(list,zip(*pairs))
        plt.plot(xs,ys,label="DC = "+dc)
    plt.title("BER x Amplitude de "+node)
    plt.xlabel("Amplitude do sinal (uA)")
    plt.ylabel("BER")
    plt.legend()

plt.show()






