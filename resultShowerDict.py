import matplotlib.pyplot as plt
import numpy as np
import re
from collections import defaultdict
import json
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
import math

# ================================================================
# =============== CARREGAR JSON (FORMATO NOVO) ===================
# ================================================================

with open("resultados.json") as fs:
    data_dict = json.load(fs)

# ================================================================
# === Identificar automaticamente todos os canais existentes =====
# ================================================================

all_channels = set()

for key, sim_list in data_dict.items():
    for sim in sim_list:
        all_channels.update(sim.keys())

all_channels = sorted(list(all_channels))  
channel_to_idx = {ch: i for i, ch in enumerate(all_channels)}
num_channels = len(all_channels)

print("Canais detectados:", all_channels)

# Exemplo:
# ['V(comp_pga)', 'V(comp_real)', 'V(tia)']


# ================================================================
# === Regex para extrair parâmetros das keys =====================
# ================================================================

pattern = r"dc=([0-9.]+).*?sig_amp=([0-9.e\-]+).*?noise_amp=([0-9.e\-]+)"

# data_group[(noise, canal_idx)] = lista de (dc, sig, valor)
data_group = defaultdict(list)


# ================================================================
# === Reorganizar dados no novo formato ==========================
# ================================================================

for key, sim_list in data_dict.items():
    m = re.search(pattern, key)
    if not m:
        continue

    dc = float(m.group(1))
    sig = float(m.group(2))
    noise = float(m.group(3))

    # Média por canal dentro da lista de simulações
    acc = {ch: [] for ch in all_channels}
    for sim in sim_list:
        for ch in all_channels:
            if ch in sim:
                acc[ch].append(sim[ch])

    # Criar média por canal
    chan_mean = {ch: np.mean(acc[ch]) if len(acc[ch]) else None for ch in all_channels}

    # Armazenar por canal
    for ch in all_channels:
        if chan_mean[ch] is not None:
            idx = channel_to_idx[ch]
            data_group[(noise, idx)].append( (dc, sig, chan_mean[ch]) )


# ================================================================
# Valores únicos de noise_amp
# ================================================================

noise_values = sorted({n for (n, _) in data_group.keys()})


# ================================================================
# Plot usando imshow (mantido igual ao seu)
# ================================================================

def PlotConjunto_imshow_irregular(chan_idx, row=1, nrows=1, addTitle=""):
    for i, noise in enumerate(noise_values):
        ax = plt.subplot(nrows, len(noise_values), i+1+((row-1)*len(noise_values)))

        points = data_group[(noise, chan_idx)]
        if not points:
            continue

        dc_vals = sorted(set(p[0] for p in points))
        sig_vals = sorted(set(p[1] for p in points))

        Z = np.zeros((len(sig_vals), len(dc_vals)))
        for dc, sig, val in points:
            Z[sig_vals.index(sig), dc_vals.index(dc)] = val
        
        sig_vals_plot = sorted(set(p[1]*1e6 for p in points))

        im = ax.imshow(Z, origin="lower", aspect="auto",
                       extent=[min(dc_vals), max(dc_vals),
                               min(sig_vals_plot), max(sig_vals_plot)],
                       vmin=0, vmax=1, cmap="plasma_r")

        cmap = plt.get_cmap("plasma_r")
        rgba = cmap(Z)
        rgba[Z == 0] = (0, 1, 0, 1)
        rgba[Z == 1] = (0, 0, 0, 1)
        im.set_data(rgba)

        plt.colorbar(im, ax=ax, label="Valor")
        ax.set_title(f"noise={noise*1e6:.1e} uA / {addTitle}")
        ax.set_xlabel("Duty-Cycle")
        ax.set_ylabel("Sig amplitude (uA)")


def PlotConjunto(chan_idx, row=1, nrows=1, addTitle=""):
    PlotConjunto_imshow_irregular(chan_idx, row, nrows, addTitle)


# ================================================================
# Layout automático
# ================================================================

def auto_grid(n):
    if n <= 2: return (1, n)
    if n <= 4: return (2, 2)
    if n <= 6: return (2, 3)
    if n <= 9: return (3, 3)
    if n <= 12: return (3, 4)
    if n <= 16: return (4, 4)
    r = int(np.ceil(np.sqrt(n)))
    c = int(np.ceil(n / r))
    return (r, c)


# ================================================================
# Plot de linha por noise (adaptado aos novos canais)
# ================================================================

def PlotLinhaPorNoise(idx_list=None):

    if idx_list is None:
        idx_list = list(range(num_channels))

    for noise in noise_values:

        all_dc = sorted({
            p[0]
            for (n, ch) in data_group
            if n == noise
            for p in data_group[(n, ch)]
        })

        n = len(all_dc)
        if n == 0:
            continue

        r, c = auto_grid(n)
        fig, axes = plt.subplots(r, c)
        fig.suptitle(f"noise_amp = {noise*1e6:.1e} uA", fontsize=16)

        axes = np.array(axes).flatten()

        for i, dc_val in enumerate(all_dc):
            ax = axes[i]
            ax.set_title(f"Duty-Cycle = {dc_val:.3g}")
            ax.set_xlabel("Sig amplitude (uA)")
            ax.set_ylabel("Valor")
            ax.set_ylim(0, 1)
            ax.grid(alpha=0.3)

            for chan_idx in idx_list:
                points = data_group.get((noise, chan_idx), [])
                pts = [(p[1], p[2]) for p in points if p[0] == dc_val]

                if not pts:
                    continue

                pts = sorted(pts, key=lambda x: x[0])
                sig = [p[0] * 1e6 for p in pts]
                val = [p[1] for p in pts]

                label = all_channels[chan_idx]

                ax.plot(sig, val,
                        marker="o", linewidth=1.3, markersize=4,
                        label=label)

            ax.legend(fontsize=7)

        for j in range(i+1, len(axes)):
            axes[j].axis("off")


# ================================================================
# ==== PLOTS =====================================================
# ================================================================

plt.figure(constrained_layout=True)
plt.suptitle("Canais detectados (modo Heatmap)")

for idx, ch in enumerate(all_channels):
    PlotConjunto(idx, idx+1, len(all_channels), addTitle=ch)

plt.show()

PlotLinhaPorNoise()
PlotLinhaPorNoise([0])
PlotLinhaPorNoise([1])
PlotLinhaPorNoise([2])
plt.show()
