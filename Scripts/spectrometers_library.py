import copy
import numpy
from materials import*

def mpf_channels_response(regions):

	def mult(input_list):
		m = 1
		for i in input_list:
			m *= i
		return m

	R = []
	filters = [i.f() for i in regions]
	detectors = [i.d() for i in regions]
	detectors.insert(0, 0)

	for i in range(1, len(regions), 2):
		channel_response = mult(filters[:i]) * detectors[i + 1]
		R.append(channel_response)
		
	return R



def edge_channels_response(regions, detector):
	filters = [i.f() for i in regions]
	R = [filt * detector for filt in filters]
	return R



def ross_channels_response(regions, detector):
	filters = [regions[i].f() - regions[i - 1].f() for i in range(1, len(regions))]
	R = [filt * detector for filt in filters]
	return R



def differential_signal(spectrum, response):
	signal = spectrum * response
	return signal



def integral_signal(different_signal, grid):
	s = 0
	for i in range(1, len(different_signal) - 2):
		s += (grid[i] - grid[i - 1]) * different_signal[i - 1]
	return s



def ross(T, material_num_1, material_num_2, marker):

    t1, t2 = T
    f_1 = R(Material(material_num_1), t1).f()
    f_2 = R(Material(material_num_2), t2).f()

    diff_signal = f_2 - f_1

    def get_work_signal(diff_signal):
        work_signal = diff_signal[:]
        work_signal[:Material(material_num_1).k_index() + 1] = 0
        work_signal[Material(material_num_2).k_index():] = 0
        return work_signal

    def get_error_signal(diff_signal):
        error_signal = diff_signal[:]
        error_signal[Material(material_num_1).k_index():Material(material_num_2).k_index() + 1] = 0
        return error_signal

    if marker == 'resp_abs_tot':
        return R(Material(material_num_2), t2).f_at() - R(Material(material_num_1), t1).f_at()
    if marker == 'all':
        return  diff_signal
    if marker == 'work':
        work_signal = get_work_signal(diff_signal)
        return work_signal
    if marker == 'error':
        error_signal = get_error_signal(diff_signal)
        return error_signal
    if marker == 'ns':
        error = ross(T, material_num_1, material_num_2, marker='error')
        work = ross(T, material_num_1, material_num_2, marker='work')
        error_abs = [abs(i) for i in error]
        work_abs = [abs(i) for i in work]
        noise_level = integral_signal(error_abs, en) / integral_signal(work_abs, en)
        return noise_level
    if marker == 'intervals_mean':
        mean_energy = (Material(material_num_1).k_en() + Material(material_num_2).k_en()) / 2
        return mean_energy


def energy_in_region(brem, material_num_1, material_num_2, en):

    diff_signal = np.array(brem)
    diff_energy = np.array(en)
    brem_e = diff_signal * diff_energy
    brem_e[:Material(material_num_1).k_index()] = 0
    brem_e[Material(material_num_2).k_index() - 1:] = 0

    signal = integral_signal(brem_e, en)
    return signal
