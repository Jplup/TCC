import numpy as np
from getIlus import getIlus
import scipy.signal
import matplotlib.pyplot as plt

def generateSignal(point,time_end,num_points,path):
    luxs=getIlus(point[1],point[0])
    amplitudes=[75*1e-9*lux for key,lux in luxs.items()]
    #frequencies = [8e3, 1e3, 2e3, 4e3]  # Frequências em Hz
    frequencies = [1000] 
    time = np.linspace(0, time_end, num_points)  # Vetor de tempo
    signal = np.zeros_like(time)  # Inicializa o sinal

    
    for amp, freq in zip(amplitudes, frequencies):
        signal+=(amp/2)+((amp / 2) * scipy.signal.square(2 * np.pi * freq * time))
    
    # Escrevendo no arquivo
    with open(path, "w") as f:
        for t, v in zip(time, signal):
            f.write(f"{t:.6e}\t{v:.6e}\n")
    
    print(f"Arquivo '{path}' gerado com sucesso!")
    y = [2, 4, 1, 5, 3]
    return(signal)

# Aqui, o primeiro parâmetro da função define o ponto dentro da sala em x,y nessa ordem
#   a discretização é de 7x7 então tanto x quanto y podem variar de 0 a 6
#generateSignal([0,0], 9.999000e-03, 5400,"testegenerate.txt")



# Dados para o gráfico (eixos X e Y)
x = [1, 2, 3, 4, 5]
y = [2, 4, 1, 5, 3]

# Criação do gráfico
plt.plot(generateSignal([3,4], 10e-03, 1000,"testegenerate_1kt.txt"))  # marker='o' adiciona marcadores nos pontos

# Mostrando o gráfico
plt.show()