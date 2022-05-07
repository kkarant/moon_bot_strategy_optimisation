from datetime import datetime, timedelta

import psycopg2

from dataValidation.dataValidationModels import KlineData


def connectionDB():
    conn = psycopg2.connect(
        database='postgres',
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    return cur, conn


def checkIfTableExist(coin):
    conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    coinSuitable = '_' + coin + 'USDT'
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
    # print('_' + coin + 'USDT created')


def checkIfTableIsEmpty(coin):
    conn = psycopg2.connect(
        database="postgres",
        user='postgres',
        password='3sw3ar',
        host='localhost',
        port='5432'
    )
    cur = conn.cursor()
    coinSuitable = '_' + coin + 'USDT'
    cur.execute(f'''
    SELECT CASE
            WHEN EXISTS(SELECT * FROM {coinSuitable} LIMIT 1) THEN 1
            ELSE 0
        END''')
    conn.commit()
    res = cur.fetchall()
    cur.close()
    conn.close()
    return res[0][0]


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
    insertStr = f'''INSERT INTO {coinSuitable} (klinevalueHigh, klinevalueLow, klineValueTimeBuy, klineValueTimeClose)
                VALUES (%s ,%s, %s, %s)'''

    cur.execute(insertStr, (dataFromKlines[1], dataFromKlines[2],
                            dataFromKlines[0], dataFromKlines[3]))
    conn.commit()
    conn.close()


def dbReceiveKlines(optimisedName, startTime, endTime, cur, conn):
    charStartTime = str(startTime)
    charEndTime = str(endTime)

    receiveStr = f'''SELECT klinevaluehigh, klinevaluelow, klinevaluetimebuy, klinevaluetimeclose FROM {optimisedName} 
                    WHERE klinevaluetimebuy >= {charStartTime!r} AND klinevaluetimeclose <= {charEndTime!r}'''
    cur.execute(receiveStr)
    result = cur.fetchall()
    conn.commit()

    return result


def receiveDataFromDB(trade, dateFormat, cur, conn):
    if checkIfTableIsEmpty(trade[1]["Coin "][:-1]):
        returnList = []
        optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")

        tmpBuyDate = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat) - timedelta(hours=2)
        tmpCloseDate = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat) \
                       + timedelta(minutes=1) - timedelta(hours=2)
        tmpBuyDate = datetime.strptime(str(tmpBuyDate)[:-2] + "00", dateFormat)
        tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)

        startTime = int(datetime.timestamp(tmpBuyDate) * 1000)
        endTime = int(datetime.timestamp(tmpCloseDate) * 1000)
        # print(optimisedName + " start = " + str(startTime) + " end = " + str(endTime))
        # print(dbReceiveKlines(optimisedName, startTime, endTime))

        for el in dbReceiveKlines(optimisedName, startTime, endTime, cur, conn):
            returnList.append(KlineData(klinevaluehigh=el[0], klinevaluelow=el[1],
                                        klinevaluetimebuy=el[2], klinevaluetimeclose=el[3]))

        return returnList
