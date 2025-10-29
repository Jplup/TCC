import pickle
import json
import math
import numpy as np
import matplotlib.pyplot as plt

from statistics import mean
from numpy.core import std
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict

# ==========================================================================================
# Diretório
path1 = 'data/Salinha/Disc31x31/4lum/NovaModulacao/Amostragem100kHz/FIR/'

# ==========================================================================================
# Nome do arquivo
filename = 'std_20241010_MediaSets_4ptos'

# Apêndices
add_a = '_RNA'
add_b = '_xtest'
add_c = '_ytest'
add_d = '_CDF'              # Salvar dados da simulação

# ==========================================================================================
# Tipos de dados
type_a = '.json'
type_b = '.pickle'

# ==========================================================================================
# Editar as dimensões e a discretização do ambiente (em cm)
xmax = 178
ymax = 272
disc_x = 31
disc_y = 31

# Escolher o número de bins no histograma
Nbins = 50

# ==========================================================================================
# Carrega a Rede Neural Artificial e os conjuntos de teste
with open(path1 + filename + add_a + type_b, 'rb') as f:
    mlpr = pickle.load(f)

with open(path1 + filename + add_b + type_b, 'rb') as f:
    x_test1 = pickle.load(f)

with open(path1 + filename + add_c + type_b, 'rb') as f:
    y_test1 = pickle.load(f)

# ==========================================================================================
#  Estima a posição de cada ponto do conjunto de teste a partir do vetor de iluminâncias 
# de cada ponto
# ==========================================================================================
ymlpr = mlpr.predict(x_test1)

# ==========================================================================================
# Medidas de desempenho da rede: Erro Médio Absoluto e Erro Médio Quadrado
# ==========================================================================================
mae_mlpr = mean_absolute_error(y_test1, ymlpr)
mse_mlpr = mean_squared_error(y_test1, ymlpr)
print("ERRO ABSOLUTO MÉDIO E QUADRÁTICO")
print("Mean Absolute Error: ", round(mae_mlpr,2),"cm")
print("Mean Squared Error: ", round(mse_mlpr,2),"cm")
print('\n')

# ==========================================================================================
#  Coeficiente de determinação R^2, Vetor de distância euclidiana, Erro médio, Desvio-padrão,
# Erro máximo e Erro mínimo.
# ==========================================================================================
r2s_mlpr = r2_score(y_test1, ymlpr)
distance_error = np.subtract(y_test1, ymlpr)
distance_error = [math.sqrt((point[0] ** 2) + (point[1] ** 2)) for point in distance_error]

max_distance_error = max(distance_error)
min_distance_error = min(distance_error)
std_distance_error = std(distance_error)
mean_distance_error = mean(distance_error)
print("MEDIDAS DE DESEMPENHO DA REDE NEURAL")
print("Coeficiente de determinação R2: ", round(r2s_mlpr,4))
print("Erro de distância médio: ", round(mean_distance_error,2),"cm")
print("Desvio-padrão: ", round(std_distance_error,2),"cm")
print("Erro de distância máximo: ", round(max_distance_error,2),"cm")
print("Erro de distância mínimo: ", round(min_distance_error,2),"cm")

# ==========================================================================================
# Mapa de posição
# ==========================================================================================
plt.close('all')
plt.figure(figsize=(8,6))
plt.title('Real position and estimation')

yt1 = [y_test1[n][0] for n in range(len(y_test1))]
yt2 = [y_test1[n][1] for n in range(len(y_test1))]

ym1 = [ymlpr[n][0] for n in range(len(ymlpr))]
ym2 = [ymlpr[n][1] for n in range(len(ymlpr))]

# Plote dos pontos reais e estimados
plt.plot(yt1,yt2, 'ob')
plt.plot(ym1,ym2, 'xr')

#Plote do grid
g1 = range(0,ymax)
g2 = range(0,xmax)
for n in range(0,disc_x):
    a = n*(xmax/(disc_x - 1))*np.ones(ymax)
    plt.plot(a,g1,'-k')
    
for n in range(0,disc_y):    
    b = n*(ymax/(disc_y - 1))*np.ones(xmax)
    plt.plot(g2,b,'-k')

plt.legend(['Real Position','Predicted Position'], bbox_to_anchor = (0.6, -0.15))
plt.xlabel('x (cm)')
plt.ylabel('y (cm)')
plt.show()

# ==========================================================================================
# Histograma do erro e Função de Distribuição Cumulativa (CDF)
# ==========================================================================================
plt.figure(figsize=(8,6))
plt.rcParams.update({'font.size': 18})

counts, b1 = np.histogram(distance_error, bins = Nbins)

b2 = np.zeros(Nbins)
c2 = np.zeros(Nbins)
c3 = np.zeros(Nbins)
for i in range(0,Nbins):
    b2[i] = b1[i+1]                 #Pto final de cada bin
    c2[i] = counts[i]/sum(counts)   #PDF
    c3[i] = sum(c2)                 #CDF
c3 = c3 * 100

plt.title('Position Error')
plt.hist(distance_error, bins = Nbins)
plt.xlabel('Error (cm)')
plt.ylabel('Number of points')
plt.show()

plt.figure(figsize=(8,6))
plt.title('Cumulative Distribution Function')
plt.plot(b2,c3,'-b')
plt.xlabel('Error (cm)')
plt.ylabel('Probability [%]')
plt.show()

# ==========================================================================================
# Salva bins e probabilidades para produzir a CDF
# ==========================================================================================
blist = b2.tolist()
clist = c3.tolist()
CDF : Dict[str, float] = {'Bins': blist, 'Prob': clist, 'DistError': distance_error, 
                          'R2': r2s_mlpr, 'Mean': mean_distance_error, 
                          'Std': std_distance_error, 'Max': max_distance_error, 
                          'Min': min_distance_error 
                          }

with open(path1 + filename + add_d + type_a, 'w') as fa:
    json.dump(CDF, fa)

# ==========================================================================================
# Leitura das porcentagens do histograma/CDF
# ==========================================================================================
# Número de pontos de teste
N_teste = len(distance_error)
# Erros de distância organizados em ordem crescente
distance_error_asc = sorted(distance_error)

# 50%, 70%, 90% e 98% dos pontos de teste (arredondado para cima)
N50 = math.ceil(len(distance_error_asc)*0.5)
N70 = math.ceil(len(distance_error_asc)*0.7)
N90 = math.ceil(len(distance_error_asc)*0.9)
N80 = math.ceil(len(distance_error_asc)*0.80)

# Listas com os 50%, 70%, 90% e 98% pontos de teste com os menores erros
distance_error50 = distance_error_asc[0:N50]
distance_error70 = distance_error_asc[0:N70]
distance_error90 = distance_error_asc[0:N90]
distance_error80 = distance_error_asc[0:N80]

# Maior error de cada lista com os 50%, 70%, 90% e 98% pontos de teste com os menores erros
max50 = max(distance_error50)
max70 = max(distance_error70)
max90 = max(distance_error90)
max80 = max(distance_error80)

print('\n')
print('50% das estimativas de posição possuem erro menor ou igual a', round(max50,2),'cm')
print('70% das estimativas de posição possuem erro menor ou igual a', round(max70,2),'cm')
print('80% das estimativas de posição possuem erro menor ou igual a', round(max80,2),'cm')
print('90% das estimativas de posição possuem erro menor ou igual a', round(max90,2),'cm \n')

#------------------------------------------------------------
## Testar no Terminal para uma porcentagem qualquer desejada
#------------------------------------------------------------
# NX = math.ceil(len(distance_error_asc)*0.6)
# distance_errorX = distance_error_asc[0:NX]
# maxX = max(distance_errorX)
# print('\n X% das estimativas de posição possuem erro menor ou igual a', round(maxX,2),'cm \n')


# ==========================================================================================
# Número de pontos com erro maior que M cm:
# ==========================================================================================
# M = 5.17

# a = 0
# b = range(0,len(distance_error))
# c = [[0,0]]
# for i in b:
#     if distance_error[i] > M:
#         a = a + 1
#         c.append([y_test1[i][0], y_test1[i][1]])
# c.pop(0)
# print("Número de pontos testados:", len(distance_error))
# print("Número de pontos com erro maior que", M, "cm:", a, "pontos")
# print("Pontos com erro maior que", M, "cm:", c)
# ==========================================================================================
