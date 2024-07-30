import ast
import requests
from collections import OrderedDict
from logging import getLogger

logger = getLogger(__name__)


# Функция получения API и его обработка. Принимает аргументы: время начала и конца
def get_api(client, client_key, api_url, start, end):
    logger.info("Подключаемся к API")
    params = {'client': client, 'client_key': client_key, 'start': start, 'end': end}
    logger.info("Скачиваем данные из %s", api_url)
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        logger.info('Скачивание завершено')

        df = []
        # Преобразуем данные под необходимый формат
        for row in data:
            format_data = OrderedDict()
            if row.get('passback_params'):
                unpack_json = dict(ast.literal_eval(str(row.get('passback_params'))))
            else:
                unpack_json = dict(
                    {'oauth_consumer_key': None, 'lis_result_sourcedid': None, 'lis_outcome_service_url': None})
            format_data['user_id'] = row.pop('lti_user_id')
            format_data['oauth_consumer_key'] = unpack_json.get('oauth_consumer_key')
            format_data['lis_result_sourcedid'] = unpack_json.get('lis_result_sourcedid')
            format_data['lis_outcome_service_url'] = unpack_json.get('lis_outcome_service_url')
            format_data['is_correct'] = row.get('is_correct')
            format_data['attempt_type'] = row.get('attempt_type')
            format_data['created_at'] = row.get('created_at')

            df.append(dict(format_data))

        logger.info('Обработка данных завершена')

        return df

    except requests.exceptions.RequestException as err:
        logger.error('Ошибка при загрузке данных %s', err)

    except Exception as err:
        logger.error('Ошибка скачивания %s', err)
