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


def connectioncloseDB(cur, conn):
    cur.close()
    conn.close()


def checkIfTableExist(coin, cur, conn):
    coinSuitable = '_' + coin
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {coinSuitable}(
                         id  SERIAL NOT NULL,
                         klineValue varchar(20) not null,
                         klineValueTime varchar(20) not null
                        )''')

    conn.commit()


def checkIfTableIsEmpty(coin, cur, conn):
    coinSuitable = '_' + coin + 'USDT'
    cur.execute(f'''
    SELECT CASE
            WHEN EXISTS(SELECT * FROM {coinSuitable} LIMIT 1) THEN 1
            ELSE 0
        END''')
    conn.commit()
    res = cur.fetchall()
    return res[0][0]


def dbAddKline(tabName, data, cur, conn):
    coinSuitable = '_' + tabName
    insertStr = f'''INSERT INTO {coinSuitable} (klinevalue, klineValueTime)
                VALUES (%s ,%s)'''

    cur.execute(insertStr, (data[0], data[1]))
    conn.commit()


def dbReceiveKlines(optimisedName, startTime, endTime, cur, conn):
    charStartTime = str(startTime)
    charEndTime = str(endTime)

    receiveStr = f'''SELECT klinevalue, klineValueTime FROM {optimisedName} 
                    WHERE klineValueTime BETWEEN {charStartTime!r} AND {charEndTime!r}'''
    cur.execute(receiveStr)
    result = cur.fetchall()
    conn.commit()

    return result


def receiveDataFromDB(trade, dateFormat, cur, conn):
    if checkIfTableIsEmpty(trade[1]["Coin "][:-1], cur, conn):
        returnList = []
        optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")

        tmpBuyDate = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
        tmpCloseDate = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat) + timedelta(minutes=1)
        tmpBuyDate = datetime.strptime(str(tmpBuyDate)[:-2] + "00", dateFormat)
        tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)

        startTime = int(datetime.timestamp(tmpBuyDate) * 1000)
        endTime = int(datetime.timestamp(tmpCloseDate) * 1000)
        # print(optimisedName + " start = " + str(startTime) + " end = " + str(endTime))
        # print(dbReceiveKlines(optimisedName, startTime, endTime))

        for el in dbReceiveKlines(optimisedName, startTime, endTime, cur, conn):
            returnList.append([el[0], el[1]])

        return returnList


def checkIfRowsExist(tabName, data, cur, conn):
    coinSuitable = '_' + tabName
    selectStr = f'''Select klinevalue, klinevaluetime select from {coinSuitable} where klineValueTime={str(data[1])!r}'''

    cur.execute(selectStr)
    result = cur.fetchall()
    conn.commit()
    if result == []:
        return False
    else:
        return True
