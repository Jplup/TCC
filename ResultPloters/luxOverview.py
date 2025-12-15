import matplotlib.pyplot as plt
import numpy as np
import json
from matplotlib import cm

def plot3D(data,title="",zLims=[]):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    X=[]
    Y=[]
    for X_Distance in data.keys():
        X.append(float(X_Distance))
    for Y_Distance in data[list(data.keys())[0]].keys():
        Y.append(float(Y_Distance))

    Z = np.zeros((len(X),len(Y)))

    for ix, x in enumerate(X):
        for iy, y in enumerate(Y):
            Z[iy,ix] = data[str(x)][str(y)]
    
    X=np.array(X)
    Y=np.array(Y)

    Xm,Ym=np.meshgrid(X,Y)

    # Plot the surface.
    surf = ax.plot_surface(Xm, Ym, Z, cmap=cm.viridis,
                        linewidth=0, antialiased=False)

    # Add a color bar which maps values to colors.
    fig.colorbar(surf)
    plt.title(title)
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")

    plt.figure()

    if len(zLims)<1:
        plt.imshow(
            Z,
            origin='lower',
            extent=[min(X), max(X), min(Y), max(Y)],
            aspect='auto'
        )
    else:
        plt.imshow(
            Z,
            origin='lower',
            extent=[min(X), max(X), min(Y), max(Y)],
            aspect='auto',
            vmin=zLims[0],
            vmax=zLims[1]
        )

    plt.colorbar(label="Iluminância (lx)")
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title(title)

def sumResults(sufixes=["VPPM2","VPPM3","60Hz"]):
    with open("Simulator/luxResults.json") as fs: simDataT=json.load(fs)
    for sufix in sufixes:
        with open("Simulator/luxResults"+sufix+".json") as fs: simDataS=json.load(fs)
        for X_Distance in simDataT.keys():
            for Y_Distance in simDataT[list(simDataT.keys())[0]].keys():
                simDataT[X_Distance][Y_Distance]+=simDataS[X_Distance][Y_Distance]
    return simDataT

with open("Simulator/luxResults.json") as fs: simData=json.load(fs)
plot3D(simData)
plt.show()
with open("sunlight.json") as fs: sun=json.load(fs)
for suff in ["","VPPM2","VPPM3","60Hz"]:
    with open("Simulator/luxResults"+suff+".json") as fs: simmi=json.load(fs)
    plot3D(simmi,suff)
plt.show()
lamps=sumResults()

al={}
maxTotal=0
for X_Distance in sun.keys():
    al[X_Distance]={}
    for Y_Distance in sun[list(sun.keys())[0]].keys():
        val=sun[X_Distance][Y_Distance]+lamps[X_Distance][Y_Distance]
        al[X_Distance][Y_Distance]=val
        if val>maxTotal: maxTotal=val
    
print("Max:",maxTotal)
input()
plot3D(lamps)
plot3D(sun,"",[0,1000])
plot3D(al,"",[0,1000])
plt.show()