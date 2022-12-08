import os
import numpy as np

current_directory = os.path.dirname(__file__)
cross_sections_datafiles_folder_name = "CS_npy" # имя папки, в которой содеждатся файлы с массивами сечений

# файл с исходными сечениями np.array([CS_init_mesh, CS_total, CS_absorbt]
init_cross_section_file_name = 'CROSS_SECTION_INIT.npy'
# файл с обработанными сечениямиями np.array([general_grid, total_general.npy, absorbt_general.npy])
processed_cross_section_file_name = 'CROSS_SECTION_PROCESSED_mesh_01.npy'
# путь до файла с исходными сечениями
init_cross_section_file_path = os.path.join(current_directory, cross_sections_datafiles_folder_name, init_cross_section_file_name)
# путь до файла с обработанными сечениями
processed_cross_section_file_path = os.path.join(current_directory, cross_sections_datafiles_folder_name, processed_cross_section_file_name)

# загрузка массивов numpy с данными о сечениях
init_cross_section_npy = np.load(init_cross_section_file_path, allow_pickle=True)
processed_cross_section_npy = np.load(processed_cross_section_file_path, allow_pickle=True)

# initial_meshs = [en001, en002, ... en100]
# initial_total_cs= [cs_total001, cs_total002, ... cs_total100]
# initial_absorbt_cs = [cs_absorbt001, cs_absorbt002, cs_absorbt100]
INITIAL_meshs = init_cross_section_npy[0]
INITIAL_total_cs = init_cross_section_npy[1]
INITIAL_absorbt_cs = init_cross_section_npy[2]

# Общая энергетическая сетка и интерполированные на ней сечения
ENERGY_MESH = processed_cross_section_npy[0]
TOTAL = processed_cross_section_npy[1]
ABSORBT = processed_cross_section_npy[2]
