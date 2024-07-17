from logging import getLogger, INFO, ERROR
import psycopg2

logger = getLogger(__name__)


# Класс для работы с PostgreSQL. Метод send_to_sql служит для отправки данных в базу.
class PGDatabase:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PGDatabase, cls).__new__(cls)
        return cls.instance

    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        logger.info('Подключаемся к базе данных PostgreSQL "%s"', self.database)
        try:
            self.conn = psycopg2.connect(
                database=database,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            self.conn.autocommit = True
        except ConnectionError as CE:
            logger.error('Ошибка подключения %s', CE)
        except TypeError as TE:
            logger.error('Ошибка загрузки данных %s', TE)
        except UnicodeDecodeError as UE:
            logger.error('Ошибка подключения %s', UE)

    def send_to_sql(self, data):
        logger.info('Загружаем данные в базу данных "%s"', self.database)
        for row in data:
            placeholders = ', '.join(['%s'] * len(row))
            columns = ', '.join(row.keys())
            values = list(row.values())
            query = "INSERT INTO URL ( %s ) VALUES ( %s ) ON CONFLICT DO NOTHING" % (columns, placeholders)
            try:
                self.cursor.execute(query, values)
            except Exception as e:
                logger.error("Ошибка загрузки: %s", e)
                break
        logger.info('Загрузка завершена')
