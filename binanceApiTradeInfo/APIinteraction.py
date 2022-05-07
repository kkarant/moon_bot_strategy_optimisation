from datetime import datetime

import requests

from databaseInteraction.dbKlinesInfo import checkIfTableExist, dbAddKline
from supportingFunctions import decorator
from datetime import timedelta

from binance import Client

from binanceApiTradeInfo.prepForAPI import finalTransform, rightTimeDatesPrep, apiCallsOptimization
from supportingFunctions import isNull


@decorator
def single_request(symbol, interval, startTime, endTime) -> dict:
    responseList = {}
    response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&"
                            f"startTime={startTime}&endTime={endTime}")
    # GET / fapi / v1 / klines     for futures reaload all db
    num = 0
    # if response.status_code == 200:
    print(response.json()[0])

    for el in response.json():
        responseList[num] = [el[0], el[2], el[3], el[6]]
        num = num + 1

    return responseList


def apiCallsManager(coinListTransformed):
    for coin in coinListTransformed:
        checkIfTableExist(coin)
    for coin in coinListTransformed:
        symbol = str(coin + "USDT")
        for el in coinListTransformed[coin]:
            startUnix = int(datetime.timestamp(el[0]) * 1000)
            closeUnix = int(datetime.timestamp(el[1]) * 1000)
            print(symbol + " | " + str(startUnix) + " == " + str(closeUnix))
            response = single_request(symbol, "1m", startUnix, closeUnix)
            for num in response:
                dbAddKline(symbol, response[num])


def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    client = Client(api_key, api_secret)
    res = client.get_exchange_info()
    print(client.response.headers)
    return client


def timeForCalls(coinList):
    allTime = timedelta(seconds=0)
    for coin in coinList:
        totalTime = timedelta(seconds=0)
        for el in coinList[coin]:
            totalTime = totalTime + el[1] - el[0]
        allTime = allTime + totalTime
        # print(f'For coin {coin} required time = {totalTime}')
    print(allTime)


def apiToDatabase(stratData, client):
    # stratData -> 1 -> stratName -> iterate over trades -> 1 -> BuyDate \ CloseDate

    if client.get_system_status()["status"] == 0 and not isNull(stratData[1]):
        coinListTransformed = finalTransform(apiCallsOptimization(*rightTimeDatesPrep(stratData)))
        timeForCalls(coinListTransformed)
        print(coinListTransformed.keys())

        apiCallsManager(coinListTransformed)  # 1000Xec
    else:
        print('system maintenance')
        return 1
