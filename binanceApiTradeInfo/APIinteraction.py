import time
from datetime import datetime

import requests

from databaseInteraction.dbKlinesInfo import checkIfTableExist, dbAddKline
from supportingFunctions import decorator
from datetime import timedelta

from binance import Client

from binanceApiTradeInfo.prepForAPI import finalTransform, rightTimeDatesPrep, apiCallsOptimization
from supportingFunctions import isNull


@decorator
def single_request(payload):
    try:
        response = requests.get(f"https://fapi.binance.com/fapi/v1/aggTrades", params=payload)
        if len(response.json()) >= 1:
            # print(response.json()[0])
            tradepriceAction = []
            tradepriceAction = select_price(response.json(), tradepriceAction)
            timeUsed = select_time(response.json())
            return tradepriceAction, timeUsed
        else:
            return 404

    except requests.exceptions.JSONDecodeError:
        print(f"Error")
        time.sleep(1)
        return 404


def select_price(responseJSON, tradepriceAction):
    for el in responseJSON:
        tradepriceAction.append([el["p"], el["T"]])

    return tradepriceAction


def select_time(responseJSON):
    timeUsed = []
    for el in responseJSON:
        timeUsed.append(el["T"])

    return timeUsed


def apiCallsManager(trade, allTimeRequested):
    dateFormat = "%Y-%m-%d %H:%M:%S"
    symbol = str(trade[1]['Coin '][:-1] + 'USDT')

    buyDateConverted = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
    closeDateConverted = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat)

    tmpBuyDate = datetime.strptime(str(buyDateConverted)[:-2] + "00", dateFormat)
    tmpCloseDate = closeDateConverted + timedelta(minutes=1)
    tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)

    startTime = int(datetime.timestamp(tmpBuyDate) * 1000)
    endTime = int(datetime.timestamp(tmpCloseDate) * 1000)

    checkIfTableExist(symbol)

    payload = {'symbol': symbol, 'startTime': startTime, 'endTime': endTime}

    response, timeUsed = single_request(payload)
    if response != 404:
        if all(item in allTimeRequested[symbol] for item in timeUsed):
            print("Coin " + symbol + " already downloaded")
        else:
            listOfNewRows = []
            tl = list(set(timeUsed) - set(allTimeRequested[symbol]))  # get elements which are in temp1 but not in temp2
            for elR in response:
                if elR[1] in tl:
                    listOfNewRows.append(elR)
            for elR in response:
                dbAddKline(symbol, elR)
                print("Coin " + symbol + " downloaded")
            for tme in tl:
                allTimeRequested[symbol].append(tme)
            return allTimeRequested
    else:
        print("Coin " + symbol + " not downloaded, error " + str(response))


def apiToDatabase(stratData, client):
    # stratData -> 1 -> stratName -> iterate over trades -> 1 -> BuyDate \ CloseDate

    if client.get_system_status()["status"] == 0 and not isNull(stratData[1]):
        allTimeRequested = {}
        for stratName in stratData[1]:
            for trade in stratData[1][stratName]:
                if str(trade[1]['Coin '][:-1] + 'USDT') not in allTimeRequested.keys():
                    allTimeRequested[str(trade[1]['Coin '][:-1] + 'USDT')] = []
                allTimeRequested = apiCallsManager(trade, allTimeRequested)

    else:
        print('system maintenance')
        return 1


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
