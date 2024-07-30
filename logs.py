import os
import re
from logging import getLogger, basicConfig, INFO, FileHandler, Formatter
from datetime import date

dir_name = os.path.dirname(__file__)
logger = getLogger()


# Функция для логирования. На вход принимает имя файла и имя папки)
def get_logs(filename, logs_folder_name):
    logs_path = os.path.join(dir_name, logs_folder_name)

    if not os.path.isdir(logs_path):
        os.mkdir(logs_path)

    form = '%(asctime)s : %(name)s : %(levelname)s : %(message)s'
    file_handler = FileHandler(filename=os.path.join(logs_path, filename))
    formatter = Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    file_handler.setFormatter(formatter)
    basicConfig(level=INFO, format=form)
    logger.addHandler(file_handler)

    for file in os.listdir(logs_path):
        logs_date = re.search(r'\d{4}-\d{2}-\d{2}', file).group()
        if (date.today() - date.fromisoformat(logs_date)).days > 1:
            os.remove(os.path.join(logs_path, file))
