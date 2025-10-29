import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

with open("results.json") as fs: data=json.load(fs)

'''for key,item in data.items():
    print(key,"-> média:",sum(item)/len(item),"/ n itens:",len(item))'''

# Carrega os dados
with open("results.json") as fs:
    data = json.load(fs)

# Listas de valores únicos de sig_amp e noise_amp em ordem crescente
sig_amp_vals = sorted({float(str(key).split("/")[3].split("=")[1].replace("e-", "e-")) for key in data})
noise_amp_vals = sorted({float(str(key).split("/")[4].split("=")[1].replace("e-", "e-")) for key in data})

# Mapear cada valor para um índice
sig_amp_to_idx = {val: idx for idx, val in enumerate(sig_amp_vals)}
noise_amp_to_idx = {val: idx for idx, val in enumerate(noise_amp_vals)}

# Arrays para plot
X_idx, Y_idx, Z = [], [], []

for key, item in data.items():
    sig_amp = float(str(key).split("/")[3].split("=")[1].replace("e-", "e-"))
    noise_amp = float(str(key).split("/")[4].split("=")[1].replace("e-", "e-"))
    z = sum(item)/len(item)

    X_idx.append(sig_amp_to_idx[sig_amp])
    Y_idx.append(noise_amp_to_idx[noise_amp])
    Z.append(z)

X_idx = np.array(X_idx)
Y_idx = np.array(Y_idx)
Z = np.array(Z)

# Criar grade para plot_surface
X_grid, Y_grid = np.meshgrid(range(len(sig_amp_vals)), range(len(noise_amp_vals)))
Z_grid = np.zeros_like(X_grid, dtype=float)

for xi, yi, zi in zip(X_idx, Y_idx, Z):
    Z_grid[yi, xi] = zi  # preencher grid

# Plota superfície
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', edgecolor='k')

# Ajusta ticks para mostrar valores reais
ax.set_xticks(range(len(sig_amp_vals)))
ax.set_xticklabels([f"{v:.0e}" for v in sig_amp_vals])
ax.set_yticks(range(len(noise_amp_vals)))
ax.set_yticklabels([f"{v:.0e}" for v in noise_amp_vals])

ax.set_xlabel('Signal amplitude')
ax.set_ylabel('Noise amplitude')
ax.set_zlabel('Média')
ax.set_title('Superfície 3D dos resultados')

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()
