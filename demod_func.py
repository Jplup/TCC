import numpy as np
from getIlus import getIlus
import scipy.signal
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import ltspice
import os


def demod (n_dados,freq_sinal,time_sample):

    points_period=round((1)/(freq_sinal*time_sample));
    length_frame=round(n_dados*points_period);
    star_frame=points_period;
    end_frame=star_frame+n_dados*star_frame;
    data_recep=[];

    l = ltspice.Ltspice(os.path.dirname(__file__) + '\\circuit.raw')
    l.parse()
    V_source = l.getData('V(v_comp)')*0.5;
    V_source=np.array(V_source[star_frame:end_frame]);
    V_source = np.round(V_source);
    vetor3= list(map(int,V_source));

    l_ref = ltspice.Ltspice(os.path.dirname(__file__) + '\\circuit_ref.raw')
    l_ref.parse()
    V_source_ref = l_ref.getData('V(v_comp)')*0.5;
    V_source_ref=np.array(V_source_ref[star_frame:end_frame]);
    V_source_ref= np.round(V_source_ref);
    vetor_ref=list(map(int,V_source_ref));

    demod = [a ^ b for a, b in zip(vetor_ref, vetor3)];

    x=list(itertools.repeat(0,n_dados)); 
    points_period=round(len(vetor3)/len(x))

    for m in x:
     partes = np.array_split(demod, len(x))
    #print(partes)

    
    for n in partes:
     demod2=round(sum(n)/points_period);
     data_recep.append(demod2)

    return(data_recep,vetor3,vetor_ref)


n_dados=10;
freq_sinal=1000;
time_sample=1*1e-6;

data_recep,vetor3,vetor_ref=demod(n_dados,freq_sinal,time_sample)


print(data_recep)

plt.plot(vetor3[:],label='Sinal_recebido')
plt.plot(vetor_ref[:],label='Referencia')
#plt.plot(demod,label='demod')
plt.legend()
plt.grid(axis = 'x')
plt.show()

exit();