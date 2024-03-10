import psycopg2
import config

try:
    # пытаемся подключиться к базе данных
    conn = psycopg2.connect(config.CON_URL)
    print('connection is ok')
except:
    # в случае сбоя подключения будет выведено сообщение в STDOUT
    print('Can`t establish connection to database')