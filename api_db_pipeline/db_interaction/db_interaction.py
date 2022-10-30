from datetime import datetime, timedelta

import psycopg2
from flask import Flask


# from flask_sqlalchemy import SQLAlchemy


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
                         klineValueTime timestamp not null
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


def dbAddKline(tabName, data, cur, conn, dateFormat):
    coinSuitable = '_' + tabName
    insertStr = f'''INSERT INTO {coinSuitable} (klinevalue, klineValueTime)
                VALUES (%s ,%s)'''
    date = datetime.fromtimestamp(int(data[1]/1000)).strftime(dateFormat)
    cur.execute(insertStr, (data[0], str(date)))
    conn.commit()


def dbReceiveKlines(optimisedName, startTime, endTime, cur, conn):
    receiveStr = f'''SELECT klinevalue, klineValueTime FROM {optimisedName} 
                    WHERE klineValueTime >= TIMESTAMP %s AND klineValueTime <= TIMESTAMP %s'''
    cur.execute(receiveStr, (startTime, endTime))
    result = cur.fetchall()
    return result


def receiveDataFromDB(trade, dateFormat, cur, conn):
    if not checkIfTableIsEmpty(trade[1]["Coin "][:-1], cur, conn):
        return None
    returnList = []
    optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")

    tmpBuyDate = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
    tmpCloseDate = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat) + timedelta(minutes=1)

    for el in dbReceiveKlines(optimisedName, tmpBuyDate, tmpCloseDate, cur, conn):
        returnList.append([el[0], el[1]])

    return returnList


def checkIfRowsExist(tabName, data, cur, conn, dateFormat):
    coinSuitable = '_' + tabName
    date = datetime.fromtimestamp(int(data[1]/1000)).strftime(dateFormat)
    selectStr = f'''Select klinevalue, klinevaluetime from {coinSuitable} where 
                    klineValueTime={str(date)!r}'''

    cur.execute(selectStr)
    result = cur.fetchall()
    conn.commit()
    if not result:
        return False
    else:
        return True
