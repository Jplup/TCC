from copy import deepcopy

# Este módulo fornece um decorador e funções para adicionar automaticamente métodos
#especiais gerados, como __init__() e __repr__() para classes definidas pelo usuário.
from dataclasses import dataclass

from math import sqrt, acos, degrees, atan2, sin, pi, cos

# Argumento de tipo opcional: Optional[X] é equivalente a X|None (ou Union[X, None]).
from typing import Dict, Optional, List

from numpy import sign

# Importa as classes Luminaries, Plane e Axis
from luminarie import Luminarie
from plane import Plane, Axis


@dataclass
class Wall:
    # Atributos
    __plane: Plane                  #atributo _plane é da classe Plane
    __iluminance_per_point: Dict    #_iluminance_per_point é do tipo Dict

    # Construtor
    def __init__(self, plane: Plane, luminaire: List[Luminarie], refletance: Optional[float] = None,
                 sample_frequency: Optional[int] = None, total_time=None, wall_id: str = None):
        self.__total_time = total_time
        self.__sample_frequency = None if sample_frequency is None else sample_frequency
        self.__ellapsed_time_vector = self.__get_elapsed_time([lum.wave_frequency for lum in luminaire])
        self.__refletance = 0 if refletance is None else refletance
        self.__plane = plane
        self.__wall_index = '' if wall_id is None else wall_id
        #atributo _constant_axis recebe o resultado do método constant_axis do objeto plane
        self.__constant_axis = plane.constant_axis
        self.__iluminance_per_point = self.__set_wall_iluminance(luminaire) if refletance != 0 else None
        self.__high_order_iluminance = deepcopy(self.__iluminance_per_point)

    # getter retorna a refletancia
    @property
    def refletance(self):
        return self.__refletance

    @property
    def wall_index(self):
        return self.__wall_index
    
    # getter retorna o eixo constante
    @property
    def constant_axis(self):
        constant = [axis.value for axis in Axis if axis.value in self.__constant_axis.keys()]
        return constant[0], self.__constant_axis[constant[0]]

    # getter retorna o tempo decorrido
    #insere como parametro de entrada uma lista com as frequencias de onda a partir da lista de luminarias
    def __get_elapsed_time(self, frequencies: List[int]):
        if self.__sample_frequency is None:
            return [0]
        dt = 1 / self.__sample_frequency
        if self.__total_time is None:
            freq = min(frequencies)
            t = 1 / freq
        else:
            t = self.__total_time
        n = round(t / dt)
        time = [k * dt for k in range(n + 1)]
        return time

    # getter retorna, para qqr pto, distancia e angulos de incidencia da luminaria
    def get_angles(self, x: float, y: float, z: float, lumie: Luminarie):
        # dist é a distancia de todos os ptos da luminaria
        dx = lumie.position['x'] - x
        dy = lumie.position['y'] - y
        dz = lumie.position['z'] - z
        dist = (dx ** 2) + (dy ** 2) + (dz ** 2)
        dist = sqrt(dist)

        # t é o ângulo vertical de incidencia theta
        t = degrees(acos(dz / dist))
        t = t if t > 0 or t != 360 else 360 - abs(t)
        # p é o ângulo horizontal de incidencia phi
        p = degrees(atan2(dy, dx))
        p = p if p > 0 else 360 - abs(p)

        # recebe as chaves de um objeto Luminaire, atributo light_distribution, para os angulos horizontais
        p_angles = [key for key in lumie.light_distribution.keys()]
        _, idx_p = min([(abs(p - p_angle), n) for n, p_angle in enumerate(p_angles)], key=lambda a: a[0])
        p = p_angles[idx_p]

        # recebe as chaves de um objeto Luminaire, atributo light_distribution, para os angulos verticais
        t_angles = [key for key in lumie.light_distribution[p].keys()]
        _, idx_t = min([(abs(t - t_angle), n) for n, t_angle in enumerate(t_angles)], key=lambda a: a[0])
        t = t_angles[idx_t]
        
        return p, t, dist

    def _get_angles(self, dx, dy, dz):
        distance = (dx ** 2) + (dy ** 2) + (dz ** 2)
        distance = sqrt(distance)
        theta = degrees(acos(dz / distance))
        theta = theta if theta > 0 or theta != 360 else 360 - abs(theta)
        phi = degrees(atan2(dy, dx))
        phi = phi if phi > 0 else 360 - abs(phi)
        return phi, theta, distance

    # getter retorna o calculo da iluminancia direta
    def __calculate_direct_iluminance(self, lum: Luminarie, x: float, y: float, z: float, time: float):
        w = pi * time * lum.wave_frequency
        # onda quadrada da luz modulada
        factor = 0.5 * sign(sin(2 * w))  # uncomment this to temporal simulation
        # chama a função get_angles
        phi, theta, dist = self.get_angles(x, y, z, lum)
        if phi > lum.max_phi or theta > lum.max_theta:
            return 0
        # recebe a distribuição de luz da luminaria para cada angulo
        ilu = lum.light_distribution[phi][theta]
        scale = self.refletance * self.plane.diferential_area
        e = ilu * scale / (4 * pi * (dist ** 2))
        return e * (1 + factor)

    # Configura e retorna a iluminancia no tempo de uma parede para todo o mapa
    def __set_wall_iluminance(self, luminarie: List[Luminarie]):
        free_axis = self.plane.free_axis
        constant_axis, c = self.constant_axis
        axis_a = free_axis[0]
        axis_b = free_axis[1]
        shift = self.plane.discretization / 2
        
        timed_iluminance_dict = {dt: None for dt in self.__ellapsed_time_vector}
        for dt in timed_iluminance_dict:
            #recebe os ptos do mapa discretizado
            iluminance_dict = {
                a + shift: {b + shift: 0 for b in self.plane.points[axis_b] if b < self.plane.sizes[axis_b]}
                for a in self.plane.points[axis_a] if a < self.plane.sizes[axis_b]}
            #para cada luminaria
            for lum in luminarie:
                for a in iluminance_dict.keys():
                    for b in iluminance_dict[a].keys():
                        #se o eixo cte for X, então Y e Z recebem os ptos discretizados
                        if constant_axis is Axis.X.value:
                            x = c
                            y = a
                            z = b
                        elif constant_axis is Axis.Y.value:
                            x = a
                            y = c
                            z = b
                        elif constant_axis is Axis.Z.value:
                            x = a
                            y = b
                            z = c
                        #armazena a iluminancia direta calculada para o pto (a,b)
                        iluminance_dict[a][b] += self.__calculate_direct_iluminance(lum, x, y, z, dt)
            # armazena os valores de iluminancia para todo o mapa no instante de tempo dt?
            timed_iluminance_dict[dt] = iluminance_dict
        return timed_iluminance_dict

    # ==========================================================================
    def _calculate_second_order_ilu(self, ilu, x, y, z, dt):
        for a in self.wall_iluminace[dt]:
            for b in self.wall_iluminace[dt][a].keys():
                x1, y1, z1 = self._convert_plane_point_to_vector((a, b), self.constant_axis)
                dx = x1 - x
                dy = y1 - y
                dz = z1 - z
                ilu2 = self.__calculate_second_order_ilu(dx, dy, dz, ilu)
                self.__high_order_iluminance[dt][a][b] += ilu2

    def calculate_second_order_ilu(self, other_walls):
        for wall in other_walls:
            for dt in wall.wall_iluminace.keys():
                for a in self.wall_iluminace[dt].keys():
                    for b in self.wall_iluminace[dt][a].keys():
                        i = self.wall_iluminace[dt][a][b]
                        x0, y0, z0 = self._convert_plane_point_to_vector((a, b), wall.constant_axis)
                        self._calculate_second_order_ilu(i, x0, y0, z0, dt)

    def __calculate_second_order_ilu(self, dx, dy, dz, ilu):
        phi, theta, distance = self._get_angles(dx, dy, dz)
        scale = self.refletance * self.plane.diferential_area
        a = cos(dz / distance)
        e = (ilu * scale * a) / (4 * pi * (distance ** 2))
        return e

    def _convert_plane_point_to_vector(self, point: tuple, const_axis):
        constant_axis, c = const_axis
        a, b = point
        if constant_axis is Axis.X.value:
            x = c
            y = a
            z = b
        elif constant_axis is Axis.Y.value:
            x = a
            y = c
            z = b
        elif constant_axis is Axis.Z.value:
            x = a
            y = b
            z = c
        return x, y, z
    # ==========================================================================

    # getter retorna o plano discretizado
    @property
    def plane(self):
        return self.__plane

    # getter retorna a iluminancia por ponto da parede
    @property
    def wall_iluminace(self):
        return self.__iluminance_per_point

    # ==========================================================================
    def get_wall_iluminance(self, high_order=False):
        if not high_order:
            return self.wall_iluminace
        else:
            return self.__high_order_iluminance

    def __eq__(self, other: "Wall"):
        return self.wall_index == other.wall_index
    # ==========================================================================

    # #compara se a iluminancia por pto de duas paredes é a mesma?
    # def __eq__(self, other: "Wall"):
    #     for dt in self.wall_iluminace.keys():
    #         for x in self.wall_iluminace[dt].keys():
    #             for y in self.wall_iluminace[dt][x].keys():
    #                 a = self.wall_iluminace[dt][x][y]
    #                 b = other.wall_iluminace[dt][x][y]
    #                 if a != b:
    #                     return False
    #     return True
