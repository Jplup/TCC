import matplotlib.pyplot as plt
import numpy as np

# Gera a onda de sinal de corrente com dados VPPM
def VPPMGenerator(freq,inputData,dutyCycle):
    ys=[] # vetor de amplitudes
    T=1/freq # período
    ts=np.linspace(0,T*len(inputData),1000*len(inputData)) # vetor de tempos
    # Para cada valor de tempo:
    for t in ts:
        # De acordo com o tempo, ve qual é o periodo do VPPM (vppmBin) e em qual ponto do período está 
        remainder=t%T
        vppmBin=t//T
        # Vê na lista de dados, qual o dado desse bin
        try: infoBit=inputData[int(vppmBin)]
        except: infoBit=inputData[-1]
        amplitude=1

        # De acordo com o bit desse bin, calcula a amplitude de acordo com a porcentagem do período já 
        #   foi percorrida, considerando o dutyCycle
        if infoBit==0:
            if remainder>T*dutyCycle: ys.append(0)
            else: ys.append(amplitude)
        else:
            if remainder<T*(1-dutyCycle): ys.append(0)
            else: ys.append(amplitude)

    return ts,ys

'''
['size', 'width', 'color', 'tickdir', 'pad', 'labelsize', 'labelcolor', 'labelfontfamily',
 'zorder', 'gridOn', 'tick1On', 'tick2On', 'label1On', 'label2On', 'length', 'direction',
 'left', 'bottom', 'right', 'top', 'labelleft', 'labelbottom', 'labelright', 'labeltop',
 'labelrotation', 'grid_agg_filter', 'grid_alpha', 'grid_animated', 'grid_antialiased', 
 'grid_clip_box', 'grid_clip_on', 'grid_clip_path', 'grid_color', 'grid_dash_capstyle', 
 'grid_dash_joinstyle', 'grid_dashes', 'grid_data', 'grid_drawstyle', 'grid_figure', 
 'grid_fillstyle', 'grid_gapcolor', 'grid_gid', 'grid_in_layout', 'grid_label', 'grid_linestyle', 
 'grid_linewidth', 'grid_marker', 'grid_markeredgecolor', 'grid_markeredgewidth', 
 'grid_markerfacecolor', 'grid_markerfacecoloralt', 'grid_markersize', 'grid_markevery', 
 'grid_mouseover', 'grid_path_effects', 'grid_picker', 'grid_pickradius', 'grid_rasterized', 
 'grid_sketch_params', 'grid_snap', 'grid_solid_capstyle', 'grid_solid_joinstyle', 
 'grid_transform', 'grid_url', 'grid_visible', 'grid_xdata', 'grid_ydata', 'grid_zorder', 
 'grid_aa', 'grid_c', 'grid_ds', 'grid_ls', 'grid_lw', 'grid_mec', 'grid_mew', 'grid_mfc', 
 'grid_mfcalt', 'grid_ms']
'''

bits=[0,1,0,0,1]

ts,ys=VPPMGenerator(50000,bits,0.3)
tss=[t*1000 for t in ts]
firstBit=True
indexesRef=[]
for n in range((len(bits)+1)):
    periodTransition=(n)/50
    plt.plot([periodTransition,periodTransition],[-0.1,1.1],'--',c='k',linewidth=2)
    if n<len(bits):
        c=0.05/50
        dT=1/50
        delays=np.linspace(periodTransition+c,periodTransition+dT-c,10)
        for i,delay in enumerate(delays):
            t=np.searchsorted(tss,delay)
            if t>=len(tss): continue
            if firstBit:
                plt.scatter(tss[t],ys[t],c='r',marker='x')
                lastScatterX=[tss[t],ys[t]]
                indexesRef.append(t)
            else:
                #plt.scatter(tss[t],ys[indexesRef[i]],c='r',marker='x')
                plt.scatter(tss[t],ys[t],c='tab:green')
                lastScatterO=[tss[t],ys[t]]

    firstBit=False
plt.plot(tss,ys)
plt.scatter(lastScatterX[0],lastScatterX[1],c='r',marker='x',label="Amostras de referência")
plt.scatter(lastScatterO[0],lastScatterO[1],c='tab:green',label="Amostras de sinal")
plt.legend()
plt.xlabel("Tempo (us)")
plt.ylabel("Nivel lógico do sinal")
plt.yticks([0,1])
#plt.tick_params(tick1On=False,tick2On=False,label1On=False,label2On=False)
plt.show()