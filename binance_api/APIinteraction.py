import time
from datetime import datetime

import requests

from db_interaction.dbKlinesInfo import checkIfTableExist, dbAddKline, checkIfRowsExist, connectionDB, \
    connectioncloseDB
from data_validation.supportingFunctions import decorator
from datetime import timedelta

from data_validation.supportingFunctions import isNull
from db_interaction.rdsConnection import connectionDBrds, connectioncloseDBrds


@decorator
def single_request(payload):
    try:
        response = requests.get(f"https://fapi.binance.com/fapi/v1/aggTrades", params=payload)
        if len(response.json()) >= 1:
            # print(response.json()[0])
            tradepriceAction = []
            tradepriceAction = select_price(response.json(), tradepriceAction)
            return tradepriceAction
        else:
            print("err API")
            return 404

    except requests.exceptions.JSONDecodeError:
        print(f"Error")
        time.sleep(1)
        return 404


def select_price(responseJSON, tradepriceAction):
    for el in responseJSON:
        tradepriceAction.append([el["p"], el["T"]])

    return tradepriceAction


def apiCallsManager(trade, cur, conn):
    dateFormat = "%Y-%m-%d %H:%M:%S"
    symbol = str(trade[1]['Coin '][:-1] + 'USDT')

    buyDateConverted = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
    closeDateConverted = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat)

    tmpBuyDate = datetime.strptime(str(buyDateConverted)[:-2] + "00", dateFormat)
    tmpCloseDate = closeDateConverted + timedelta(minutes=1)
    tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)

    startTime = int(datetime.timestamp(tmpBuyDate) * 1000)
    endTime = int(datetime.timestamp(tmpCloseDate) * 1000)

    checkIfTableExist(symbol, cur, conn)

    payload = {'symbol': symbol, 'startTime': startTime, 'endTime': endTime}

    response = single_request(payload)
    if response != 404:
        for el in response:
            if checkIfRowsExist(symbol, el, cur, conn, dateFormat):
                pass
            else:
                dbAddKline(symbol, el, cur, conn, dateFormat)
                print("Sum new added new to db")
    else:
        print("Coin " + symbol + " not downloaded, error " + str(response))


def apiToDatabase(stratData):
    # stratData -> 1 -> stratName -> iterate over trades -> 1 -> BuyDate \ CloseDate
    cur, conn = connectionDBrds()
    # client.get_system_status()["status"] == 0 and
    if not isNull(stratData[1]):
        for stratName in stratData[1]:
            for trade in stratData[1][stratName]:
                print('trade number: ' + str(trade[0]))
                apiCallsManager(trade, cur, conn)

    else:
        print('system maintenance')
        return 1
    connectioncloseDBrds(cur, conn)


def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    # client = Client(api_key, api_secret)
    # print(client.get_system_status())
    # return client


def timeForCalls(coinList):
    allTime = timedelta(seconds=0)
    for coin in coinList:
        totalTime = timedelta(seconds=0)
        for el in coinList[coin]:
            totalTime = totalTime + el[1] - el[0]
        allTime = allTime + totalTime
        # print(f'For coin {coin} required time = {totalTime}')
    print(allTime)
