import math
import numpy as np


def dataframe_to_list(dataframe, marker='m'):
    """
    Принимает датафрейм с сечениями epdl97 вида en001 cs001 en002 cs002
    и разбивает его на два списка
    первый список [en001, en002, en003..]
    второй список [cs001, cs002, cs003]
    :param marker: флаг: e, c, m
    :param dataframe:
    :return: m - list [[en001, cs001], [en002, cs002]] список пар энерния-сечение
    materials[i][j], i = 0..99 - индекс элемента, j = 0,1: 0-энергия, 1-сечение
    e - list[en001, en002, en003..]
    c - list[cs001, cs002, cs003]
    """

    energy_lists = []
    cross_sections_lists = []

    num = int(len(dataframe.iloc[0]))
    for i in range(0, num):
        if i % 2 == 0:
            energy_lists.append((dataframe[i]).dropna().to_list())
        else:
            cross_sections_lists.append(dataframe[i].dropna().to_list())

    materials = list(zip(energy_lists, cross_sections_lists))

    if marker == 'm':
        return materials
    if marker == 'e':
        return energy_lists
    if marker == 'c':
        return cross_sections_lists


def edge_to_dict(number, marker, dataframe):
    """
    :param number: индекс элемента
    :param marker: флаг, имеет два значения
        если marker_side='0' - возвращаются значения сечений K-скачка
        при стремлении слева
        если marker_side='1' - возвращаются значения сечений K-скачка
        при стремлении справа
    :return: dict словарь со значениями энергий и сечений K-скачов
    """

    # распаковка списка materials_list
    materials_list = dataframe_to_list(dataframe)
    energy = materials_list[number][0]
    cross_section = materials_list[number][1]

    # списки, содержащие значения сечений слева и справа в точке разрыва
    left_k_cs, right_k_cs, k_energies = [], [], []

    for i, en in enumerate(energy):
        if np.isclose(energy[i - 1], energy[i], atol=1e-50):
            right_k_cs.append(cross_section[i])
            left_k_cs.append(cross_section[i - 1])
            k_energies.append(en)

    if marker == 'energy':
        return k_energies
    if marker == 'left':
        return left_k_cs
    if marker == 'right':
        return right_k_cs


def get_general_grid(dataframe):
    """
    :param dataframe: датафрейм энергий и сечегий epdl97
    :return: list список - общую энергетическую сетку
    """
    energies = dataframe_to_list(dataframe, marker='e')
    general_grid = []

    for list_ in energies:
        # для каждого значения энергии в выбраной сетке
        for energy in list_:
            # в общую сетку добавляются те значения энегии, которых еще не было
            if energy not in general_grid:
                # если значение энергии встречается два раза (K-скачок) добавить
                # значение два раза
                if list_.count(energy) == 2:
                    general_grid.append(energy)
                    general_grid.append(energy)
                else:
                    general_grid.append(energy)

    general_grid.sort()
    return general_grid


def interpolate_cs_on_general_grid(dataframe, general_grid):
    """
    :param dataframe: датафрейм энергий и сечегий epdl97
    :return: список списков [[интерполированные сечения1], [интерполированные сечения2], ..]
    """
    num = int(len(dataframe.iloc[0]) / 2)
    # general_grid = get_general_grid(dataframe)
    energies = dataframe_to_list(dataframe, marker='e')
    cross_sections = dataframe_to_list(dataframe, marker='c')
    interpolated_cross_sections = [np.interp(general_grid, energies[i], cross_sections[i]) for i in range(0, num)]

    return interpolated_cross_sections


def to_log(dataframe):
    """
    :param dataframe: датафрейм энергий и сечегий epdl97
    :return: датафрейм логарифмов исходных значений
    """
    dataframe_copy = dataframe.copy()
    for column in dataframe_copy.columns:
        dataframe_copy[column] = dataframe[column].agg(lambda x: math.log(x))

    return dataframe_copy


def to_linear(dataframe):
    """
    :param dataframe: датафрейм энергий и сечегий epdl97 в логарифме
    :return: датафрейм линеарезованных значений
    """
    dataframe_copy = dataframe.copy()
    for column in dataframe_copy.columns:
        dataframe_copy[column] = dataframe[column].agg(lambda x: math.exp(x))

    return dataframe_copy


def interpolate_with_edge(dataframe, general_grid):
    """
    :param dataframe: датафрейм энергий и сечений epdl97
    :return: список списков [[интерполированные сечения1], [интерполированные сечения2], ..] с исправленными скачками
    """
    materials = dataframe_to_list(dataframe)
    # gg = get_general_grid(dataframe)  # gg - general grid
    gg = general_grid
    ics = interpolate_cs_on_general_grid(dataframe, gg)  # ics - interpolated cross sections

    ggl = [math.log(val) for val in gg]  # ggl - general grid logarithm
    dfl = to_log(dataframe)
    icsl = interpolate_cs_on_general_grid(dfl, ggl)  # icsl - interpolated cs logarithm

    for list_ in icsl:
        for p, val in enumerate(list_):
            list_[p] = math.exp(val)  # icls из логарифма переводится в линейный

    for i, material in enumerate(materials):
        for j, edge in enumerate(edge_to_dict(i, 'energy', dataframe)):
            icsl[i][gg.index(edge_to_dict(i, 'energy', dataframe)[j])] = edge_to_dict(i, 'left', dataframe)[j]
            icsl[i][gg.index(edge_to_dict(i, 'energy', dataframe)[j]) + 1] = edge_to_dict(i, 'right', dataframe)[j]

    return icsl


def get_general_grid_center(dataframe):
    energies = dataframe_to_list(dataframe, marker='e')
    general_grid = []

    for list_ in energies:
        # для каждого значения энергии в выбраной сетке
        for energy in list_:
            # в общую сетку добавляются те значения энегии, которых еще не было
            if energy not in general_grid:
                # если значение энергии встречается два раза (K-скачок) добавить
                # значение два раза
                if list_.count(energy) == 2:
                    general_grid.append(energy)
                    general_grid.append(energy)
                    general_grid.append(energy)
                else:
                    general_grid.append(energy)

    general_grid.sort()
    return general_grid


def interpolate_with_edge_center(dataframe):
    materials = dataframe_to_list(dataframe)
    gg = get_general_grid_center(dataframe)  # gg - general grid
    ics = interpolate_cs_on_general_grid(dataframe, gg)  # ics - interpolated cross sections

    ggl = [math.log(val) for val in gg]  # ggl - general grid logarithm
    dfl = to_log(dataframe)
    icsl = interpolate_cs_on_general_grid(dfl, ggl)  # icsl - interpolated cs logarithm

    for list_ in icsl:
        for p, val in enumerate(list_):
            list_[p] = math.exp(val)  # icls из логарифма переводится в линейный

    for i, material in enumerate(materials):
        for j, edge in enumerate(edge_to_dict(i, 'energy', dataframe)):
            val = (edge_to_dict(i, 'left', dataframe)[j] + edge_to_dict(i, 'right', dataframe)[j]) / 2

            icsl[i][gg.index(edge_to_dict(i, 'energy', dataframe)[j])] = edge_to_dict(i, 'left', dataframe)[j]
            icsl[i][gg.index(edge_to_dict(i, 'energy', dataframe)[j]) + 1] = val
            icsl[i][gg.index(edge_to_dict(i, 'energy', dataframe)[j]) + 2] = edge_to_dict(i, 'right', dataframe)[j]

    return icsl


def dataframe_to_array(dataframe):
    l = len(dataframe.columns)
    indexes = np.array(range(0, l))
    dataframe = dataframe.set_axis(indexes, axis=1)
    materials_array = [dataframe[col].to_list() for col in dataframe.columns]

    return materials_array

