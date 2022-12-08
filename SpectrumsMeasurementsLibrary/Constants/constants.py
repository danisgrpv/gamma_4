import os
import numpy as np

current_directory = os.path.dirname(__file__)

# файл со свойствами материалов [[Молярные массы], [Плотности веществ]]
materials_property_file_name = 'MATERIALS_PROPERTY.npy'
# путь до файла со свойствами материалов
materials_property_file_path = os.path.join(current_directory, materials_property_file_name)
# загрузка файла npy со свойствами материалов
materials_property_npy = np.load(materials_property_file_path, allow_pickle=True)

RO = materials_property_npy[1] # массив плотностей материалов
MU = materials_property_npy[0]  # массив молярных масс материалов

AVOGADRRO = 6.02214076E+23 # частиц на моль
BARN= 1E-24 # см^2
