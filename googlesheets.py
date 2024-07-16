import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from logging import getLogger


logger = getLogger(__name__)


# Функция для отправки отчёта в Google Docs
def post_to_sheets(data, sheet_id, credentials_file_name):
    logger.info("Подключаемся к Google Sheets")

    scopes = ['https://spreadsheets.google.com/feeds',
              'https://www.googleapis.com/auth/spreadsheets',
              'https://www.googleapis.com/auth/drive.file',
              'https://www.googleapis.com/auth/drive'
              ]
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.getcwd() + f'\\{credentials_file_name}',
            scopes
        )
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key(sheet_id)
        sheet_info = sheet.get_worksheet(0)
        # Формируем название колонок
        col_name = [data.index.name] + data.columns.values.tolist()
        for index, row in data.iterrows():
            # Формируем строки
            rows = [pd.to_datetime(index).strftime('%d-%m-%Y')] + row.values.tolist()
            try:
                if not sheet_info.get_values():
                    sheet.sheet1.append_row(col_name)
                    sheet.sheet1.append_row(rows)
                    sheet.sheet1.format(f'A1:Z1', {'textFormat': {'bold': True}})
                else:
                    # Проверка по дате на "дублирование строк"
                    if rows[0] in sum(sheet_info.get_values(), []):
                        logger.warning(f'Данные за текущую дату %s были загружены ранее', rows[0])
                        continue
                    else:
                        sheet.sheet1.append_row(rows)

            except Exception as E:
                logger.error("Ошибка отправки: %s", E)
        logger.info('Загрузка завершена')
    except ReferenceError as R:
        logger.error("Ошибка подключения: %s", R)
    except Exception as e:
        logger.error("Ошибка подключения: %s", e)



