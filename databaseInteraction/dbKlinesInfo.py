import psycopg2


def dbIit():
    conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()
    sql = '''CREATE TABLE klinesData(
     id  SERIAL NOT NULL,
     coin varchar(20) not null,
     klineValues varchar(20) not null
    )'''
