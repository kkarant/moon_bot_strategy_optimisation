import psycopg2


def dbInit(optimisedCoins):
    conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    for coin in optimisedCoins:
        coinSuitable = '_' + coin
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {coinSuitable}(
                 id  SERIAL NOT NULL,
                 klineValueHigh varchar(20) not null,
                 klineValueLow varchar(20) not null,
                 klineValueTimeBuy varchar(20) not null,
                 klineValueTimeClose varchar(20) not null
                )''')
        conn.commit()
    cur.close()
    conn.close()


def dbAddKline(tabName, dataFromKlines):
    conn = psycopg2.connect(
        database='postgres',
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    coinSuitable = '_' + tabName
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {coinSuitable}(
                     id  SERIAL NOT NULL,
                     klineValueHigh varchar(20) not null,
                     klineValueLow varchar(20) not null,
                     klineValueTimeBuy varchar(20) not null,
                     klineValueTimeClose varchar(20) not null
                    )''')
    conn.commit()
    insertStr = f'''INSERT INTO {coinSuitable} (klinevalueHigh, klinevalueLow, klineValueTimeBuy, klineValueTimeClose)
                VALUES (%s ,%s, %s, %s)'''

    cur.execute(insertStr, (dataFromKlines[0], dataFromKlines[1],
                            dataFromKlines[2], dataFromKlines[3]))
    conn.commit()
    conn.close()
