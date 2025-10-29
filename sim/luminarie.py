from dataclasses import dataclass
from typing import Dict
import enum

# Classe Keys enumera chaves das luminarias
class Keys(enum.Enum):
    IESNA = 'iesna'
    TEST = 'test'
    DATE = 'date'
    MANUFAC = 'manufac'
    LUMCAT = 'lumcat'
    LUMINAIRE = 'luminaire'
    LAMPCAT = 'lampcat'
    LAMP = 'lamp'
    BALLASTCAT = 'ballastcat'
    BALLAST = 'ballast'
    TILT = 'tilt'
    INITIAL = 'initial_rated_lumens'
    SCALE_FACTOR = 'scale_factor'
    NUM_VERTICAL = 'num_vertical'
    NUM_HORIZONTAL = 'num_horizontal'
    UNIT_TYPE = 'unit_type'
    LUMINOUS_OPENING = 'luminous_opening'
    VERTICAL_ANGLES_SET = 'vertical_angles_set'
    HORIZONTAL_ANGLES_SET = 'horizontal_angles_set'
    CANDELA_VALUES_SET = 'candela_values_set'


@dataclass
#Constroi o objeto Luminaire a partir dos parametros de entrada e do arquivo .ies
class Luminarie:
    #Definição dos tipos de dados dos atributos da classe
    position: Dict[str, float]
    light_distribution: Dict
    wave_frequency: int
    __ies_file_dict: Dict
    max_phi: int
    max_theta: int

    # Construtor
    def __init__(self, ies_file_path=None, wave_frequency: int = None, position=None, lums=None, potency_factor=1):
        #recebe o parametro de entrada
        self.potency_factor = potency_factor
        #chama o método "load_ies_file_into_dict" se lums for nulo
        self.__ies_file_dict = self.load_ies_file_into_dict(ies_file_path) if lums is None else None
        #distribuição de iluminancia a partir do arquivo .ies
        self.light_distribution = self.__ies_file_dict[Keys.CANDELA_VALUES_SET.value] if lums is None else lums
        #recebem os parametros de entrada
        self.wave_frequency = wave_frequency
        self.position = position
        #valores máximos da distribuição de iluminancia
        self.max_phi = max(list(self.light_distribution.keys()))
        self.max_theta = max(list(self.light_distribution[self.max_phi].keys()))

    #parametro de entrada é o caminho do arquivo .ies
    def load_ies_file_into_dict(self, ies_file_path):
        #abre o arquivo ies como f. Fecha ao sair desse bloco.
        with open(ies_file_path, 'r+') as f:
            f.seek(0)
            ies_file_lines = f.readlines()

        ies_dict = {}
        splited_info = []
        checked_lines = 0
        for line in ies_file_lines:
            for key in Keys:
                if key.value in line.lower():
                    raw_info = line.split('\n')
                    raw_info = raw_info[0]
                    if '\t' in line or ' ' in line:
                        splited_info = raw_info.split('\t') if '\t' in line else raw_info.split(' ')
                    elif '=' in line:
                        splited_info = raw_info.split('=')
                    elif ':' in line:
                        splited_info = raw_info.split(':')

                    line_info = splited_info[-1]
                    #armazena os dados do arquivo ies
                    ies_dict[key.value] = line_info
                    #numero de linhas que foram checadas
                    checked_lines += 1
                    break
                else:
                    continue

        #valores já configurados recebe conjunto vazio
        already_set_values = set()
        #armazena as linhas restantes
        remaining_lines = ies_file_lines[checked_lines:]
        for n, line in enumerate(remaining_lines):
            if n == 0:
                checked_lines += 1
                continue
            if n == 5:
                checked_lines += 1
                continue
            if n == 8:
                checked_lines += 1
                break
            if line in already_set_values:
                continue
            #chaves de interesse no arquivo
            keys_slice = (Keys.INITIAL, Keys.SCALE_FACTOR, Keys.NUM_VERTICAL,
                          Keys.NUM_HORIZONTAL, Keys.UNIT_TYPE, Keys.LUMINOUS_OPENING)
            for key in keys_slice:
                if key.value in ies_dict.keys():
                    continue
                if line in already_set_values:
                    continue
                split_line = line.split('\n')
                split_line = split_line[0]
                if ' ' in split_line:
                    value_list = []
                    split_line = line.split(' ')
                    for l in split_line:
                        value_list.append(float(l))
                    #armazena os dados do arquivo ies
                    ies_dict[key.value] = value_list
                else:
                    #armazena os dados do arquivo ies
                    ies_dict[key.value] = float(split_line)
                already_set_values.add(line)
                #numero de linhas que foram checadas
                checked_lines += 1

        #chaves de interesse no arquivo
        keys_slice = (Keys.VERTICAL_ANGLES_SET, Keys.HORIZONTAL_ANGLES_SET)
        for key in keys_slice:
            key_name = key.value
            key_name = key_name.split('_angles_set')
            key_name = 'num_' + key_name[0]
            ies_dict[key.value] = []
            while len(ies_dict[key.value]) < ies_dict[key_name]:
                for n, line in enumerate(ies_file_lines[checked_lines:]):
                    split_line = line.split('\n')
                    split_line = split_line[0]
                    split_line = split_line.split(' ')
                    value_list = [float(v) for v in split_line if v.isnumeric()]
                    if len(value_list) == 0:
                        break
                    if n == 0 and value_list[0] != 0:
                        continue
                    if len(ies_dict[key.value]) == ies_dict[key_name]:
                        break
                    #armazena os dados do arquivo ies
                    ies_dict[key.value] += value_list
                    #numero de linhas que foram checadas
                    checked_lines += 1

        #armazena os angulos verticais e horizontais do arquivo ies
        ver_angles = ies_dict[keys_slice[0].value]
        hor_angles = ies_dict[keys_slice[1].value]
        #recebe as linhas restantes
        remaining_lines = ies_file_lines[checked_lines:]
        remaining_lines = [l.split('\n')[0].split(' ') for l in remaining_lines]
        
        #armazena a intensidade luminosa em candela
        candle_values = []
        for splited_lines in remaining_lines:
            only_numeric = [line for line in splited_lines if line.isnumeric() or '.' in line]
            candle_values += only_numeric

        #armazena a intensidade luminosa em candela no ies_dict para os angulos de interesse
        ies_dict[Keys.CANDELA_VALUES_SET.value] = {int(phi): {int(theta): 0 for theta in ver_angles} for phi in
                                                   hor_angles}
        for n, phi in enumerate(hor_angles):
            for m, theta in enumerate(ver_angles):
                ies_dict[Keys.CANDELA_VALUES_SET.value][int(phi)][int(theta)] = float(
                    self.potency_factor * candle_values[n * len(ver_angles) + m])

        return ies_dict
