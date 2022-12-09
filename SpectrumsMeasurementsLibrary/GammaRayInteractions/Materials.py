import numpy as np

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
        k_edge_index = ENERGY_MESH.index(self.K_edge_energy())
        return k_edge_index


    def thickness_for_level(self, level):
        """
        Возвращает толщину материала, необходимую для обеспечения заданного пропускания в К крае поглощения
        """
        linear_absorption_coefficient_in_k_edge = self.ro()*self.K_edge_value()*AVOGADRRO*BARN / self.mu()
        thickness_that_needed = np.log(level) / linear_absorption_coefficient_in_k_edge
        return thickness_that_needed


    def energy_absorption_coefficients(self):
        """
        Возвращает коэффициент поглощения энергии электронов данным веществом
        """
        total_cross_sections = self.cs('total')
        absorbt_cross_sections = self.cs('absorbt')
        coefficient = absorbt_cross_sections / total_cross_sections
        return coefficient

class R:

    def __init__(self, material_number, thickness):
        self.number = material_number
        self.thickness = thickness
        self.material = Material(self.number)


    def transmission(self):
        """
        Возвращает кривую пропускания излучения областью из данного вещества
        """
        index_of_power = self.material.cs('total')*self.thickness*self.material.ro()*AVOGADRRO*BARN / self.material.mu()
        transmission_function = np.exp(-index_of_power)
        return transmission_function


    def mass_transmission(self):
        """
        Возвращает кривую пропускания излучения областью из вещества с массовой толщиной
        """
        index_of_power = self.material.cs('total')*self.thickness*AVOGADRRO*BARN / self.material.mu()
        mass_transmission_function = np.exp(-index_of_power)
        return mass_transmission_function


    def attenuation(self):
        """
        Возвращает кривую ослабления излучения данной областью вещества
        """
        attenuation_function = 1 - self.transmission()
        return attenuation_function


    def mass_attenuation(self):
        """
        Возвращает кривую ослабления излучения данной областью вещества
        """
        mass_attenuation_function = 1 - self.mass_transmission()
        return mass_attenuation_function


    def emitted_bremsstrahlung(self, incident_electron_beam_energy):
        """
        Возвращает тормозной спектр, испущенный при прохождении излучения через данную область
        Параметр: энергия налетающего пучка электронов
        """
        energy = self.material.mesh()
        normalizing_factor = (incident_electron_beam_energy - energy) / incident_electron_beam_energy
        emitted_radiation = self.attenuation() / (energy * normalizing_factor)
        emitted_radiation[emitted_radiation < 0] = 0
        return emitted_radiation


    def mass_emitted_bremsstrahlung(self, incident_electron_beam_energy):
        """
        Возвращает тормозной спектр, испущенный при прохождении излучения через данную область с массовой толщиной
        Параметр: энергия налетающего пучка электронов
        """
        energy = self.material.mesh()
        normalizing_factor = (incident_electron_beam_energy - energy) / incident_electron_beam_energy
        emitted_radiation = self.mass_attenuation() / (energy * normalizing_factor)
        emitted_radiation[emitted_radiation < 0] = 0
        return emitted_radiation
