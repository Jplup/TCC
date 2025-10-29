import json

def getIlus(indexI,indexJ):
    pathPrefix="salaDiscretizada/"
    paths=["id","ie","sd","se"]
    pathPosfix=".json"
    values={}
    for path in paths:
        with open(pathPrefix+path+pathPosfix) as fs:
            values[path]=json.load(fs) 
    
    ilus={}
    for dicKey in values.keys():
        dic=values[dicKey]
        xssim=dic[list(dic.keys())[indexI]]
        val=xssim[list(xssim.keys())[indexJ]]
        ilus[dicKey]=(val[0])

    return ilus
    



'''import numpy as np
import matplotlib.pyplot as plt
import json

pathPrefix="salaDiscretizada/"
paths=["id","ie","sd","se"]
pathPosfix=".json"
values={}
for path in paths:
    with open(pathPrefix+path+pathPosfix) as fs:
        values[path]=json.load(fs) 

xs=[]
ys=[]
for x in values["id"].keys(): xs.append(float(x))
for y in values["id"][list(values["id"].keys())[0]].keys(): ys.append(float(y))
xs=np.array(xs)
ys=np.array(ys)

X,Y=np.meshgrid(xs,ys)
Esum=np.zeros_like(X)
Emat=np.zeros_like(X)
dif=np.zeros_like(X)

for i in range(len(xs)):
    for j in range(len(ys)):
        soma=0
        for dicKey in values.keys():
            dic=values[dicKey]
            xssim=dic[list(dic.keys())[i]]
            val=xssim[list(xssim.keys())[j]]
            soma+=val[0]
        Esum[j,i]=soma

path='4lum_DadosEstatico.json'
with open(path) as fs: dic=json.load(fs) 

xs=[]
ys=[]
for x in dic.keys(): xs.append(float(x))
for y in dic[list(dic.keys())[0]].keys(): ys.append(float(y))
xs=np.array(xs)
ys=np.array(ys)

Emat=np.zeros_like(X)
Edif=np.zeros_like(X)

for i in range(len(xs)):
    for j in range(len(ys)):
        xssim=dic[list(dic.keys())[i]]
        val=xssim[list(xssim.keys())[j]]
        Emat[j,i]=val[0]
        Edif=100*abs(Emat-Esum)/Emat
    
Eplot=Edif


planoTrabalho=1.84
# Posições das luminárias (nos 4 cantos da sala, 15 cm afastadas das paredes)
luminarias = np.array([
    [0.25,0.36,planoTrabalho],
    [1.51,2.37,planoTrabalho],
    [1.52,0.36,planoTrabalho],
    [0.26,2.31,planoTrabalho]
])

# Plotando o mapa de iluminância
plt.contourf(X, Y, Eplot, levels=100, cmap='viridis')
plt.colorbar(label='Iluminância Total (lux)')
plt.scatter(X,Y,c='k')
plt.scatter(luminarias[:, 0], luminarias[:, 1], c='red', marker='o', label='Luminárias')
plt.xlabel('X (m)')
plt.ylabel('Y (m)')
plt.title('Distribuição da Iluminância Total no Ambiente')
plt.legend()
plt.axis('equal')
plt.show()'''