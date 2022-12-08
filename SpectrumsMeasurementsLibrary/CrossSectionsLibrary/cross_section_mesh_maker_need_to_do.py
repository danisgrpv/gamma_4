import sys
import math
import numpy as np
import pandas as pd

from SpectrumsMeasurementsLibrary.CrossSectionsLibrary import cross_sections_processing
from cross_sections_processing import dataframe_to_list, interpolate_with_edge_from_minimal_en

# считывание данных
# Необходимо указать путь до Excel файла, содержащего исходные энергии и сечения epdl97
# en001 cs001 en002 cs002 ... en100 cs100
# Файл Excel получается в результате работы программы parser.py
INIT_CS_PATH_xlxs = input("Укажите путь до Excel файла, содержащего сечения epdl97")

cross_sections_df = pd.read_excel(INIT_CS_PATH_xlxs, header=None, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)
total = cross_sections_df['TOTAL']
absorbt = cross_sections_df['ABSORBT']


# Список со списками энергий каждого элемента
energies = dataframe_to_list(total, 'e')
min_en = 1e-3
# Создание списка с энергиями всех скачков
edge_energies = []
for list_ in energies:
    for energy in list_:
        if energy not in edge_energies:
            if energy >= min_en:
                if list_.count(energy) == 2:
                    edge_energies.append(energy)

edge_energies.sort()


# Создание основной сетки энергий
base = np.linspace(1, 8, 81)
base_enegries = []
for j in [3, 2, 1, 0]:
    values = [round(val*(10)**(-j), 10) for val in base]
    base_enegries.extend(values)


# Объединение основных энергий и энергий К скачков
general_grid = []
general_grid.extend(edge_energies)
general_grid.extend(edge_energies)

for val in base_enegries:
    if val not in general_grid:
        general_grid.append(val)

general_grid.sort()

# Добавление промежуточных точек между соседними скачками
for i in range(len(edge_energies) - 1):
    index_1 = general_grid.index(edge_energies[i]) + 1
    index_2 = general_grid.index(edge_energies[i + 1]) + 1

    if len(general_grid[index_1:index_2]) % 2 == 0:
        center = round((edge_energies[i] + edge_energies[i + 1]) / 2, 10)
        general_grid.append(center)

general_grid.sort()


# Добавление промежуточной точки между первой точкой и первым скачком
start = 0
first_edge_index = general_grid.index(edge_energies[0])

if len(general_grid[start + 1:first_edge_index]) % 2 == 0:
    center = round((general_grid[0] + edge_energies[0]) / 2, 10)
    general_grid.append(center)

general_grid.sort()


min_en = float(input("Укажите минимальную энергию: "))
cs_total = interpolate_with_edge_from_minimal_en(total, general_grid, min_en)
cs_absorbt = interpolate_with_edge_from_minimal_en(absorbt, general_grid, min_en)
