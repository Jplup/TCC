import json
import matplotlib.pyplot as plt
import scipy
import numpy as np
import scipy.signal
from typing import Dict
from numpy.fft import rfft #, rfftfreq


if __name__ == "__main__":
    plt.close('all')
    # Diretório
    path1 = 'data/Salinha/Disc31x31/4lum/NovaModulacao/Amostragem100kHz/FIR/'

    
    # Filtros FIR
    fir1 = "coef_FIR_1kHz"
    fir2 = "coef_FIR_2kHz"
    fir3 = "coef_FIR_4kHz"
    fir4 = "coef_FIR_8kHz"
    path2 = "data/Salinha/Filtros FIR/NovasFrequencias/"
    ext2 = ".mat"
    
    ## Arquivos
    input_file_name =  'DadosTempo_NovaModulacao'
    output_file_name = 'DadosFrequencia_FIR_NovaModulacao'
    
    # Tipo de dados
    type_a = '.json'
    
    # Escolher ponto p entre 0 e ((disc x disc) - 1)
    p = 0
    
    # # ================================================================================
    # # ========================= FREQUÊNCIA DE AMOSTRAGEM =============================
    # # ================================================================================
    Fs_o = 100e3    # frequência de amostragem original
    r = 1           # fator de decimação
    Ts_o = 1/Fs_o   # período de amostragem original
    
    Fs = Fs_o/r     # frequência de amostragem do sinal decimado
    Ts = 1/Fs       # período de amostragem do sinal decimado
    
    M = 500         # ordem dos filtros FIR
    
    # # ================================================================================
    # # ============= OBTENÇÃO DO SINAL DE ILUMINÂNCIA NO TEMPO REAMOSTRADO ============
    # # ================================================================================
    #Abre dados de simulação
    with open(path1 + input_file_name + type_a) as fp:
        signals=json.load(fp)      #obtem todos os dados do arquivos json (dados no tempo em todos os ptos)
    
    sinais = []
    for a in signals.keys():
        for b in signals[a].keys():
            sinais.append(signals[a][b])
    sinais = np.array(sinais)     #matriz com 961 linhas, cada uma contendo o sinal no tempo para cada ponto
    
    # plt.figure()
    # plt.plot(sinais[p])
    # plt.title('Sinal de iluminância original')
    # plt.ylabel("Amplitude (lux)")
    
    medias = np.zeros(len(sinais))
    for i in range(len(sinais)):
        medias[i] = np.mean(sinais[i])
        sinais[i] = sinais[i] - medias[i]
    
    plt.figure()
    plt.plot(sinais[p])
    plt.title('Sinal de iluminância após remover a média')
    plt.ylabel("Amplitude (lux)")
    
    # # ================================================================================
    # # ============================== CÁLCULO DA DFT ==================================
    # # ================================================================================
    N = len(sinais[p])
    t = np.zeros(N)
    freq = np.zeros(N)                # vetor de frequencia da DFT
    for i in range(N):
        t[i] = Ts * i
        freq[i] = (Fs/N) * i
    ## DFT do sinal de iluminancia
    X = rfft(sinais[p])
    mag = 2/N * abs(X)
    plt.figure()
    plt.title('DFT')
    plt.stem(freq[1:int(N/2)],mag[1:int(N/2)])
    
    # # ================================================================================
    # # ============================ FILTRAGEM DOS SINAIS ==============================
    # # ================================================================================
    # Filtros FIR
    fi1 = scipy.io.loadmat(path2+fir1+ext2)     # carrega os dados do arquivo .mat
    f1 = fi1['b_1kHz'][0]                       # coeficientes do filtro (1kHz)
    fi2 = scipy.io.loadmat(path2+fir2+ext2)     # carrega os dados do arquivo .mat
    f2 = fi2['b_2kHz'][0]                       # coeficientes do filtro (2kHz)
    fi3 = scipy.io.loadmat(path2+fir3+ext2)     # carrega os dados do arquivo .mat
    f3 = fi3['b_4kHz'][0]                       # coeficientes do filtro (4kHz)
    fi4 = scipy.io.loadmat(path2+fir4+ext2)     # carrega os dados do arquivo .mat
    f4 = fi4['b_8kHz'][0]                       # coeficientes do filtro (8kHz)
    
    # Sinais filtrados
    y1 = np.zeros((sinais.shape))
    y2 = np.zeros((sinais.shape))
    y3 = np.zeros((sinais.shape))
    y4 = np.zeros((sinais.shape))
    for i in range(len(sinais)):
        y1[i] = scipy.signal.lfilter(f1,1,sinais[i])
        y2[i] = scipy.signal.lfilter(f2,1,sinais[i])
        y3[i] = scipy.signal.lfilter(f3,1,sinais[i])
        y4[i] = scipy.signal.lfilter(f4,1,sinais[i])
    
    plt.figure()
    plt.plot(y1[p])
    plt.title('Componente de 1kHz')
    plt.ylabel("Amplitude (lux)")
    
    plt.figure()
    plt.plot(y2[p])
    plt.title('Componente de 2kHz')
    plt.ylabel("Amplitude (lux)")
    
    plt.figure()
    plt.plot(y3[p])
    plt.title('Componente de 4kHz')
    plt.ylabel("Amplitude (lux)")
    
    plt.figure()
    plt.plot(y4[p])
    plt.title('Componente de 8kHz')
    plt.ylabel("Amplitude (lux)")
    
    # # ================================================================================
    # # ============================== ESTADO ESTACIONÁRIO =============================
    # # ================================================================================    
    # Parte estacionária dos sinais filtrados
    yest1 = np.zeros((len(sinais), N-M))
    yest2 = np.zeros((len(sinais), N-M))
    yest3 = np.zeros((len(sinais), N-M))
    yest4 = np.zeros((len(sinais), N-M))
    
    for i in range(len(sinais)):
        for j in range(N-M):
            yest1[i][j] =  y1[i][500 + j]
            yest2[i][j] =  y2[i][500 + j]
            yest3[i][j] =  y3[i][500 + j]
            yest4[i][j] =  y4[i][500 + j]
    
    # # ================================================================================
    # # ========================= EXTRAÇÃO DE CARACTERÍSTICAS ==========================
    # # ================================================================================ 
    ## Calcula os valores rms dos sinais de saída dos filtros (Features para a RNA)
    y1_rms = np.zeros(len(yest1))
    y2_rms = np.zeros(len(yest2))
    y3_rms = np.zeros(len(yest3))
    y4_rms = np.zeros(len(yest4))
    for i in range(len(yest1)):
        y1_rms[i] = np.sqrt(np.mean(yest1[i]**2))
        y2_rms[i] = np.sqrt(np.mean(yest2[i]**2))
        y3_rms[i] = np.sqrt(np.mean(yest3[i]**2))
        y4_rms[i] = np.sqrt(np.mean(yest4[i]**2))
    # print(y1_rms[0], y2_rms[0], y3_rms[0], y4_rms[0])
    
    y1list = y1_rms.tolist()
    y2list = y2_rms.tolist()
    y3list = y3_rms.tolist()
    y4list = y4_rms.tolist()
    RMS : Dict[str, float] = {
                                    'filter_1': y1list,
                                    'filter_2': y2list, 
                                    'filter_3': y3list, 
                                    'filter_4': y4list
                              }
    #Salva as características
    with open(path1 + output_file_name + type_a, 'w') as f:
        json.dump(RMS, f)
    
    # # ================================================================================
    ## Calcula as amplitudes dos sinais filtrados
    # m1 = np.zeros(len(yest1))
    # m2 = np.zeros(len(yest2))
    # m3 = np.zeros(len(yest3))
    # m4 = np.zeros(len(yest4))
    
    # for i in range(len(yest1)):
    #     m1[i] = (max(yest1[i][:]) - min(yest1[i][:]))/2
    #     m2[i] = (max(yest2[i][:]) - min(yest2[i][:]))/2
    #     m3[i] = (max(yest3[i][:]) - min(yest3[i][:]))/2
    #     m4[i] = (max(yest4[i][:]) - min(yest4[i][:]))/2
    
    # m1list = m1.tolist()
    # m2list = m2.tolist()
    # m3list = m3.tolist()
    # m4list = m4.tolist()
    # Amplitudes : Dict[str, float] = {
    #                                   'filter_1': m1list,
    #                                   'filter_2': m2list, 
    #                                   'filter_3': m3list, 
    #                                   'filter_4': m4list
    #                           }
    
    # =================================================================================
    # ============================== TODOS OS FILTROS =================================
    # =================================================================================
    plt.figure()
    plt.subplot(5,1,1)
    plt.plot(sinais[p])
    plt.title('Sinal de iluminância')
    plt.ylabel("Amplitude (bits)")
    
    plt.subplot(5,1,2)
    plt.plot(yest1[p])
    plt.title('Sinal filtrado a 1kHz')
    plt.ylabel("Amplitude (bits)")
    
    plt.subplot(5,1,3)
    plt.plot(yest2[p])
    plt.title('Sinal filtrado a 2kHz')
    plt.ylabel("Amplitude (bits)")
    
    plt.subplot(5,1,4)
    plt.plot(yest3[p])
    plt.title('Sinal filtrado a 4kHz')
    plt.ylabel("Amplitude (bits)")
    
    plt.subplot(5,1,5)
    plt.plot(yest4[p])
    plt.title('Sinal filtrado a 8kHz')
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude (bits)")
    
    plt.subplots_adjust(hspace=0.6, left=0.06, right=0.97, top=0.95, bottom=0.07)
    plt.show()
    
