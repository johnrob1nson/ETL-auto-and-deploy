from datetime import time, datetime, timedelta, date
import os
import configparser
from logs import get_logs
from api import get_api
from database_psql import PGDatabase
from data_aggregation import do_data_agregation
from googlesheets import post_to_sheets
from email_report import Email
import pandas as pd

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

dir_name = os.path.dirname(__file__)
config = configparser.ConfigParser(interpolation=None)
config.read(os.path.join(dir_name, 'config.ini'), encoding='UTF-8')

LOGS = config['Logs']
PARAMS = config['Params']
DATABASE = config['Database']
SHEET = config['Google_Sheets']
EMAIL = config['Email']

name_file = f'{date.today()}.log'

# День (дни), данные за которые планируется загружать и обрабатывать
START = datetime.combine(datetime.now() - timedelta(days=1), time.min)
END = datetime.combine(datetime.now() - timedelta(days=1), time.max)

# Запускаем логирование
get_logs(name_file, LOGS['logs_path'])

if __name__ == '__main__':
    # Получаем данные по API
    data_api = get_api(PARAMS['client'], PARAMS['client_key'], PARAMS['api_url'], start=START, end=END)
    # Отправка данных в sql
    db = PGDatabase(
        database=DATABASE['database'],
        user=DATABASE['user'],
        password=DATABASE['password'],
        host=DATABASE['host'],
        port=DATABASE['port'],
    )
    db.send_to_sql(data_api)
    # Анализ данных
    df = do_data_agregation(data_api)
    # Отправка данных в Google Sheets
    post_to_sheets(df, SHEET['sheet_id'], SHEET['credential_path'])
    # Отправка сообщения на почту
    em = Email(EMAIL['smtp_email'], EMAIL['port'], EMAIL['your_email'], EMAIL['password'])
    check_result = em.check_api_error(START, END, LOGS['logs_path'])
    em.send_email(EMAIL['subject'], EMAIL['body'], EMAIL['recipient_email'], check_result[0], check_result[1])
