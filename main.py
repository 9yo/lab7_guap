import fcntl
import time
import socket

DOMAINS_FILE_PATH = 'domains'  # путь до файла с доменами
RESULTS_FILE_PATH = 'results'  # путь до файла с резульатом
POSITION_FILE_PATH = 'position'  # путь до файла с указателем
# сколько ссылок программа будет считывать из файла за раз
LINKS_PER_ITERATION_NUMBER = 3


def enter_lock(file):
    # устанавливает lock на файл, пытется захватить его в случае неудачи
    while True:
        try:
            fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as e:
            print('THE FILE IS LOCKED')
            time.sleep(0.005)
        else:
            return


def exit_lock(f):
    # снимает lock
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


def main():
    running = True

    while running:
        pointer = 0
        try:
            pointer_file = open(POSITION_FILE_PATH, 'r')
            enter_lock(pointer_file)
            # патаемся считать значение из файла pointer
            file_data = pointer_file.readlines()[0].strip()
            pointer = int(file_data)

            # записываем новое значение в файл pointer
            open(POSITION_FILE_PATH, 'w').write(
                str(pointer + LINKS_PER_ITERATION_NUMBER))

            exit_lock(pointer_file)

        except (IndexError, FileNotFoundError):
            pass

        # достаем нужный нам домен по указателю
        file_data = open(DOMAINS_FILE_PATH, 'r').readlines()
        if len(file_data) <= pointer + LINKS_PER_ITERATION_NUMBER:
            open(POSITION_FILE_PATH, 'w').write('0')
            running = False
        domain_list = [line.strip()
                       for line in file_data[pointer:pointer + LINKS_PER_ITERATION_NUMBER]]
        # print(pointer, pointer + LINKS_PER_ITERATION_NUMBER)
        print(domain_list)

        output = ''
        for domain in domain_list:
            try:
                output += domain + \
                    '\t\t\t\t[' + str(socket.gethostbyname(domain)) + ']\n'
            except socket.gaierror:
                output += domain + '\t\t\t\t[' + 'uknown' + ']\n'
                pass

        result_file = open(RESULTS_FILE_PATH, 'a')
        enter_lock(result_file)
        result_file.write(output)
        exit_lock(result_file)


if __name__ == '__main__':
    main()
