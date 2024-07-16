import os
from logging import getLogger, basicConfig, INFO, FileHandler, Formatter

logger = getLogger()


# Функция для логирования. На вход принимает имя файла и имя папки)
def get_logs(filename, logs_folder_name):
    LOGS_PATH = f'{os.getcwd()}\\{logs_folder_name}'

    if not os.path.isdir(LOGS_PATH):
        os.mkdir(LOGS_PATH)

    FORMAT = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
    file_handler = FileHandler(filename=f'{LOGS_PATH}\\{filename}')
    formatter = Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    file_handler.setFormatter(formatter)
    basicConfig(level=INFO, format=FORMAT)
    logger.addHandler(file_handler)

    if len(os.listdir(LOGS_PATH)) > 3:
        os.remove(f'{LOGS_PATH}\\{sorted(os.listdir(LOGS_PATH))[0]}')
