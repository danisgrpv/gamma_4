import time
import numpy as np
from CrossSectionsLibrary.cross_sections_data import ENERGY_MESH
from GammaRayInteractions.Materials import Material, R
from NumericalMethods.simpson_rule import simpson_rule
import numpy as np

def initialization_brem(material_z, beam_energy, tick=0.01):
    """
    Функция принимает материал мишени и энергию налетающего 
    электронного пучка
    Возвращаемое значение: генерируемый тормозной спектр
    """
    
    coefficient = Material(material_z).mu()/material_z
    target = R(material_z, tick*coefficient)
    bremsstrahlung = target.mass_emitted_bremsstrahlung(beam_energy)
    
    return bremsstrahlung


def generate_empty_matrix(num_row, num_col):
    """
    Функция создает пустую матрицу заданных размеров
    """
    empty_matrix = [[i for i in range(num_col)] for j in range(num_row)]
    return empty_matrix


def complete_empty_matrix(empty_matrix, array_1, array_2, func):
    """
    Функция заполняет пустую матрицу заданными элементами из массивов
    array_1, array_2 по правилу, определяемому функцией fucn.
    Возвращает заполненную матрицу np.ndarray
    """
    for row, val_1 in enumerate(array_1):
        for col, val_2 in enumerate(array_2):
            empty_matrix[row][col] = func(val_1, val_2)
            
    return np.array(empty_matrix)


def integrate_the_row(row):
    """
    Функция возвращает значение интеграла вычисленное
    по правилу Симпсона
    """
    return simpson_rule(row)


def get_integral_signals(bremsstrahlung, K):
    """
    Фукнция возвращает результаты измерения спектра
    измерительной системой K
    Параметры: 
    1) измеряемый спектр
    2) матрица измерительной системы
    """
    measurements = K*bremsstrahlung
    integral_signals = np.apply_along_axis(integrate_the_row, arr=measurements, axis=1)
    return integral_signals


def apply_function_to_matrix(objective_matrix, func, K):
    """
    Функция применяет правило, определяемое функцией func к
    каждому элементу целевой матрицы и создает матрицу возвращаемых
    значений
    Параметры:
    1) целевая матрица
    2) функция, определяющая возвращаемые значения
    """
    num_row = objective_matrix.shape[0]
    num_col = objective_matrix.shape[1]
    
    empty_matrix = [[i for i in range(num_col)] for j in range(num_row)]
    
    # время начала
    start_time = time.time()
    
    for row in range(num_row):
        for col in range(num_col):
            empty_matrix[row][col] = func(objective_matrix[row][col], K)
            print(f'Выполнено {col+1} из {num_col}. Время: {round(time.time()-start_time, 4)} секунды')
        print(f'ВЫПОЛНЕНО {row+1} из {num_row} СТОЛБЦОВ. Время: {round(time.time()-start_time, 4)} секунды') 
    return np.array(empty_matrix)


def get_measuring_systems_signals(brem, new_mesh, measuring_system_matrix):

    measuring_systems_signals = []

    new_brem = np.interp(new_mesh, ENERGY_MESH, brem)
    for ind, matrix in enumerate(measuring_system_matrix):
        signals = matrix @ new_brem
        measuring_systems_signals.append(signals)

    return np.array(measuring_systems_signals)


def get_brem_measuring_results(bremsstrahlungs_matrix, measuring_system_matrix, new_mesh, empty):
    for row, val1 in enumerate(empty):
        for col, val2 in enumerate(empty[row]):
            empty[row][col] = get_measuring_systems_signals(bremsstrahlungs_matrix[row][col], new_mesh, measuring_system_matrix)

    return empty