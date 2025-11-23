import pickle
import json
import math
import numpy as np
import matplotlib.pyplot as plt

from statistics import mean
from numpy.core import std
from sklearn.metrics import r2_score
from typing import Dict

plt.close('all')

# ==========================================================================================
# Diretórios
path1 = 'data/Salinha/Disc31x31/4lum/NovaModulacao/Amostragem100kHz/FIR/'
path2 = 'data/Salinha/DadosExperimentais/'
path3 = path2 + 'NovaModulacao1k2k4k8k/Sets20240930/MediaSets/'

# ==========================================================================================
# Nomes de arquivos
filename_a = 'std_20240930_MediaSets_4ptos'     # RNA treinada #std_20240930_MediaSets_4ptos
filename_b = 'PosicoesSala'         # Posições reais no ambiente
filename_c = 'DadosFreq'            # Dados experimentais de frequência
filename_d = 'Coeficientes'         # Coeficientes de ajuste

# Apêndices
add_a = '_RNA'
add_b = '_xtest'
add_c = '_ytest'
add_d = '_CDFEXP'
add_e = '_FIR'                      # Tipo de filtro ('_FIR', ou '_butter')
add_f = '_4'

# Tipos de dados
type_a = '.json'
type_b = '.pickle'

# ==========================================================================================
# Editar as dimensões e a discretização do ambiente (em cm) para plote do mapa
xmax = 178
ymax = 272
disc_x = 7
disc_y = 7

# Escolher o número de bins no histograma
Nbins = 50

# ==========================================================================================
# Carrega a Rede Neural Artificial e os conjuntos de teste
with open(path1 + filename_a + add_a + type_b, 'rb') as f:
    mlpr = pickle.load(f)

with open(path1 + filename_a + add_b + type_b, 'rb') as f:
    x_test1 = pickle.load(f)

with open(path1 + filename_a + add_c + type_b, 'rb') as f:
    y_test1 = pickle.load(f)

# ==========================================================================================
# Carrega os dados experimentais
with open(path2 + filename_b + type_a, 'r') as fp:
    p = json.load(fp)

with open(path3 + filename_c + add_e + type_a, 'r') as fp:
    ilumi = json.load(fp)

# Carrega os coeficientes de ajuste
with open(path3 + filename_d + add_e + add_f + type_a, 'r') as fp:
    coef = json.load(fp)

# ==========================================================================================
# ================================ DADOS EXPERIMENTAIS =====================================
# ==========================================================================================
# Coeficientes de ajuste
A = np.zeros((4,1))
B = np.zeros((4,1))
for a in coef.keys():
    A = coef['A']
    B = coef['B']


pos_exp =  np.zeros((25,2))
ilu_exp =  np.zeros((25,4))
for j in range(0,5):
    for i in range(0,5):
        pos_exp[5*j+i] = p[j][i]
        ilu_exp[5*j+i] = ilumi[j][i]

il1 =  np.zeros((25,1))
il2 =  np.zeros((25,1))
il3 =  np.zeros((25,1))
il4 =  np.zeros((25,1))

##===================================
## Usar esse para discretização 31x31
for i in range(0,25):
    il1[i] = ilu_exp[i][0]
    il2[i] = ilu_exp[i][1]
    il3[i] = ilu_exp[i][2]
    il4[i] = ilu_exp[i][3]

#====================================

iexp =  np.zeros((25,4))
for i in range(0,25):
    iexp[i][0] = A[0] * il1[i] + B[0]
    iexp[i][1] = A[1] * il2[i] + B[1]
    iexp[i][2] = A[2] * il3[i] + B[2]
    iexp[i][3] = A[3] * il4[i] + B[3]

### Para comparação
# for i in range(0,25):
#     iexp[i][0] = il1[i]
#     iexp[i][1] = il2[i]
#     iexp[i][2] = il3[i]
#     iexp[i][3] = il4[i]

# ==========================================================================================
#  Estima a posição de cada ponto do conjunto de dados experimentais a partir do vetor de 
# iluminâncias de cada ponto
# ==========================================================================================
pos_estimada = mlpr.predict(iexp)

# ==========================================================================================
#  MEDIDAS DE ERRO DOS DADOS EXPERIMENTAIS: Coeficiente de determinação R^2, Vetor de 
# distância euclidiana, Erro médio, Desvio-padrão, Erro máximo e Erro mínimo
# ==========================================================================================
CD = r2_score(pos_exp, pos_estimada)
ED = np.subtract(pos_exp, pos_estimada)
ED = [math.sqrt((point[0] ** 2) + (point[1] ** 2)) for point in ED]

max_ED = max(ED)
min_ED = min(ED)
std_ED = std(ED)
mean_ED = mean(ED)

EDist = np.array(ED)
# Cálculo do MSE e do MAE
mse = np.mean(EDist ** 2)
mae = np.mean(np.abs(EDist))

print("MEDIDAS DE ERRO DOS DADOS EXPERIMENTAIS")
print("Coeficiente de determinação R2: ", round(CD,4))
print("Erro de distância médio: ", round(mean_ED,2),"cm")
print("Desvio-padrão: ", round(std_ED,2),"cm")
print("Erro de distância máximo: ", round(max_ED,2),"cm")
print("Erro de distância mínimo: ", round(min_ED,2),"cm \n")

print(f"Mean Squared Error (MSE): {mse:.4f} cm2")
print(f"Mean Absolute Error (MAE): {mae:.4f} cm \n")


# ==========================================================================================
# ========================== DADOS EXPERIMENTAIS ESCALONADOS ===============================
# ==========================================================================================
# ilu_exp_corr =  np.zeros((25,4))
# for k in range(0,25):
#     ### Usar esse para discretização 31x31
#     ilu_exp_corr[k][0] = iexp[k][0] * 1.0040    #filtro 4.3kHz  (lum D)
#     ilu_exp_corr[k][1] = iexp[k][1] * 1.0256    #filtro 3.2kHz  (lum C)
#     ilu_exp_corr[k][2] = iexp[k][2] * 0.9613    #filtro 1kHz    (lum A)
#     ilu_exp_corr[k][3] = iexp[k][3] * 0.9192    #filtro 2.1kHz  (lum B)
#     ### Usar esse para todas as outras discretizações
#     # ilu_exp_corr[k][0] = iexp[k][0] * 0.959218093
#     # ilu_exp_corr[k][1] = iexp[k][1] * 0.9171292042
#     # ilu_exp_corr[k][2] = iexp[k][2] * 1.02673586185
#     # ilu_exp_corr[k][3] = iexp[k][3] * 1.002415842

# pos_corr = mlpr.predict(ilu_exp_corr)

# ==========================================================================================
#  MEDIDAS DE ERRO DOS DADOS ESCALONADOS: Coeficiente de determinação R^2, Vetor de 
# distância euclidiana, Erro médio, Desvio-padrão, Erro máximo e Erro mínimo
# ==========================================================================================
# CD2 = r2_score(pos_exp, pos_corr)
# ED2 = np.subtract(pos_exp, pos_corr)
# ED2 = [math.sqrt((point[0] ** 2) + (point[1] ** 2)) for point in ED2]

# max_ED2 = max(ED2)
# min_ED2 = min(ED2)
# std_ED2 = std(ED2)
# mean_ED2 = mean(ED2)


# print("MEDIDAS DE ERRO DOS DADOS CORRIGIDOS")
# print("Coeficiente de determinação R2: ", round(CD2,4))
# print("Erro de distância médio: ", round(mean_ED2,2),"cm")
# print("Desvio-padrão: ", round(std_ED2,2),"cm")
# print("Erro de distância máximo: ", round(max_ED2,2),"cm")
# print("Erro de distância mínimo: ", round(min_ED2,2),"cm \n")


# ==========================================================================================
# Mapa de posição dos dados experimentais
# ==========================================================================================
plt.figure(figsize=(8,6))
# plt.subplots_adjust(left=0.237, bottom=0.216, right=0.476, top=0.948)
plt.rcParams.update({'font.size': 22})
plt.title('Map of the environment')

ye1 = [pos_exp[n][0] for n in range(len(pos_exp))]
ye2 = [pos_exp[n][1] for n in range(len(pos_exp))]

yest1 = [pos_estimada[n][0] for n in range(len(pos_estimada))]
yest2 = [pos_estimada[n][1] for n in range(len(pos_estimada))]

plt.plot(ye1,ye2, 'ob', linewidth=2, markersize=12)
plt.plot(yest1,yest2, 'xr', linewidth=2, markersize=12)
plt.axis('equal')


# for i in range(0,len(yest1)):
#     circles = plt.Circle((yest1[i], yest2[i]), 2*std_ED, color='green')
#     fig = plt.gcf()
#     ax = fig.gca()
#     ax.add_patch(circles)


#Plote do mapa
g1 = range(0,ymax)
g2 = range(0,xmax)
for n in range(0,disc_x):
    a = n*(xmax/(disc_x - 1))*np.ones(ymax)
    plt.plot(a,g1,'-k')
    
for n in range(0,disc_y):    
    b = n*(ymax/(disc_y - 1))*np.ones(xmax)
    plt.plot(g2,b,'-k')

plt.axis([0, xmax, -10, ymax+10])
plt.legend(['Real Position','Predicted Position'], bbox_to_anchor = (1.0, 0.8))
plt.xlabel('x [cm]')
plt.ylabel('y [cm]')

plt.tight_layout()
plt.show()



# ==========================================================================================
# Histograma do erro e Função de Distribuição Cumulativa (CDF)
# ==========================================================================================
plt.figure(figsize=(8,6))
plt.rcParams.update({'font.size': 18})

counts, b1 = np.histogram(ED, bins = Nbins)

b2 = np.zeros(Nbins)
c2 = np.zeros(Nbins)
c3 = np.zeros(Nbins)
for i in range(0,Nbins):
    b2[i] = b1[i+1]                 #Pto final de cada bin
    c2[i] = counts[i]/sum(counts)   #PDF
    c3[i] = sum(c2)                 #CDF
c3 = c3 * 100

plt.title('Position Error')
plt.hist(ED, bins = Nbins)
plt.xlabel('Error [cm]')
plt.ylabel('Number of points')
plt.show()

plt.figure(figsize=(8,6))
plt.rcParams.update({'font.size': 22})
plt.title('Cumulative Distribution Function')
plt.plot(b2,c3,'-b')
plt.xlabel('Error [cm]')
plt.ylabel('Probability [%]')
plt.show()


# ==========================================================================================
# Salva bins e probabilidades para produzir a CDF
# ==========================================================================================
blist = b2.tolist()
clist = c3.tolist()
CDF : Dict[str, float] = {'Bins': blist, 'Prob': clist, 'DistError': ED, 
                          'R2': CD, 'Mean': mean_ED, 
                          'Std': std_ED, 'Max': max_ED, 
                          'Min': min_ED
                          }

with open(path1 + filename_a + add_d + add_e + type_a, 'w') as fa:
    json.dump(CDF, fa)

# ==========================================================================================
# Leitura das porcentagens do histograma/CDF
# ==========================================================================================
# Número de pontos de teste
N_teste = len(ED)
# Erros de distância organizados em ordem crescente
distance_error_asc = sorted(ED)

# 50%, 70%, 90% e 98% dos pontos de teste (arredondado para cima)
N50 = math.ceil(len(distance_error_asc)*0.5)
N70 = math.ceil(len(distance_error_asc)*0.7)
N80 = math.ceil(len(distance_error_asc)*0.8)
N90 = math.ceil(len(distance_error_asc)*0.9)

# Listas com os 50%, 70%, 90% e 98% pontos de teste com os menores erros
distance_error50 = distance_error_asc[0:N50]
distance_error70 = distance_error_asc[0:N70]
distance_error80 = distance_error_asc[0:N80]
distance_error90 = distance_error_asc[0:N90]

# Maior error de cada lista com os 50%, 70%, 90% e 98% pontos de teste com os menores erros
max50 = max(distance_error50)
max70 = max(distance_error70)
max80 = max(distance_error80)
max90 = max(distance_error90)

print('\n')
print('50% das estimativas de posição possuem erro menor ou igual a', round(max50,2),'cm')
print('70% das estimativas de posição possuem erro menor ou igual a', round(max70,2),'cm')
print('80% das estimativas de posição possuem erro menor ou igual a', round(max80,2),'cm')
print('90% das estimativas de posição possuem erro menor ou igual a', round(max90,2),'cm \n')

# #------------------------------------------------------------
# ## Testar no Terminal para uma porcentagem qualquer desejada
# #------------------------------------------------------------
# NX = math.ceil(len(distance_error_asc)*0.6)
# distance_errorX = distance_error_asc[0:NX]
# maxX = max(distance_errorX)
# print('\n X% das estimativas de posição possuem erro menor ou igual a', round(maxX,2),'cm \n')


# ==========================================================================================
# Número de pontos com erro maior que M cm:
# ==========================================================================================
# M = 50

# a = 0
# b = range(0,len(ED2))
# c = [[0,0]]
# for i in b:
#     if ED2[i] > M:
#         a = a + 1
#         c.append([pos_exp[i][0], pos_exp[i][1]])
# c.pop(0)
# print("Número de pontos testados:", len(ED2))
# print("Número de pontos com erro maior que", M, "cm:", a, "pontos")
# print("Pontos com erro maior que", M, "cm:", c, "\n")


# ==========================================================================================
# REMOÇÃO DE OUTLIERS (duas vezes o desvio-padrão)
# ==========================================================================================
# p_est1 = np.delete(pos_corr,[4,9,19,20,21,24],0)
# p_real1 = np.delete(pos_exp,[4,9,19,20,21,24],0)

# gp = []
# for i in range(0,len(ED2)):
#     if ED2[i] > mean_ED2 + 2*std_ED2:
#         gp.append(i)
# gp = np.array(gp)

# p_est1 =  np.delete(pos_corr, gp, 0)
# p_real1 = np.delete(pos_exp, gp, 0)

# CDM = r2_score(p_real1, p_est1)
# EDM = np.subtract(p_real1, p_est1)
# EDM = [math.sqrt((point[0] ** 2) + (point[1] ** 2)) for point in EDM]

# max_EDM = max(EDM)
# min_EDM = min(EDM)
# std_EDM = std(EDM)
# mean_EDM = mean(EDM)

# print("MEDIDAS DE ERRO COM OUTLIERS REMOVIDOS")
# print("Número de outliers: ", len(gp))
# print("Coeficiente de determinação R2: ", round(CDM,4))
# print("Erro de distância médio: ", round(mean_EDM,2),"cm")
# print("Desvio-padrão: ", round(std_EDM,2),"cm")
# print("Erro de distância máximo: ", round(max_EDM,2),"cm")
# print("Erro de distância mínimo: ", round(min_EDM,2),"cm \n")

# ==========================================================================================
