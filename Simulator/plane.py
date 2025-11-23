# Uma enumeração é um conjunto de nomes simbólicos (membros) vinculados a 
#valores constantes e únicos. Em uma enumeração, os membros podem ser 
#comparados por identidade e a própria enumeração pode ser iterada.
import enum

# Dict declara um tipo Dicionário que espera que todas as suas instancias
#tenham um certo conjunto de chaves onde cada chave é associada com um valor 
#de um tipo consistente
# List declara uma lista de objetos de mesmo tipo
from typing import Dict, List

# Cria uma enumeração com nomes X, Y, Z e valores 'x', 'y', 'z' para os eixos
#do plano
class Axis(enum.Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'

class Plane:
    # Construtor da classe
    def __init__(self, number_of_divisions, sizes, constant_axis, refletance=None):
        #recebe os valores de eixos de um objeto axis da classe Axis criada acima
        self.__axis = [axis.value for axis in Axis]
        # recebe o parametro de entrada constant_axis do tipo dicionario de strings com valores float
        self.__constant_axis: Dict[str, float] = constant_axis
        # recebe o parametro de entrada
        self._number_of_divisions: int = number_of_divisions
         # recebe o parametro de entrada
        self._sizes: Dict[str, float] = sizes
        # chama o método _calculate_plane_points que retorna o mapa discretizado
        self._points: Dict[str, float] = self.__calculate_plane_points()
        # chama o método _calculate_area
        self.__area: float = self.__calculate_area()
        # chama o método _default_luminance
        self.__incident_luminance: Dict = self.__default_luminance()
        # recebe o parâmetro de entrada refletance do tipo float
        self.__refletance: float = refletance

    # Retorna todos os pontos do mapa discretizado
    def __calculate_plane_points(self):
        points = {axis: [] for axis in self.__axis if axis not in self.__constant_axis.keys()}
        for axis in points.keys():
            #se axis for o eixo cte, passar à próxima iteração
            if axis in self.__constant_axis.keys():
                continue
            self.discretization = self._sizes[axis] / self._number_of_divisions
            points[axis] = [k * self.discretization for k in
                            range(self._number_of_divisions + 1)]
        return points

    # Retorna a área do mapa
    def __calculate_area(self):
        area = 1
        for axis in self._sizes.keys():
            size_magnitude = self._sizes[axis]
            if axis in self.__constant_axis.keys():
                continue
            area *= size_magnitude
        return area

    # Retorna a luminancia padrão
    def __default_luminance(self):
        #recebe os eixos livres
        free_axis = [axis for axis in self.__axis if axis not in self.__constant_axis.keys()]
        #recebe os ptos dos eixos livres
        points_per_axis: List[List[float]] = [self._points[axis] for axis in free_axis]
        #matriz de luminancia com valores 0?
        lum = {x: {y: 0 for y in points_per_axis[1]} for x in points_per_axis[0]}
        return lum

    # Função setter que seta a iluminancia incidente no plano
    def set_plane_iluminace(self, plane_iluminance):
        self.__incident_luminance = plane_iluminance

    # Função getter que retorna a iluminancia incidente no plano
    @property
    def plane_iluminance(self):
        return self.__incident_luminance

    # Método getter retorna o mapa discretizado
    @property
    def points(self):
        return self._points

    # Função getter que retorna a área do plano
    @property
    def area(self):
        return self.__area

    # Método getter retorna a área diferencial de um elemento discretizado do plano
    @property
    def diferential_area(self):
        area = 1
        for axis in self._sizes.keys():
            if axis in self.__constant_axis.keys():
                continue
            size = self._sizes[axis] / self._number_of_divisions
            area *= size
        return area

    # Método getter retorna o tamanho do lado em um eixo
    @property
    def sizes(self):
        return self._sizes

    # Função getter que retorna os eixos livres
    @property
    def free_axis(self):
        return [axis.value for axis in Axis if axis.value not in self.__constant_axis.keys()]

    # Função getter que retorna o eixo constante
    @property
    def constant_axis(self):
        return self.__constant_axis

    # Função getter que retorna a luminancia incidente no plano
    @property
    def iluminance(self):
        return self.__incident_luminance

    # Função getter que retorna os pontos do plano discretizado
    @property
    def points(self):
        return self._points
