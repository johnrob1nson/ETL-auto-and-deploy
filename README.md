# ETL-пайплайн, деплой и автоматизация для обучающей платформы
## Описание задачи

Задача - написать скрипт, в котором:

+ Будет происходить обращение к API для получения данных
+ Данные будут обрабатываться и готовиться к загрузке в базу данных
+ Обработанные данные будут загружаться в удаленную базу PostgreSQL
+ Добавить код, который в конце будет агрегировать данные за день (например, сколько попыток было совершено; сколько успешных попыток было из всех совершенных; количество уникальных юзеров и.т.п.)
+ Во время обработки будет сохраняться лог работы скрипта с отлавливанием всех ошибок и выводом промежуточных стадий (например, скачивание началось / скачивание завершилось / заполнение базы началось и т.д., с трекингом времени). Лог нужно сохранять в текстовый файл. Файл нужно именовать в соответствии с текущей датой. Если в папке с логами уже есть другие логи - их необходимо удалять, оставляем только логи за последние 3 дня.
+ Настраиваем email-оповещение на почту об успешной (или нет) выполенной выгрузке данных.
+ Развертываем наш скрипт на удаленном сервере
+ Атоматизируем скрипт на ежедневную работу
+ Развертываем Metabase удаленно
## Разбор решения
### 1. Файл logs.py для настройки логов. Функция get_logs создает папку для логов, файл с текущей датой логов, а также оставляет только данные за поледние 3 дня.
На вход принимает имя файла(текущая дата) и путь и имя директории, куда хотим сохранить логи.  
![image](https://github.com/user-attachments/assets/27bfc288-b2f8-481b-a6f8-edf0867ea05a)


### 2. Файл api.py - служит для получения API, а также для подготовки данных к выгрузке.

#### Пример ответа от API:
</p><pre>
[
    {
        "lti_user_id": "3583bf109f8b458e13ae1ac9d85c396a",
        "passback_params": "{'oauth_consumer_key': '', 'lis_result_sourcedid': 'course-v1:SF+DST-3.0+28FEB2021:lms.sf.ru-ca3ecf8e5f284c329eb7bd529e1a9f7e:3583bf109f8b458e13ae1ac9d85c396a', 'lis_outcome_service_url': 'https://lms.sf.ru/courses/course-v1:sf+DST-3.0+28FEB2021/xblock/block-v1:sf+DST-3.0+28FEB2021+type@lti+block@ca3ecf8e5f284c329eb7bd529e1a9f7e/handler_noauth/grade_handler'}",
        "is_correct": null,
        "attempt_type": "run",
        "created_at": "2023-05-31 09:16:11.313646"
    },
    {
        "lti_user_id": "ab6ddeb7654ab35d44434d8db629bd01",
        "passback_params": "{'oauth_consumer_key': '', 'lis_result_sourcedid': 'course-v1:sf+DSPR-2.0+14JULY2021:lms.sf.ru-0cf38fe58c764865bae254da886e119d:ab6ddeb7654ab35d44434d8db629bd01', 'lis_outcome_service_url': 'https://lms.sf.ru/courses/course-v1:sf+DSPR-2.0+14JULY2021/xblock/block-v1:sf+DSPR-2.0+14JULY2021+type@lti+block@0cf38fe58c764865bae254da886e119d/handler_noauth/grade_handler'}",
        "is_correct": null,
        "attempt_type": "run",
        "created_at": "2023-05-31 09:16:30.117858"
    }
]
</code></pre><p> 
  
#### Структура базы данных:
+ user_id - строковый айди пользователя
+ oauth_consumer_key - уникальный токен клиента
+ lis_result_sourcedid - ссылка на блок, в котором находится задача в ЛМС
+ lis_outcome_service_url - URL адрес в ЛМС, куда мы шлем оценку
+ is_correct - была ли попытка верной (null, если это run)
+ attempt_type - ран или сабмит
+ created_at - дата и время попытки

#### Результат:
</p><pre>
[
    {
      'user_id': '4fb333223f59678d2ab82066b74be16a', 
      'oauth_consumer_key': '', 
      'lis_result_sourcedid': 'course-v1:SkillFactory+SQL2.0+31AUG2020:lms.skillfactory.ru-a7402acc9e67474b8a2fe6242b908c33:4fb333223f59678d2ab82066b74be16a', 
      'lis_outcome_service_url': 'https://lms.skillfactory.ru/courses/course-v1:SkillFactory+SQL2.0+31AUG2020/xblock/block-v1:SkillFactory+SQL2.0+31AUG2020+type@lti+block@a7402acc9e67474b8a2fe6242b908c33/handler_noauth/grade_handler', 
      'is_correct': None, 
      'attempt_type': 'run', 
      'created_at': '2024-07-17 22:04:09.057570'
    }, 
    {
      'user_id': '907a94cbadcebd95f8c84d5d10fd6d42', 
      'oauth_consumer_key': '', 
      'lis_result_sourcedid': 'course-v1:SkillFactory+FPW-2.0+27AUG2020:lms.skillfactory.ru-84449de2949d4e78a057611a86d2dfcb:907a94cbadcebd95f8c84d5d10fd6d42', 
      'lis_outcome_service_url': 'https://lms.skillfactory.ru/courses/course-v1:SkillFactory+FPW-2.0+27AUG2020/xblock/block-v1:SkillFactory+FPW-2.0+27AUG2020+type@lti+block@84449de2949d4e78a057611a86d2dfcb/handler_noauth/grade_handler', 
      'is_correct': None, 
      'attempt_type': 'run', 
      'created_at': '2024-07-17 22:04:27.435008'
    }
]
</code></pre><p>

### 3. Файл Database_psql.py. Class PGDatabase и метод send_to_sql служат для подключения к базе данных PostgreSQL

#### !!! Важно !!! Перед тем как запускать данный скрипт, базу данных нужно предварительно развернуть на удаленном сервере. DDL для создания таблицы
</p><pre>
CREATE TABLE public.url (
	user_id varchar(50) NULL,
	oauth_consumer_key bpchar(100) NULL,
	lis_result_sourcedid bpchar(200) NULL,
	lis_outcome_service_url text NULL,
	is_correct int2 NULL,
	attempt_type varchar(50) NULL,
	created_at varchar(50) NULL,
	CONSTRAINT url_unique UNIQUE (user_id, oauth_consumer_key, lis_result_sourcedid, lis_outcome_service_url, is_correct, attempt_type, created_at)
);
</code></pre><p>
  
#### Результат:
![image](https://github.com/user-attachments/assets/5f0c84b9-ba40-47aa-82e9-7a6b04718c56)

  
### 4. Файл data_aggregation.py служит для агрегации данных и расчета метрик (для последующей отправки в Google Sheets)
Получает данные из API и возвращает датафрейм Pandas.
### 5. Файл post_to_sheets.py служит для отправки посчитанных метрик в Google Sheets
На вход принимает датафрейм Pandas (из пункта 4), id-таблицы GoogleSheets и предварительно сохраненный файл с credentials.json с ключами. 
Подробно, как получить ключи, можно изучить здесь: https://hands-on.cloud/python-google-sheets-api/?utm_content=cmp-true#google_vignette
#### Результат:
![image](https://github.com/user-attachments/assets/9a03576e-e04e-414c-9e66-188617de3913)

### 6. Файл email-report. в class Email служит для отправки email о результатах проделанной работы. Принимает smtp-email, порт, email (с которого планируется отправка писем), пароль от почты)  
##### Метод **check_api_error**: 
+ формирует диапазон дат, за который загружается отчёт и возвращает их
+ проверяет в текущем файле с логами наличие Error и возвращает True/Fasle(возвращает True, если есть и False, если нет) 

##### Метод **send_email** Отправляет письмо. 
На вход принимает: Заголовок письма; тело письма; email получателя; даты (из check_api_error), за которые делаем отчёт; True/False (есть ли ошибка или нет; также из check_api_error)
#### Результат:
![image](https://github.com/user-attachments/assets/fd9778bf-c15d-4093-a7d4-337b8aa61026)

## Настройка сервера (У меня Ubuntu 22.04.4 LTS)
### Необходимые программы для запуска скрипта 
+ pip 22.0.2
+ Python version >= 3.10
+ PSQL version 14.12 (руководство по установке https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart-ru)
+ Docker version 27.0.3 (руководство по установке https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)
+ Metabase (руководство по установке образа https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker)
+ Nginx (руководство по установке https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04)

### Подготовка среды
</p><pre>
git clone https://github.com/johnrob1nson/ETL-auto-and-deploy
cd ETL-auto-and-deploy/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
</code></pre><p>

## Запуск скрипта
#### !!! Важно !!! Перед тем как запускать данный скрипт в файле config.ini нужно добавить свои данные. 
</p><pre>
python3 run.py
</code></pre><p>

#### Результат:

![image](https://github.com/user-attachments/assets/a3e1d38b-c1ff-44b4-b76d-9eb398478819)


## Автоматизация
</p><pre>
EDITOR=nano crontab -e
</code></pre><p>

01 07 * * * периодичность * * * * * (~ каждый день в 7 часов 1 минуту)  ;  путь до интерпретатора  ;  путь до исполняемого файла
  
![image](https://github.com/user-attachments/assets/dc9935e7-d604-43b1-a48b-107b1809c196)

## Запуск Metabase
</p><pre>
cd etc/nginx
nano nginx.conf
</code></pre><p>
  
#### Вставляем в открытый файл код (место 3002 прописываем имя порта, которое указали при установки Metabase container ):
</p><pre>  
server {
        listen 3002;
        location / {
                proxy_pass http://127.0.0.1:3002;
        }
}
</code></pre><p>
  
![image](https://github.com/user-attachments/assets/53c2281b-4283-4075-92a8-0f0378acd442)

#### Переходим по адресу IP сервера:3002 и работаем с Metabase. (При запуске и регистрации, подключение можно настроить по SSH)

#### Результат:
![image](https://github.com/user-attachments/assets/fc10a855-3dcd-415f-a84a-54b4ac08c2c7)


