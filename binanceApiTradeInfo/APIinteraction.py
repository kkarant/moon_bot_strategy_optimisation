from datetime import datetime

import requests

from databaseInteraction.dbKlinesInfo import checkIfTableExist, dbAddKline
from supportingFunctions import decorator
from datetime import timedelta

from binance import Client

from binanceApiTradeInfo.prepForAPI import finalTransform, rightTimeDatesPrep, apiCallsOptimization
from supportingFunctions import isNull


def test_request_corect_price():
    responseSpot = requests.get(f"https://api.binance.com/api/v3/klines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseSpot.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Spot {date}"
          f"\n High = {responseSpot.json()[0][2]}"
          f"\n Low = {responseSpot.json()[0][3]}")
    responseFutures = requests.get(f"https://fapi.binance.com/fapi/v1/klines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseFutures.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Futures {date}"
          f"\nHigh = {responseFutures.json()[0][2]}"
          f"\n Low = {responseFutures.json()[0][3]}")
    responseMark = requests.get(f"https://fapi.binance.com/fapi/v1/markPriceKlines?symbol=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseMark.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Mark {date}"
          f"\nHigh = {responseMark.json()[0][2]}"
          f"\n Low = {responseMark.json()[0][3]}")
    responseIndex = requests.get(f"https://fapi.binance.com/fapi/v1/indexPriceKlines?pair=ZILUSDT&interval=1m&limit=10")
    date = datetime.fromtimestamp(responseIndex.json()[0][0] / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Index {date}"
          f"\nHigh = {responseIndex.json()[0][2]}"
          f"\n Low = {responseIndex.json()[0][3]}")


@decorator
def single_request(symbol, interval, startTime, endTime):
    response = 0
    responseList = {}
    try:
        response = requests.get(f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&"
                                f"startTime={startTime}&endTime={endTime}")
        # GET / fapi / v1 / klines     for futures reaload all db
        num = 0
        # if response.status_code == 200:
        if len(response.json()) >= 1:
            # print(response.json()[0])

            for el in response.json():
                responseList[num] = [el[0], el[2], el[3], el[6]]
                num = num + 1
        else:
            return 404

    except requests.exceptions.JSONDecodeError:
        if response is not None:
            if response.status_code == 404:
                print(f"Error in request for coin {symbol} with startTime = {startTime} endTime = {endTime}")
                return 404

    return responseList


def apiCallsManager(coinListTransformed):
    for coin in coinListTransformed:
        checkIfTableExist(coin)
    for coin in coinListTransformed:
        symbol = str(coin + "USDT")
        for el in coinListTransformed[coin]:
            startUnix = el[0]
            closeUnix = el[1]
            # print(symbol + " | " + str(startUnix) + " == " + str(closeUnix))
            response = single_request(symbol, "1m", startUnix, closeUnix)
            if response != 404:
                for num in response:
                    dbAddKline(symbol, response[num])
                print("Coin " + symbol + " downloaded")
            else:
                print("Coin " + symbol + " not downloaded, error " + str(response))


def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    client = Client(api_key, api_secret)
    print(client.get_system_status())
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
        # print(coinListTransformed.keys())
        # print(coinListTransformed.keys())
        # apiCallsManager(coinListTransformed)
    else:
        print('system maintenance')
        return 1
