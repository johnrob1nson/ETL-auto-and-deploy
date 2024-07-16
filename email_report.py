import os
from datetime import timedelta
import re
import smtplib
import ssl
from email.message import EmailMessage
from logging import getLogger
import pandas as pd

logger = getLogger(__name__)

class Email:
    def __init__(self, smtp_email, port, your_email, password):
        self.smtp_email = smtp_email
        self.port = port
        self.your_email = your_email
        self.password = password


    # Функция формирует диапазон дат, за которые планируется загрузить отчёт, а также проверяет, есть ли в логах Error,
    @staticmethod
    def check_api_error(start, end, folder_name):
        RANGE_DATE = pd.date_range(start.date() + timedelta(days=1), end.date() + timedelta(days=1)).strftime(
            '%Y-%m-%d').tolist() #прибавляем 1 день т.к. отчёт берется за предыдущий день, а логи за текущий.
        LOGS_PATH = f'{os.getcwd()}\\{folder_name}'
        lst_dir = os.listdir(LOGS_PATH)
        for file in lst_dir:
            if re.search(r'\d{4}-\d{2}-\d{2}', file).group() in RANGE_DATE:
                date_report = ', '.join(RANGE_DATE)
                result_msg = True
                with open(f'{LOGS_PATH}\\{file}') as fl:
                    if 'ERROR' in fl.read():
                        result_msg = False

                return date_report, result_msg


    def send_email(self, subject, body, recipient_email, date_report, result_msg):
        try:
            logger.info("Отправка сообщения %s", recipient_email)
        # Создание защищенного соединения SSL
            self.context = ssl.create_default_context()
            self.smtp_server = smtplib.SMTP_SSL(self.smtp_email, self.port, context=self.context)
            self.smtp_server.login(self.your_email, self.password)
            msg = EmailMessage()
            if result_msg:
                result_msg = 'успешно'
            else:
                result_msg = 'с ошибкой'
            msg.set_content(body.format(date_report=date_report, result_msg=result_msg))
            msg['Subject'] = subject
            msg['From'] = self.your_email
            msg['To'] = recipient_email
            self.smtp_server.send_message(msg=msg)
            logger.info('Сообщение отправлено успешно')
        except Exception as e:
            logger.error("Ошибка отправки")



