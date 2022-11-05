import os
import re

from xlsxwriter.workbook import Workbook

workbook = Workbook("cross_sections.xlsx")
worksheet_1 = workbook.add_worksheet('TOTAL')
worksheet_2 = workbook.add_worksheet('ABSORBT')


folder_1 = input('Путь до папки STOT: ')
folder_2 = input('Путь до папки ABSORBT: ')

data_directory_1 = os.path.join(os.getcwd(), folder_1)
data_directory_2 = os.path.join(os.getcwd(), folder_2)

def to_lists(lines):
    """Получает два списка из первой и последней колонки из строк файла"""
    first = []
    last = []

    for line in lines[1:]:
        parts = line.split()
        first.append(float(parts[0]))
        last.append(float(parts[-1]))

    return first, last


def sort_by_number(input_string):
        return int(re.search(r"\d+$", input_string)[0])

def parse_files(path, worksheet):
    """Проходит по файлам из data_directory и обрабатывает их, записывает результат в директорию dist"""
    file_names = os.listdir(path)
    file_names.sort(key=sort_by_number)
    column_index = 0

    for file_name in file_names:
        with open(os.path.join(path, file_name)) as file:
            lines = file.readlines()
            first, last = to_lists(lines)
            # header = lines[0].strip() отключили запись заголовка в первую строку
            # worksheet.write_column(0, column_index, [header])
            worksheet.write_column(0, column_index, first)
            column_index += 1
            worksheet.write_column(0, column_index, last)
            column_index += 1


parse_files(data_directory_1, worksheet_1)
parse_files(data_directory_2, worksheet_2)

workbook.close()

