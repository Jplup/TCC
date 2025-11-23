import json
import numpy as np
import matplotlib.pyplot as plt

'''with open("results.json") as fs: AllData=json.load(fs)

SNRs={}

for key,item in AllData.items():
    params=dict(p.split("=") for p in key.split("/"))
    SNR=params["SNR"]
    try:
        SNRs[SNR][key]=item
    except:
        SNRs[SNR]={key:item}'''


import json
import re
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# -----------------------------------------------------
# Carregar resultados
# -----------------------------------------------------
with open("results.json") as f:
    data = json.load(f)

# -----------------------------------------------------
# Função pra extrair os parâmetros da chave
# -----------------------------------------------------
def parse_key(key):
    params = {}
    for part in key.split('/'):
        if '=' in part:
            k, v = part.split('=', 1)
            try:
                params[k] = float(v)
            except ValueError:
                params[k] = v
    return params

# -----------------------------------------------------
# Organizar dados por noise_amp
# -----------------------------------------------------
groups = defaultdict(list)

for key, ber_list in data.items():
    params = parse_key(key)
    if "X" not in params or "Y" not in params or "noise_amp" not in params:
        continue
    x = params["X"]
    y = params["Y"]
    noise_amp = params["noise_amp"]
    ber_mean = np.mean(ber_list)
    groups[noise_amp].append((x, y, ber_mean))

# -----------------------------------------------------
# Gerar heatmap pra cada noise_amp
# -----------------------------------------------------
for noise_amp, values in sorted(groups.items()):
    xs = sorted(set([v[0] for v in values]))
    ys = sorted(set([v[1] for v in values]))
    
    # Criar matriz Z (BER)
    Z = np.zeros((len(ys), len(xs)))
    for (x, y, ber) in values:
        xi = xs.index(x)
        yi = ys.index(y)
        Z[yi, xi] = ber

    # Plot
    plt.figure(figsize=(6,5))
    plt.imshow(Z, origin='lower', extent=[min(xs), max(xs), min(ys), max(ys)],
               aspect='auto', cmap='plasma')
    plt.colorbar(label='BER')
    plt.title(f'Heatmap - noise_amp = {noise_amp:.2e}')
    plt.xlabel('X position')
    plt.ylabel('Y position')
    plt.tight_layout()
    plt.show()


import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from scipy.interpolate import griddata

# -----------------------------------------------------
# Carregar resultados
# -----------------------------------------------------
with open("results.json") as f:
    data = json.load(f)

# -----------------------------------------------------
# Função pra extrair os parâmetros da chave
# -----------------------------------------------------
def parse_key(key):
    params = {}
    for part in key.split('/'):
        if '=' in part:
            k, v = part.split('=', 1)
            try:
                params[k] = float(v)
            except ValueError:
                params[k] = v
    return params

# -----------------------------------------------------
# Organizar dados por noise_amp
# -----------------------------------------------------
groups = defaultdict(list)

for key, ber_list in data.items():
    params = parse_key(key)
    if "X" not in params or "Y" not in params or "noise_amp" not in params:
        continue
    x = params["X"]
    y = params["Y"]
    noise_amp = params["noise_amp"]
    ber_mean = np.mean(ber_list)
    groups[noise_amp].append((x, y, ber_mean))

# -----------------------------------------------------
# Gerar heatmap interpolado pra cada noise_amp
# -----------------------------------------------------
for noise_amp, values in sorted(groups.items()):
    # Separar os pontos
    xs = np.array([v[0] for v in values])
    ys = np.array([v[1] for v in values])
    zs = np.array([v[2] for v in values])

    # Criar grade regular
    xi = np.linspace(xs.min(), xs.max(), 100)
    yi = np.linspace(ys.min(), ys.max(), 100)
    XI, YI = np.meshgrid(xi, yi)

    # Interpolação dos valores de BER
    ZI = griddata((xs, ys), zs, (XI, YI), method='cubic')

    # Plot
    plt.figure(figsize=(6,5))
    plt.imshow(
        ZI,
        origin='lower',
        extent=[xs.min(), xs.max(), ys.min(), ys.max()],
        aspect='auto',
        cmap='plasma'
    )
    plt.colorbar(label='BER')
    plt.title(f'Interpolated Heatmap - noise_amp = {noise_amp:.2e}')
    plt.xlabel('X position')
    plt.ylabel('Y position')
    plt.tight_layout()
    plt.show()


