from luminarie import Luminarie
from typing import List, Optional
from wall import Wall
from plane import Plane
from sensor import Sensor


class Ambient:
    def __init__(self, ambient_settings, high_order=False):
        self.high_order = high_order
        #tempo total de simulação
        self.__total_time = None
        #nível do chão
        self.__floor_level = {'z': 0}
        #frequencia de amostragem
        self.__sample_frequency = None
        #tamanho do ambiente
        self.__room_sizes = None
        #Lista de objetos do tipo Luminarie inicia vazia
        self.__lumies: List[Luminarie] = []
        #Objeto opcional do tipo Plane
        self.__plane: Optional[Plane] = None
        #abertura de refletancia
        self.__refletance_aperture = None
        #Lista de objetos do tipo Wall
        self.__walls: List[Wall] = []
        #Objeto opcional do tipo Sensor
        self.__sensor: Optional[Sensor] = None
        #Método de configuração das características do ambiente
        self.__generate_ambient(ambient_settings)

    #Métodos getters para cada atributo da classe
    @property
    def sample_frequency(self):
        return self.__sample_frequency

    @property
    def floor_level(self):
        return self.__floor_level

    @property
    def refletance_aperture(self):
        return self.__refletance_aperture

    @property
    def room_sizes(self):
        return self.__room_sizes

    @property
    def luminaries(self):
        return self.__lumies

    @property
    def floor(self):
        return self.__plane

    @property
    def sensor(self):
        return self.__sensor

    @property
    def walls(self):
        return self.__walls

    @property
    def total_time(self):
        return self.__total_time

    #Método setter configura o ambiente a partir do parametro de entrada ambient_settings
    def __generate_ambient(self, ambient_settings):
        # =============================================================================
        #Tempo total, abertura de refletancia, freq de amostragem e posições das luminarias são recebidos
        self.__total_time = ambient_settings['total_simulation_time']
        aperture = ambient_settings['ambient']['refletance_aperture']
        self.__refletance_aperture = aperture if aperture is not None else self.__refletance_aperture
        self.__sample_frequency = ambient_settings['ambient']['sample_frequency']
        lums_position = ambient_settings['luminaries']['positions']
        # =============================================================================
        #Para cada índice e posição de luminaria lums_position
        for n, pos in enumerate(lums_position):
            #Cria-se um objeto Luminarie
            lumie = Luminarie(ies_file_path=ambient_settings['luminaries']['ies_file_path'],
                              wave_frequency=ambient_settings['luminaries']['modulation_frequencies'][n], position=pos)
            #Adiciona-se à lista de luminarias
            self.__lumies.append(lumie)
        # =============================================================================
        #Recebe os tamanhos do comodo e nível do chão. Cria um objeto do tipo Plane
        num = ambient_settings['ambient']['divisions_number']
        self.__room_sizes = ambient_settings['ambient']['room_sizes']
        constant_axis = {'z': ambient_settings['ambient']['floor_level']}
        self.__floor_level = constant_axis.copy()
        self.__plane = Plane(number_of_divisions=num, sizes=self.room_sizes, constant_axis=constant_axis)
        
        # # =============================================================================
        # # A SER MODIFICADO!!!
        # #Para cada eixo cte no parametro de entrada
        # for const_axis in ambient_settings['ambient']['walls']:
        #     #Cria-se um objeto Plane com esse eixo cte
        #     plane = Plane(number_of_divisions=num, sizes=self.room_sizes, constant_axis=const_axis)
        #     #Cria-se um objeto Wall a partir desse Plane
        #     wall = Wall(plane=plane, luminaire=self.luminaries,
        #                 refletance=ambient_settings['ambient']['walls_refletance'],
        #                 sample_frequency=self.__sample_frequency, total_time=self.total_time)
        #     #Adiciona-se à lista de objetos do tipo Wall
        #     self.__walls.append(wall)
        # =============================================================================

        for w_id, const_axis in enumerate(ambient_settings['ambient']['walls']):
            #Cria-se um objeto Plane com esse eixo cte
            plane = Plane(number_of_divisions=num, sizes=self.room_sizes, constant_axis=const_axis)
            #Cria-se um objeto Wall a partir desse Plane
            wall = Wall(plane=plane, luminaire=self.luminaries,
                        refletance=ambient_settings['ambient']['walls_refletance'],
                        sample_frequency=self.__sample_frequency, total_time=self.total_time,
                        wall_id=str(w_id))
            #Adiciona-se à lista de objetos do tipo Wall
            self.__walls.append(wall)

        # =============================================================================
        if self.high_order:
            for wall in self.__walls:
                other_walls = [w for w in self.__walls if not w == wall]
                wall.calculate_second_order_ilu(other_walls)
        # =============================================================================
        #Cria-se um objeto do tipo Sensor a partir dos parametros de entrada
        self.__sensor = Sensor(position=ambient_settings['sensor']['position'],
                               filter_parameters=ambient_settings['sensor']['filter_parameter'],
                               sample_rate=self.__sample_frequency)
