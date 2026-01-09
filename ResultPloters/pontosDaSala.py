import matplotlib.pyplot as plt
import numpy as np
import os

pathPrefix="LTSpiceSimResults/PGA_timeWaves/"
allDirs=os.listdir(pathPrefix)
indexes=[
    (1,1),
    (7,7),
    (13,13)
]

xTicks=[0]
yTicks=[0]

xTicks=[]
yTicks=[]

for path,index in zip(allDirs,indexes):
    X=path.split("_")[0].split("-")[1]
    Y=path.split("_")[1].split("-")[1].split(".json")[0]
    plt.scatter(float(X),float(Y),label=str(index))
    print("X:",X,"Y:",Y)
    xTicks.append(round(float(X),2))
    yTicks.append(round(float(Y),2))

dimentions=[4,5]
'''xTicks.append(4)
yTicks.append(5)'''


plt.plot([0,0,dimentions[0],dimentions[0],0],[0,dimentions[1],dimentions[1],0,0],c='k')
plt.axis("equal")
#plt.legend()
plt.xticks(xTicks)
plt.yticks(yTicks)
plt.grid("true")
plt.show()