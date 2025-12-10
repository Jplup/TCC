import matplotlib.pyplot as plt
import json
import numpy as np
from matplotlib import cm

with open("limiarTest.json") as fs: dataRaw=json.load(fs)

def extract(key, field):
    return key.split(field + "=")[1].split("/")[0]


for suu in ["","_Trig"]:

    plt.figure()
    data = {}  # resultado final: {dc: {X: V}}

    for key, value in dataRaw.items():
        dc     = extract(key, "dc")
        x_val  = extract(key, "X")
        v_real = value[0]["V(compideal)"+suu]

        if dc not in data:
            data[dc] = {}

        data[dc][x_val] = v_real

    X=[]
    Y=[]
    for X_Distance in data.keys():
        X.append(float(X_Distance))
    for Y_Distance in data[list(data.keys())[0]].keys():
        Y.append(float(Y_Distance))

    Z = np.zeros((len(Y),len(X)))

    for ix, x in enumerate(data.keys()):
        for iy, y in enumerate(data[list(data.keys())[0]].keys()):
            Z[iy,ix] = data[(x)][(y)]

    X=np.array(X)
    Y=np.array(Y)

    Xm,Ym=np.meshgrid(X,Y)

    plt.imshow(
        Z,
        origin='lower',
        extent=[min(X), max(X), min(Y), max(Y)],
        aspect='auto'
    )

    plt.colorbar(label="Z")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Heatmap (sem interpolação)"+suu)

plt.show()