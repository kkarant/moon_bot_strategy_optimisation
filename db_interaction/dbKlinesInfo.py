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
    if checkIfTableIsEmpty(trade[1]["Coin "][:-1], cur, conn):
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


def toDate(cur, conn):
    lst = ['_1000xecusdt', '_1inchusdt', '_aaveusdt', '_adausdt', '_akrousdt', '_algousdt', '_aliceusdt',
           '_alphausdt', '_ancusdt', '_ankrusdt', '_antusdt', '_apeusdt', '_api3usdt', '_arpausdt', '_arusdt',
           '_atausdt', '_atomusdt', '_audiousdt', '_avaxusdt', '_axsusdt', '_bakeusdt', '_balusdt', '_bandusdt',
           '_batusdt', '_bchusdt', '_belusdt', '_blzusdt', '_bnxusdt', '_btsusdt', '_c98usdt', '_celousdt',
           '_celrusdt', '_chrusdt', '_chzusdt', '_compusdt', '_cotiusdt', '_crvusdt', '_ctkusdt', '_ctsiusdt',
           '_cvcusdt', '_dashusdt', '_dentusdt', '_dgbusdt', '_dodousdt', '_dotusdt', '_duskusdt', '_dydxusdt',
           '_egldusdt', '_enjusdt', '_ensusdt', '_eosusdt', '_etcusdt', '_ethusdt', '_filusdt', '_flowusdt',
           '_ftmusdt', '_fttusdt', '_galausdt', '_gmtusdt', '_grtusdt', '_hbarusdt', '_hntusdt', '_hotusdt',
           '_icpusdt', '_icxusdt', '_imxusdt', '_iostusdt', '_iotausdt', '_iotxusdt', '_kavausdt', '_kncusdt',
           '_ksmusdt', '_linausdt', '_linkusdt', '_litusdt', '_ltcusdt', '_lunausdt', '_manausdt', '_maskusdt',
           '_mkrusdt', '_mtlusdt', '_nearusdt', '_neousdt', '_nknusdt', '_oceanusdt', '_ognusdt', '_omgusdt',
           '_oneusdt', '_ontusdt', '_peopleusdt', '_qtumusdt', '_rayusdt', '_reefusdt', '_renusdt', '_rlcusdt',
           '_roseusdt', '_rsrusdt', '_runeusdt', '_rvnusdt', '_sandusdt', '_sfpusdt', '_sklusdt', '_snxusdt',
           '_solusdt', '_srmusdt', '_stmxusdt', '_storjusdt', '_sushiusdt', '_sxpusdt', '_thetausdt',
           '_tlmusdt', '_tomousdt', '_trbusdt', '_trxusdt', '_unfiusdt', '_uniusdt', '_vetusdt', '_wavesusdt',
           '_woousdt', '_xemusdt', '_xlmusdt', '_xmrusdt', '_xrpusdt', '_xtzusdt', '_zecusdt', '_zilusdt',
           '_zrxusdt']

    for el in lst:
        selectStr = f'''ALTER TABLE {el}
                        ALTER COLUMN klinevaluetime
                        TYPE timestamp without time zone
                        USING klinevaluetime::timestamp without time zone
                        '''

        cur.execute(selectStr)
        conn.commit()

        # selectStr = f'''UPDATE {el}
        #                        SET klinevaluetime=to_timestamp(klinevaluetime::bigint/1000);'''

        # cur.execute(selectStr)
        # conn.commit()
