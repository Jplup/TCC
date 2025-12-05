import json
import matplotlib.pyplot as plt
import os
import numpy as np

nodeNames=['V(u1)','V(u2)','V(u16)','V(u128)',
            'V(o1)','V(o2)','V(o16)','V(o128)']

'''for file in os.listdir("AmpOpData"):
    with open("AmpOpData/"+file) as fs: data=json.load(fs)
    ts=data["t"]
    for waveName in data.keys():
        if waveName=="t": continue
        ys=data[waveName]
        plt.figure()
        plt.title(file+"/"+waveName)
        plt.plot(ts,ys)
    plt.show()'''

with open("AmpOpTestResults.json") as fs: data=json.load(fs)

# Shows consistant delay during whole wave
if 0:
    for DC in data.keys():
        for wave in data[DC].keys():
            values=data[DC][wave]
            mean=np.mean(values)
            plt.figure()
            plt.title("DC="+DC+" / "+wave)
            plt.plot(range(len(values)),values)
            plt.scatter([0,0],[mean-1,mean+1])
            plt.grid("true")
        plt.show()

# Shows consistant delay for all DCs
if 1:
    resultsPerNode={}
    for DC in data.keys():
        for wave in data[DC].keys():
            values=data[DC][wave]
            mean=np.mean(values)
            try: 
                resultsPerNode[wave]['DC'].append(float(DC))
                resultsPerNode[wave]['Means'].append(mean)
            except:
                resultsPerNode[wave]={'DC':[float(DC)],'Means':[mean]}

    for wave in resultsPerNode.keys():
        plt.figure()
        plt.title(wave)
        xs=resultsPerNode[wave]['DC']
        ys=resultsPerNode[wave]['Means']
        plt.plot(xs,ys)
        plt.grid("true")
        dy=max(ys)-min(ys)
        if dy<2:
            mean=np.mean(ys)
            plt.ylim([mean-1,mean+1])

    plt.figure()
    for wave in resultsPerNode.keys():
        xs=resultsPerNode[wave]['DC']
        ys=resultsPerNode[wave]['Means']
        plt.plot(xs,ys,label=wave)
        plt.grid("true")
    plt.legend()
    plt.show()
'''






TA TUDO ERRADO CARA, CONFERE AS FORMA DE ONDA






'''

resultsPerNode={}
for DC in data.keys():
    for wave in data[DC].keys():
        values=data[DC][wave]
        mean=np.mean(values)
        try: 
            resultsPerNode[wave].append(mean)
        except:
            resultsPerNode[wave]=[mean]

data={}
for wave in resultsPerNode.keys():
    mean=np.mean(resultsPerNode[wave])
    data[wave]=mean

# Extrair as bases numéricas do eixo X
x_values = [1, 2, 16, 128]
x = np.arange(len(x_values))  # posições no gráfico

# Categorizar por tipo
u_values = [data[f"V(u{n})"] for n in x_values]
o_values = [data[f"V(o{n})"] for n in x_values]

# Largura das barras
bar_width = 0.35

plt.figure(figsize=(10, 6))

# Plot das barras (deslocamento para separar)
plt.bar(x - bar_width/2, u_values, width=bar_width, label="Universal", color="blue")
plt.bar(x + bar_width/2, o_values, width=bar_width, label="OPA2350", color="red")

# Eixo X com valores reais
plt.xticks(x, x_values)

plt.xlabel("Valor da Key (1, 2, 16, 128)")
plt.ylabel("Valor do dicionário")
plt.title("Comparação Universal vs OPA2350")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()