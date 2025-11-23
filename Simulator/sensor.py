from typing import Dict

from scipy.signal import butter, sosfilt


class Filter:
    #construtor
    def __init__(self, filter_parameters, sample_rate, filter_id):
        self.filter = None
        #recebem os parametros de entrada
        self.filter_id = filter_id
        self.sample_rate = sample_rate
        #chama o método _generate_filter
        self._generate_filter(filter_parameters)

    #método getter para filtrar dados
    def filter_data(self, data):
        #Filtra dados ao longo de uma dimensão usando seções de segunda ordem em cascata
        #Filtra uma sequência de dados, data, usando um filtro IIR digital definido por filter
        return sosfilt(self.filter, data)

    def _generate_filter(self, filter_parameters):
        #recebem as freq de corte baixa e alta e a ordem
        self.low_cut = filter_parameters['low_cut']
        self.high_cut = filter_parameters['high_cut']
        self.order = filter_parameters['order']
        #chama o método _init_filter
        self.__init_filter()

    def __init_filter(self):
        nyq = 0.5 * self.sample_rate
        low = self.low_cut / nyq
        high = self.high_cut / nyq
        #Projeto de filtro analógico e digital Butterworth. Projeta um filtro 
        #Butterworth digital ou analógico de ordem order e retorna os coeficientes do filtro
        self.filter = butter(self.order, [low, high], analog=False,
                             btype='band', output='sos')


class Sensor:
    #construtor
    def __init__(self, position, filter_parameters, sample_rate):
        self.sensor_filters = []
        #para cada filter_id no parametro de entrada filter_parameters
        for filter_id in filter_parameters.keys():
            #Cria-se e adiciona-se um objeto do tipo Filter para esse filter_id
            self.sensor_filters.append(Filter(filter_parameters=filter_parameters[filter_id],
                                              sample_rate=sample_rate,
                                              filter_id=filter_id))
        #recebe a posição do sensor
        self.position: Dict[str, float] = position
