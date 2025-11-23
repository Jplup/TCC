import re
import numpy as np
import matplotlib.pyplot as plt
import json

with open("results.json") as fs: data=json.load(fs)

# --- Processamento dos dados ---

dc_groups = {}

for key, values in data.items():
    # Extrair dc usando regex
    match = re.search(r"dc=([0-9.]+)", key)
    if not match:
        continue
    
    dc = float(match.group(1))

    # Converter lista para numpy array para cálculos
    arr = np.array(values)

    if dc not in dc_groups:
        dc_groups[dc] = []

    dc_groups[dc].append(arr)

# Calcular médias por posição
dc_means = {}
for dc, arrays in dc_groups.items():
    stacked = np.vstack(arrays)  # Empilhar listas
    dc_means[dc] = np.mean(stacked, axis=0)  # Média por coluna

# --- Plot ---

dcs = sorted(dc_means.keys())
num_bars = len(dc_means[dcs[0]])  # número de posições dentro das listas

bar_width = 0.15
x_base = np.arange(len(dcs))

plt.figure(figsize=(10, 6))

# Cores automáticas e legendas
legends=["Só filtro","PGA","Saturado"]
for i in range(num_bars):
    y_vals = [dc_means[dc][i] for dc in dcs]
    plt.bar(x_base + i * bar_width, y_vals, width=bar_width, label=legends[i])

plt.xticks(x_base + bar_width * (num_bars - 1) / 2, [str(dc) for dc in dcs])
plt.xlabel("Duty-Cycle")
plt.ylabel("Média de BER")
plt.title("Comparação entre processamentos pós filtragem")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
