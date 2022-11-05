import numpy as np
import pandas as pd

avogadro = 6.02214076E+23
barn = 1E-24

min_en = float(input('Минимальная энергия: '))
system = input('windows (w) or linux (l): ')

if system == 'l':
    cs = pd.read_excel(r'/home/danis/work/python_works/gamma_4/Scripts/DATA/cross_sections_with_header.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)
    materials = pd.read_excel(r'/home/danis/work/python_works/gamma_4/Scripts/DATA/materials_property.xlsx', header=0, index_col=0, sheet_name=['PROPERTY', 'ELEMENTS'])

    elements = materials['ELEMENTS']
    total = cs['TOTAL']
    absorbt = cs['ABSORBT']

    total_general = pd.read_excel(r'/home/danis/work/python_works/gamma_4/Scripts/DATA/GENERAL/GENERAL_01.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)['TOTAL']
    absorbt_general = pd.read_excel(r'/home/danis/work/python_works/gamma_4/Scripts/DATA/GENERAL/GENERAL_01.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)['ABSORBT']

if system == 'w':
    cs = pd.read_excel(r'D:\Учеба\Практика\Диплом\gamma_4\Scripts\DATA\cross_sections_with_header.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)
    materials = pd.read_excel(r'D:\Учеба\Практика\Диплом\gamma_4\Scripts\DATA\materials_property.xlsx', header=0, index_col=0, sheet_name=['PROPERTY', 'ELEMENTS'])

    elements = materials['ELEMENTS']
    total = cs['TOTAL']
    absorbt = cs['ABSORBT']

    total_general = pd.read_excel(r'D:\Учеба\Практика\Диплом\gamma_4\Scripts\DATA\GENERAL\GENERAL_01.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)['TOTAL']
    absorbt_general = pd.read_excel(r'D:\Учеба\Практика\Диплом\gamma_4\Scripts\DATA\GENERAL\GENERAL_01.xlsx', header=0, sheet_name=['TOTAL', 'ABSORBT'], dtype=np.float64)['ABSORBT']

def edge_to_dict(number, marker_side, dframe):


    """
    Возвращаемое значение:
        1) type: dict
           Массив со значениями энергий и сечений K-скачов
        
        Параметры:
        1) type: int
           number - номер элемента (зарядовое число Z)
           
        2) type: str
           marker_side - флаг. Имеет два значения 't' и 'a'
           если marker_side='left' - возвращаются значения сечений K-скачка 
           при стремлении слева
           
           если marker_side='right' - возвращаются значения сечений K-скачка 
            при стремлении справа
    """

    # получение списка энергий и сечений из датафрейма
    energy = dframe[f'en{number:03}'].dropna().tolist()
    cross_section = dframe[f'cs{number:03}'].dropna().tolist()

    # списки, содержащие значения сечений слева и справа в точке разрыва
    K_left, K_right, E, index = [], [], [], []

    for i, en in enumerate(energy):
        if energy[i - 1] >= min_en:
            if np.isclose(energy[i - 1], energy[i], atol=1e-50):
                K_right.append(cross_section[i])
                K_left.append(cross_section[i - 1])
                E.append(en)
                index.append(i)

    if marker_side == 'left':
        return dict(zip(E, K_left))
    
    if marker_side == 'right':
        return dict(zip(E, K_right))

    if marker_side == 'energy':
        return E


class Material:
    """Модель материала вещества"""


    global total_general
    global absorbt_general
    
    def __init__(self, number):
        """Инициализирует атрибуты number - зарядовое число Z и ro - плотность вещества"""
        self.number = number
        
    def en(self):
        """Возвращает энергетическую сетку"""
        energy = total_general.filter([f'en'], axis=1)
        energy.columns = ['en']
        return energy
    
    def cs(self, marker):
        """Возвращает сечение взаимодействия. 't' - полное сечение взнаимодейтсвия, 
        'a' - сечение поглощения"""
        if marker == 't':
            cross_section_t = total_general.filter([f'cs{self.number:03}'], axis=1)
            cross_section_t.columns = ['cs']
            return cross_section_t
        if marker == 'a':
            cross_section_a = absorbt_general.filter([f'cs{self.number:03}'], axis=1)
            cross_section_a.columns = ['cs']
            return cross_section_a
        
    def ro(self):
        """Плотность вещества"""
        elements_property = materials['PROPERTY']
        return elements_property.loc['ro'][f'el{self.number:03}']
    
    def M(self):
        """Молярная масса вещества"""
        elements_property = materials['PROPERTY']
        return elements_property.loc['mu'][f'el{self.number:03}']
    
    def k(self):
        """Значение сечения К-скачка"""
        a = edge_to_dict(self.number, 'left', total)
        b = list(a.keys())
        k_edge = a[b[-1]]
        return k_edge
    
    def k_en(self):
        """Значение энергии К-скачка"""
        a = edge_to_dict(self.number, 'left', total)
        b = list(a.keys())
        return b[-1]
    
    def k_index(self):
        """Индекс К-скачка"""
        en = self.en()['en'].tolist()
        index = en.index(self.k_en())
        return index
    
    def lt(self, level):
        """Возвращает толщину для К-края выбранной высоты"""
        mu_k_edge = -self.ro()*avogadro*self.k()*barn/self.M()
        t = np.log(level) / mu_k_edge
        return t


class R:


    def __init__(self, material, thickness):
        self.material = material
        self.thickness = thickness
        
    def f(self):
        mat = self.material
        out = np.exp(-mat.cs('t')*self.thickness*avogadro*mat.ro()*barn/mat.M())
        return out['cs'].to_numpy(dtype=np.float64)

    def f_at(self):
        mat = self.material
        out = (mat.cs('a')/mat.cs('t'))*np.exp(-mat.cs('t')*self.thickness*avogadro*mat.ro()*barn/mat.M())
        return out['cs'].to_numpy(dtype=np.float64)
    
    def d(self):
        mat = self.material
        out = (mat.cs('a')/mat.cs('t'))*np.exp(-mat.cs('t')*self.thickness*avogadro*mat.ro()*barn/mat.M()).agg(lambda x: 1 - x)
        return out['cs'].to_numpy(dtype=np.float64)
    
    def brem(self, energy):
        mat = self.material
        en = mat.en()['en'].to_numpy(dtype=np.float64)
        brem = self.f() / en * ((energy - en) / energy)
        brem[brem < 0] = 0
        
        return brem / max(brem)

# материалы

H = Material(1)
He = Material(2)
Li = Material(3)
Be = Material(4)
B = Material(5)
C = Material(6)
N = Material(7)
O = Material(8)
F = Material(9)
Ne = Material(10)
Na = Material(11)
Mg = Material(12)
Al = Material(13)
Si = Material(14)
P = Material(15)
S = Material(16)
Cl = Material(17)
Ar = Material(18)
K = Material(19)
Ca = Material(20)
Sc = Material(21)
Ti = Material(22)
V = Material(23)
Cr = Material(24)
Mn = Material(25)
Fe = Material(26)
Co = Material(27)
Ni = Material(28)
Cu = Material(29)
Zn = Material(30)
Ga = Material(31)
Ge = Material(32)
As = Material(33)
Se = Material(34)
Br = Material(35)
Kr = Material(36)
Rb = Material(37)
Sr = Material(38)
Y = Material(39)
Zr = Material(40)
Nb = Material(41)
Mo = Material(42)
Tc = Material(43)
Ru = Material(44)
Rh = Material(45)
Pd = Material(46)
Ag = Material(47)
Cd = Material(48)
In = Material(49)
Sn = Material(50)
Sb = Material(51)
Te = Material(52)
I = Material(53)
Xe = Material(54)
Cs = Material(55)
Ba = Material(56)
La = Material(57)
Ce = Material(58)
Pr = Material(59)
Nd = Material(60)
Pm = Material(61)
Sm = Material(62)
Eu = Material(63)
Gd = Material(64)
Tb = Material(65)
Dy = Material(66)
Ho = Material(67)
Er = Material(68)
Tm = Material(69)
Yb = Material(70)
Lu = Material(71)
Hf = Material(72)
Ta = Material(73)
W = Material(74)
Re = Material(75)
Os = Material(76)
Ir = Material(77)
Pt = Material(78)
Au = Material(79)
Hg = Material(80)
Tl = Material(81)
Pb = Material(82)
Bi = Material(83)
Po = Material(84)
At = Material(85)
Rn = Material(86)
Fr = Material(87)
Ra = Material(88)
Ac = Material(89)
Th = Material(90)
Pa = Material(91)
U = Material(92)
Np = Material(93)
Pu = Material(94)
Am = Material(95)
Cm = Material(96)
Bk = Material(97)
Cf = Material(98)
Es = Material(99)
Fm = Material(100)

# ОБЩАЯ СЕТКА ЭНЕРГИЙ
en = H.en()['en'].tolist()
