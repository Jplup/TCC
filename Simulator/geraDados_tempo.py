import json
from ambient import Ambient
from simulator import Simulator

scale_factor_x = 1.78
scale_factor_y = 2.72
scale_factor_z = 1.84
scale_factor_x = 4
scale_factor_y = 5
scale_factor_z = 3

xPadding=scale_factor_x/6
yPadding=scale_factor_y/6

lampPositions=[
    [xPadding, yPadding, scale_factor_z-0.1],
    [scale_factor_x-xPadding, yPadding, scale_factor_z-0.1],
    [xPadding, scale_factor_y-yPadding, scale_factor_z-0.1],
    [scale_factor_x-xPadding, scale_factor_y-yPadding, scale_factor_z-0.1]
]
sufixes=[
    "",
    "VPPM2",
    "VPPM3",
    "60Hz"
]

for saveDirSufix,lampXYZ in zip(sufixes,lampPositions):
    saveDir="temporalResults"+saveDirSufix
    floorLevel=0.07

    # ==========================================================================================
    # Diretórios
    dir_a = 'data/'
    dir_b = 'Salinha/'
    dir_c = 'Disc7x7/'
    dir_d = '4lum/'
    dir_e = 'NovaModulacao/'
    dir_f = 'Amostragem100kHz/'

    # Arquivos
    IES = 'LampPhilips_Modificado'
    filename = 'DadosTempo_NovaModulacao'

    # Tipos de dados
    type_a = '.json'
    type_b = '.txt'

    # ==========================================================================================
    # Dict com caracteristicas do ambiente, luminarias e sensor
    ambient_sets = {
        'total_simulation_time': 0.2/50000,      #0.0036,      #None,
        'ambient': {
            'room_sizes': {'x': scale_factor_x * 1, 'y': scale_factor_y * 1, 'z': scale_factor_z * 1},
            'floor_level': floorLevel,
            'divisions_number': 13,             # x = Disc - 1
            # 'divisions_number': {'x': 29, 'y': 9, 'z': 29},
            'sample_frequency': 100e5,
            'walls_refletance': 0.00,
            'refletance_aperture': None,
            'walls': [
                {'x': 0},
                {'x': scale_factor_x * 1},
                {'y': 0},
                {'y': scale_factor_y * 1}
            ]
        },
        'luminaries': {
            'positions': [
                ##Salinha (luminárias na ordem das freq. de mod., i.e., 1k,2k,3k,4k)
                #{'x': 0.26, 'y': 2.31, 'z': 1.74},        # A 1kHz
                #{'x': 1.51, 'y': 2.37, 'z': 1.74},        # B 2.1kHz
                #{'x': 1.52, 'y': 0.36, 'z': 1.74},        # C 3.2kHz
                #{'x': 0.25, 'y': 0.36, 'z': 1.74}         # D 4.3kHz
                
                {'x': lampXYZ[0], 'y': lampXYZ[1], 'z': lampXYZ[2]} 

                ##Normal
                # {'x': scale_factor_x * 0.25, 'y': scale_factor_y * 0.25, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.75, 'y': scale_factor_y * 0.25, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.25, 'y': scale_factor_y * 0.75, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.75, 'y': scale_factor_y * 0.75, 'z': scale_factor_z * 1},
                
                ##Cantos
                # {'x': scale_factor_x * 0.12, 'y': scale_factor_y * 0.12, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.12, 'y': scale_factor_y * 0.88, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.88, 'y': scale_factor_y * 0.12, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.88, 'y': scale_factor_y * 0.88, 'z': scale_factor_z * 1}
                
                ##Centro
                # {'x': scale_factor_x * 0.38, 'y': scale_factor_y * 0.38, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.38, 'y': scale_factor_y * 0.62, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.62, 'y': scale_factor_y * 0.38, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.62, 'y': scale_factor_y * 0.62, 'z': scale_factor_z * 1}
                
                ## 9 luminárias
                # {'x': scale_factor_x * 0.25, 'y': scale_factor_y * 0.25, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.75, 'y': scale_factor_y * 0.25, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.50, 'y': scale_factor_y * 0.75, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.25, 'y': scale_factor_y * 0.75, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.75, 'y': scale_factor_y * 0.75, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.50, 'y': scale_factor_y * 0.50, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.50, 'y': scale_factor_y * 0.25, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.25, 'y': scale_factor_y * 0.50, 'z': scale_factor_z * 1},
                # {'x': scale_factor_x * 0.75, 'y': scale_factor_y * 0.50, 'z': scale_factor_z * 1}
                
            ],
            'ies_file_path': dir_a + IES + type_b,
            # 'modulation_frequencies': [4300]
            # 'modulation_frequencies': [1000, 2100, 3200, 4300]
            'modulation_frequencies': [50000]

            
            #10000, 21000, 32000, 43000, 54000, 65000, 76000, 87000, 98000
        },
        'sensor': {'position': {'x': 0, 'y': 0, 'z': 0},
                'filter_parameter': {'filter_1': {'low_cut': 1500.0,
                                                    'high_cut': 2250.0,
                                                    'order': 5}}}
    }

    # =============================================================================
    # SIMULAÇÃO
    # =============================================================================
    # Cria objetos do tipo Ambient e Simulator
    ambient = Ambient(ambient_sets)
    simulator = Simulator(ambient)
    # Calcula e retorna a iluminancia total (direta e refletida) para todos os ptos do plano no tempo
    results = simulator.simulate()

    ##-----------------------------------------------------------------------------
    ## COMENTAR AO USAR NÚMERO DE DIVISÕES DIFERENTES PARA CADA EIXO
    # Plota um mapa de calor da iluminancia no mapa no instante dt
    simulator.plotting(0)
    ##-----------------------------------------------------------------------------

    # Armazena a iluminancia total (direta e refletida) para todos os ptos do plano no tempo
    temporal_results = {x: {y: [] for y in results[0][0].keys()} for x in results[0].keys()}

    for dt in results.keys():
        for x in results[dt].keys():
            for y in results[dt][x].keys():
                temporal_results[x][y].append(results[dt][x][y])

    # Salva em "temporal_results.json" os valores de iluminancia calculados
    with open(saveDir+".json", 'w') as f:
        json.dump(temporal_results, f)

    params={
        "Dim":[scale_factor_x,scale_factor_y,scale_factor_z],
        "Lamp":[ambient_sets['luminaries']['positions'][0]],
        "Plano":floorLevel
    }

    with open(saveDir+"Params.json",'w') as fs: json.dump(params,fs)
