import matplotlib.pyplot as plt
import numpy as np

lux=[25.34,12.11,10.18,7.07,4.523,2.883]

dx=1.78/6
dy=2.72/6
#dh=(22+142-4)/100
dh=0.22

xs=[0,0,3,2,1]
ys=[0,0,3,2,1]
xs=[0,0,0,0,0]
hs=[0,1,0,0,0]
lxs=[9,19.1,3.7,4.9,7.55]

def calcLux(): pass




for B in list(np.linspace(0,5,10)):
    X=[]

    num=0
    den=0

    for i in range(len(xs)):
        x=xs[i]
        y=ys[i]
        h=hs[i]
        zd=1.8-(h*dh)
        xd=(x*dx)
        yd=(y*dy)
        print("x:",x,"y:",y,"z:",h)
        print("xd:",xd,"yd:",yd,"zd:",zd)
        d=((xd**2)+(yd**2)+(zd**2))**(1/2)
        print("d:",d,"lx:",lxs[i])
        X.append(d)
        num+=lxs[i]/((d+B)**2)
        den+=1/((d+B)**4)

    coef=np.polyfit(X,lxs,2)  # retorna [a, b, c]
    a,b,c=coef

    print("A:",num/den)

    print("a:",a,"b:",b,"c:",c)

    npx=np.linspace(min(X),max(X),100)
    npy=a*npx**2+b*npx+c

    my=((num/den)/(npx**2))

    man=(4.31/((npx-1.1)**2))

    

    plt.figure()
    plt.scatter(X,lxs)
    plt.plot(npx,npy,label="Np")
    plt.plot(npx,my,label="Jp")
    plt.plot(npx,man,label="Man")
    plt.plot()
    plt.legend()
    plt.title("B = "+str(B))


plt.show()