# -*- coding: utf-8 -*-

from fcntl import flock, LOCK_EX, LOCK_NB, LOCK_UN
from time import sleep
from socket import gethostbyname
from sys import argv

DOMAINS_FILE_PATH = 'domains'  # путь до файла с доменами
RESULTS_FILE_PATH = 'results'  # путь до файла с резульатом
POSITION_FILE_PATH = 'position'  # путь до файла с указателем
# сколько ссылок программа будет считывать из файла за раз
LINKS_PER_ITERATION_NUMBER = 3


def enter_lock(file):
    # устанавливает lock на файл, пытется захватить его в случае неудачи
    while True:
        try:
            flock(file, LOCK_EX | LOCK_NB)
        except BlockingIOError as e:
            sleep(0.005)
        else:
            return


def exit_lock(f):
    # снимает lock с файла
    flock(f, LOCK_UN)
    f.close()


def main():
    # Реализация справки по ключу -h или --help
    if '-h' in argv or '--help' in argv:
        help_text = '''
        Данная прогамма определяет ip по домену. Домены берутся из файла domains,
        результаты упаковываются в файл results. Файл pointer - является системным.
        '''
        print(help_text)
        return

    # статус выполнения алгоритма
    running = True
    # маркер первой итерации
    while running:

        pointer_file = open(POSITION_FILE_PATH, 'r')

        '''
        блокируем файл для других процессов для того, что бы не попасть в
        ситуацию, когда после того, как мы считаем значение указателя, другой
        процесс не записал туда новое значение, тем самым нарушив работу программы
        '''
        enter_lock(pointer_file)
        # патаемся считать значение из файла pointer
        file_data = pointer_file.readlines()[0].strip()
        # присваеваем перменной значение из файла pointer
        if file_data == 'END':
            return

        pointer = int(file_data)

        # записываем новое значение в файл pointer
        open(POSITION_FILE_PATH, 'w').write(
            str(pointer + LINKS_PER_ITERATION_NUMBER))

        # снимаем lock с файла
        exit_lock(pointer_file)
        # закрываем файл
        pointer_file.close()


        '''
        Условие, которое предотвращает ситуацию, когда один процесс завершился и
        обнулил указатель, а второй считал его и начал обработку данных по новой.
        Если итерация не первая (is_first_iteration=False), тогда программа уже
        работала до этого, в таком случае - нулевой указатель, это маркер остановки
        работы программы. Если итерация первая (is_first_iteration=True), тогда
        программа начинает работу со строки с индексом 0.
        '''
        if pointer == 'END':
            return


        # открываем файл, который содержит домены
        file_data = open(DOMAINS_FILE_PATH, 'r').readlines()
        '''
        Если значение указателя + количество единожды обрабатоваемых доменов,
        больше, чем количество доменов (строк) в файле, тогда эта итерация
        объявляется полседней и работа программы должна завершиться.
        '''
        if len(file_data) <= pointer + LINKS_PER_ITERATION_NUMBER:
            open(POSITION_FILE_PATH, 'w').write('END')
            running = False
        '''
        Cобираем нужные нам данные в промежутке от значения pointer, до
        значения pointer + LINKS_PER_ITERATION_NUMBER и удаляем из этих данных
        пробельные символы.
        '''
        domain_list = [line.strip()
                       for line in file_data[pointer:pointer + LINKS_PER_ITERATION_NUMBER]]

        '''
        Собираем ответ, добавляем строки одна за одной, в формате, данном в
        задании, IP определяем с помощью метода gethostbyname из библиотеки
        socket, в случае ошибки - IP являеться не определенным и вместо него
        записывается - unknown
        '''
        output = ''
        for domain in domain_list:
            try:
                output += domain + \
                    '\t\t\t\t[' + str(gethostbyname(domain)) + ']\n'
            except Exception:
                output += domain + '\t\t\t\t[' + 'unknown' + ']\n'
                pass

        # открываем файл результата
        result_file = open(RESULTS_FILE_PATH, 'a')
        # блокируем его, что бы не было одновременной дозаписи с другим потоком
        enter_lock(result_file)
        # записываем результат
        result_file.write(output)
        # снимаем lock
        exit_lock(result_file)
        # закрываем файл
        result_file.close()


if __name__ == '__main__':
    main()
