import pandas as pd


# Функция для расчета необходимых метрик (которые в последствии будут отправлены в google sheets).
def do_data_agregation(data):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['created_at']).dt.date

    res = df.groupby(['date']).agg(all_tries=('created_at', 'count'), unique_users=('user_id', 'nunique'))
    res['mean_amount'] = round(res['all_tries'] / res['unique_users'], 1)
    res['correct_tries'] = df[df['is_correct'] == 1].groupby('date')['date'].count()
    res['in_percent'] = round(res['correct_tries'] * 100 / res['all_tries'], 1)

    columns_name = [
        'Общее кол-во попыток',
        'Кол-во уникальных пользователей',
        'Среднее кол-во попыток на одного пользователя',
        'Кол-во правильных попыток',
        'Кол-во правильных попыток в %'
    ]
    index_name = ['Дата']

    res.columns = columns_name
    res.index.names = index_name

    return res
