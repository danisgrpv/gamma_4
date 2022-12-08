from SpectrumsMeasurementsLibrary.Constants.constants import AVOGADRRO, BARN
from SpectrumsMeasurementsLibrary.CrossSectionsLibrary.cross_sections_processing import get_edges_list
from SpectrumsMeasurementsLibrary.CrossSectionsLibrary.cross_sections_data import INITIAL_meshs, \
    INITIAL_total_cs, INITIAL_absorbt_cs, ENERGY_MESH, TOTAL, ABSORBT
from SpectrumsMeasurementsLibrary.Constants.constants import AVOGADRRO, BARN, RO, MU

# функция возвращает значения сечений скачков
get_edges = lambda number, marker: get_edges_list(number, marker, INITIAL_meshs, INITIAL_total_cs)
# функция возвращает значения энергий скачков
get_edges_energies = lambda number: get_edges_list(number, 'energy', INITIAL_meshs, INITIAL_total_cs)

class Material:

    def __init__(self, number):
        self.number = number - 1 # номер элемента в массиве на единицу меньше номера в таблице Менделеева


    def mesh(self):
        """
        Возвращает энергетическую сетку MESH, на которой построенны все данные
        """
        return ENERGY_MESH


    def cs(self, marker):
        """
        Возвращает сечение взаимодействия гамма квантов с данным веществом
        Параметры:
        1) total - полное сечение взнаимодейтсвия,
        2) absorbt - сечение поглощения энергии
        """
        if marker == 'total':
            return TOTAL[self.number]
        if marker == 'absorbt':
            return ABSORBT[self.number]


    def ro(self):
        """
        Возвращает значение плотности данного вещества
        """
        return RO[self.number]


    def mu(self):
        """
        Возвращает молярную массу данного вещества
        """
        return MU[self.number]


    def K_edge_value(self):
        """
        Возвращает значение сечения в К крае поглощения
        """
        all_edges = get_edges(self.number, marker='left')
        return all_edges[-1]


    def K_edge_energy(self):
        """
        Возвращает значение сечения в К крае поглощения
        """
        all_edges_energies = get_edges_energies(self.number)
        return all_edges_energies[-1]


    def K_edge_index(self):
        """
        Возвращает индекс К края поглощения данного материала в общей энергетической сетке MESH
        """
        energy_mesh_list = ENERGY_MESH.tolist()
        k_edge_index = energy_mesh_list.index(self.K_edge_energy())
        return k_edge_index