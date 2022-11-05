import os
import sys
import numpy as np
import pandas as pd
from scipy import linalg
from scipy import integrate


def Gold(A, b, en, init_spectrum, dec_en, x0=False, it=None, w=False, d=False):
    A = np.array(A)
    b = np.array(b)
    b = b.reshape(len(b), -1)

    def deviation(init_spectrum, dec_spectrum):
        dec_spectrum_on_init_grid = np.interp(en, dec_en, dec_spectrum)
        different = [(i - j) ** 2 for i, j in zip(dec_spectrum_on_init_grid, init_spectrum)]
        init_sq = [val ** 2 for val in init_spectrum]

        def integral_t(different_signal, grid):
            s = 0
            for i in range(1, len(different_signal) - 2):
                s += (grid[i] - grid[i - 1]) * different_signal[i - 1]
            return s

        dev = integral_t(different, en) / integral_t(init_sq, en)
        return dev

    # Если начальное приближение не задано создает вектор-столбец x0 = [1, 1,.., 1]
    if x0:
        previous_x = np.ones((A.shape[1], 1), dtype=np.float64)
    # Транспонирование вектора х0, если он считывается вектором-строкой
    else:
        x0 = float(input('Введите начальное приближение: '))
        previous_x = x0 * np.ones((A.shape[1], 1), dtype=np.float64)
    # Транспонирование вектора b, если он считывается вектором-строкой
    if b.shape[1] != 1:
        b = b.T
    if it is None:
        num_of_iter = int(input('Введите число итераций: '))
    else:
        num_of_iter = it

    if w == False:
        W = np.diag([float(1 ** 2) for i in range(0, len(b))])
    if w == True:
        W = np.diag([float(i) for i in range(0, len(b))])

    current_x = np.ones((A.shape[1], 1), dtype=np.float64)
    norm_list = []
    deviation_list = []

    # Основной цикл алгоритма Голда
    for k in range(0, num_of_iter + 1):
        # Создание матрицы Y = A.T * W.T * W * b
        Y = np.dot(A.T, np.dot(W.T, np.dot(W, b)))
        # Создание матрицы AX = A.T * W.T * W * A * x
        AX = np.dot(A.T, np.dot(W.T, np.dot(W, np.dot(A, previous_x))))
        AX[AX == 0] = np.nextafter(0, 1)
        current_x = 1.0 * previous_x + (previous_x / AX) * (Y - AX)
        previous_x = current_x

        norm_list.append(linalg.norm(np.dot(A, current_x) - b))
        if d == True:
            deviation_list.append(deviation(init_spectrum, current_x.reshape(1, 1)[0].tolist()) ** 0.5)

    norm = [range(1, num_of_iter + 2), norm_list]

    if d == True:
        dev = [range(1, num_of_iter + 2), deviation_list]
    if d == False:
        dev = deviation(init_spectrum, current_x.reshape(1, -1)[0].tolist())**0.5


    current_x = current_x.reshape(1, -1)
    current_x = current_x[0].tolist()

    return current_x, norm, dev
	
	
	

def gold_deconvolution(A, b, x0=False, it=None, w=False):

	A = np.array(A)
	b = np.array(b)
	b = b.reshape(len(b),-1)


	# Если начальное приближение не задано создает вектор-столбец x0 = [1, 1,.., 1]
	if x0:
		previous_x = np.ones((A.shape[1], 1), dtype=np.float64)
	# Транспонирование вектора х0, если он считывается вектором-строкой
	else:
		x0 = float(input('Введите начальное приближение: '))
		previous_x = x0 * np.ones((A.shape[1], 1), dtype=np.float64)
	# Транспонирование вектора b, если он считывается вектором-строкой
	if b.shape[1] != 1:
		b = b.T
	if it is None:
		num_of_iter = int(input('Введите число итераций: '))
	else:
		num_of_iter = it

	if w == False:
		W = np.diag([float(1**2) for i in range(0, len(b))])
	if w == True:
		W = np.diag([float(i) for i in range(0, len(b))])

	current_x = np.ones((A.shape[1], 1), dtype=np.float64)
	norm_list = []

	# Основной цикл алгоритма Голда
	for k in range(0, num_of_iter + 1):
		# Создание матрицы Y = A.T * W.T * W * b
		Y = np.dot(A.T, np.dot(W.T, np.dot(W, b)))
		# Создание матрицы AX = A.T * W.T * W * A * x
		AX = np.dot(A.T, np.dot(W.T, np.dot(W, np.dot(A, previous_x))))
		AX[AX == 0] = np.nextafter(0, 1)
		current_x = 1.0 * previous_x + (previous_x / AX) * (Y - AX)
		previous_x = current_x

		norm_list.append(linalg.norm(np.dot(A, current_x) - b))
		norm = [range(1, num_of_iter + 2), norm_list]

		current_x = current_x.reshape(1, -1)
		current_x = current_x[0].tolist()
		
	return current_x, norm


def get_coeff_simpson(responce, grid, EDGE, min_index=None, max_index=None):
	simpson_coeff_list = []
	new_energy = []

	if min_index is None:
		min_index = 0
	if max_index is None:
		max_index = len(grid) - 2

	reverse = False
	def write():
		simpson_coeff_list.append(simpson)
		new_energy.append(grid[i])

	RIGHT_EDGE = [val+1 for val in EDGE]

	for i in range(min_index, max_index):
		if i not in RIGHT_EDGE:
			if i == min_index:
				simpson = (1/6)*(grid[i+2] - grid[i])*responce[i]
				write()
			if i == max_index - 1:
				simpson = (1/6)*(grid[i+2] - grid[i])*responce[i]
				write()

			# если i нечетное
			if i % 2 != 0 and i != min_index and i != max_index - 1:
				# если РЕВЕРС отключен
				if reverse == False:
					# если i-скачок
					if i in EDGE:
						simpson = (1/2)*(grid[i]-grid[i-1])*responce[i] + (1/6)*(grid[i+3]-grid[i+1])*responce[i+1] # К-нечетное-скачок
						write()
						continue
					# если i без скачка
					if i not in EDGE:
						simpson = (4/6)*(grid[i+1]-grid[i-1])*responce[i] # К-нечетное
						write()
				# если РЕВЕРС включен
				if reverse == True:
					# если i-скачок
					if i in EDGE:
						simpson = (1/6)*(grid[i]-grid[i-2])*responce[i] + (1/6)*(grid[i+3]-grid[i+1])*responce[i+1] # К-четное-скачок
						write()
						reverse = False
						continue
					# если i без скачка
					if i not in EDGE:
						simpson = (1/6)*(grid[i]-grid[i-2])*responce[i] + (1/6)*(grid[i+2]-grid[i])*responce[i] # К-четное
						write()

			# если i-четное
			if i % 2 == 0 and i != min_index and i != max_index - 1:
				# если РЕВЕРС отключен
				if reverse == False:
					# если i-скачок
					if i in EDGE:
						simpson = (1/6)*(grid[i]-grid[i-2])*responce[i] + (1/6)*(grid[i+3]-grid[i+1])*responce[i+1] # К-четное-скачок
						write()
						reverse = True
						continue
					# если i без скачка
					if i not in EDGE:
						simpson = (1/6)*(grid[i]-grid[i-2])*responce[i] + (1/6)*(grid[i+2]-grid[i])*responce[i] # К-четное
						write()
				# если РЕВЕРС включен
				if reverse == True:
					# если i-скачок
					if i in EDGE:
						simpson = (1/2)*(grid[i]-grid[i-1])*responce[i] + (1/6)*(grid[i+3]-grid[i+1])*responce[i+1] # К-нечетное-скачок
						write()
						continue
					# если i без скачка
					if i not in EDGE:
						simpson = (4/6)*(grid[i+1]-grid[i-1])*responce[i] # К-нечетное
						write()

		if i in RIGHT_EDGE:
			continue

	return simpson_coeff_list, new_energy













