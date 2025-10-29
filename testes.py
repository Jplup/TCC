import matplotlib.pyplot as plt
import random
import numpy as np

def getRandom():
    rng = np.random.default_rng()
    numbers = rng.normal(loc=0.0, scale=1.0, size=1) 
    n1=random.randint(0,100)/100
    n2=random.randint(0,100)/100
    return max(min(float((numbers+1)/2),1),0)

nBins=10
nTimes=1000
db=1/nBins
bins={}
b=0
for _ in range(nBins):
    bins[str(round(b*nBins)/nBins)]=0
    b+=db
#print("Bins:",bins)
for i in range(nTimes):
    n=getRandom()
    bin=(n//(1/nBins))/nBins
    #print("n:",n,"bin:",bin)
    bins[str(bin)]+=1
    print(i)
xs=[]
ys=[]
for k,v in bins.items():
    xs.append(float(k))
    ys.append(v)

plt.plot(xs,ys)
plt.show()


# Roda o circuito
'''
ltspice_path=r"C:\Users\João Pedro\AppData\Local\Programs\ADI\LTspice\LTspice.exe"
netlist_path=r"C:\Users\João Pedro\Desktop\Modulador\circuit.net"
subprocess.run([ltspice_path,"-b",netlist_path],check=True)

# Lê o arquivo .raw gerado e pega o sinal do comparador
l=ltspice.Ltspice(os.path.join(os.getcwd(),"circuit.raw"))
l.parse()

# 4. pega dados
t=l.get_time()
vout=l.getData('V(v_tia)')

plt.plot(time,[(a/amplitude)*3.3 for a in amp],label="Dados")
plt.plot(t,[a-3.3 for a in vout],label="Comp")
plt.grid("true")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (A)")
plt.legend()
plt.show()'''