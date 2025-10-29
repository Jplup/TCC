import json
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neural_network import MLPRegressor
from copy import deepcopy

# ==========================================================================================
# Média e std para a refletância usada
mean_refl = 0.0
std_refl  = 0.05

# ==========================================================================================
# Diretórios
dir_a = 'data/'
dir_b = 'Salinha/'
dir_c = 'Disc31x31/'
dir_d = '4lum/'
dir_e = 'NovaModulacao/'
dir_f = 'Amostragem100kHz/FIR/'

# ==========================================================================================
# Nomes de arquivos
filename_a = 'DadosFrequencia_FIR_NovaModulacao'      # Carregar dados de simulação na frequência
filename_b = 'DadosTempo_NovaModulacao'           # Carregar dados de simulação no tempo
filename_c = 'std45'                # Salvar dados da simulação

# Apêndices
add_a = '_RNA'
add_b = '_xtest'
add_c = '_ytest'

# ==========================================================================================
# Tipos de dados
type_a = '.json'
type_b = '.pickle'

# ==========================================================================================
# Carrega "freq.json", com os valores de saída de cada um dos filtros
with open(dir_a + dir_b + dir_c + dir_d + dir_e + dir_f + filename_a + type_a, 'r') as fp:
    data = json.load(fp)

# Carrega "temp.json", com os ptos do plano e a iluminancia no tempo em cada um deles
with open(dir_a + dir_b + dir_c + dir_d + dir_e + dir_f + filename_b + type_a, 'r') as fp:
    plane = json.load(fp)

# ==========================================================================================
## Organiza os dados de "data" em uma matriz com uma coluna para cada filtro e uma linha
# para cada ponto
matrix_data = []
for f_id in data.keys():
    matrix_data.append(data[f_id])
matrix_data = np.array(matrix_data)
matrix_data = matrix_data.T

# ==========================================================================================
# Pontos no plano em centímetros. Localização esperada.
expected_output = [[100 * float(x), 100 * float(y)] for x in plane.keys() 
                   for y in plane[x].keys()]
saida = deepcopy(expected_output)

# ==========================================================================================
# Adiciona valores aleatórios para a matriz de iluminancia 
dados = list(deepcopy(matrix_data))
for x in range(1,5):
    sorteio = np.random.normal(mean_refl, std_refl, size=matrix_data.shape)
    new_matrix_data = matrix_data + sorteio*matrix_data
    dados.extend(list(new_matrix_data))
    saida.extend(expected_output)
dados = np.array(dados)

# ==========================================================================================
# Divide vetores ou matrizes em subconjuntos aleatórios de treinamento e teste.
x_train1, x_test1, y_train1, y_test1 = train_test_split(dados, saida, 
                                                        train_size=0.85, test_size=0.15,
                                                        random_state=0)

# ==========================================================================================
#  Regressão de vários alvos.
#  Essa estratégia consiste em ajustar um regressor por alvo. Essa é uma estratégia simples
# para estender regressores que não suportam nativamente a regressão de vários alvos.
# ==========================================================================================
mlpr = MultiOutputRegressor(MLPRegressor(max_iter=100000, batch_size='auto', 
                                         activation='relu', early_stopping=True, 
                                         hidden_layer_sizes=[2700,1800], learning_rate='adaptive',
                                         n_iter_no_change=12, solver='adam', 
                                         validation_fraction=0.12, learning_rate_init=0.001))

# Ajusta o modelo aos dados de treinamento, separadamente para cada variável de saída.
mlpr.fit(x_train1, y_train1)

# ==========================================================================================
# Salva a Rede Neural Artificial e os conjuntos de teste

with open(dir_a + dir_b + dir_c + dir_d + dir_e + dir_f + filename_c + add_a + type_b, 'wb') as fx:
    pickle.dump(mlpr, fx, pickle.HIGHEST_PROTOCOL)

with open(dir_a + dir_b + dir_c + dir_d + dir_e + dir_f + filename_c + add_b + type_b, 'wb') as fx:
    pickle.dump(x_test1, fx, pickle.HIGHEST_PROTOCOL)

with open(dir_a + dir_b + dir_c + dir_d + dir_e + dir_f + filename_c + add_c + type_b, 'wb') as fx:
    pickle.dump(y_test1, fx, pickle.HIGHEST_PROTOCOL)

# ==========================================================================================
