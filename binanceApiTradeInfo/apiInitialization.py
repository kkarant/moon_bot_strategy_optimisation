from collections import namedtuple
from datetime import datetime, timedelta
import itertools
from time import sleep

from binance import Client

# import BinanceAPIException, BinanceRequestException, NotImplementedException
from binanceApiTradeInfo.restAPIinteraction import apiCallsManager
from supportingFunctions import isNull


def clientInit():
    api_key = "InpLPIyMKvx0qNAeCFCCxBJczLxSU7snqfzZfGHlcriFUxlo2Sinr1JvVUKpChx1"
    api_secret = "CHmWXVTNhX4o0YL790vpKezFykXerCsCqvcrk3xiZCjzB1mCL7detkTUUpl0Hm7y"
    client = Client(api_key, api_secret)
    res = client.get_exchange_info()
    print(client.response.headers)
    return client


def rightTimeDatesPrep(stratData):
    dateFormat = "%Y-%m-%d %H:%M:%S"
    coinList = {}
    optimisedCoins = {}
    i = 0
    for stratName in stratData[1]:
        for trade in stratData[1][stratName]:
            coinName = str(trade[1]['Coin '][:-1])
            buyDateConverted = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
            closeDateConverted = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat)

            tmpBuyDate = buyDateConverted - timedelta(hours=2)
            tmpBuyDate = datetime.strptime(str(tmpBuyDate)[:-2] + "00", dateFormat)
            tmpCloseDate = closeDateConverted + timedelta(minutes=1) - timedelta(hours=2)
            tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)
            # print('Original buy date: ' + buyDateConverted.strftime(dateFormat)
            #       + ', converted to: ' + str(tmpBuyDate))
            # print('Original close date: ' + closeDateConverted.strftime(dateFormat)
            #       + ', converted to: ' + str(tmpCloseDate))

            optimisedCoins[i] = [coinName, tmpBuyDate, tmpCloseDate]
            if coinName not in coinList:
                coinList[coinName] = []

            i = i + 1
    return optimisedCoins, coinList


def apiCallsOptimization(optimisedCoins, coinList):
    m = 0
    for num in optimisedCoins:
        coinName = optimisedCoins[num][0]
        buyDateOptCoin = optimisedCoins[num][1]
        closeDateOptCoin = optimisedCoins[num][2]
        if not coinList[coinName]:
            coinList[coinName].append([buyDateOptCoin, closeDateOptCoin])
            continue
        elif len(coinList[coinName]) >= 1:
            for el in coinList[coinName]:
                buyDateCoinList = el[0]
                closeDateCoinList = el[1]

                # if closeDateCoinList > buyDateOptCoin:
                #     diff = closeDateCoinList - buyDateOptCoin
                #     m = 1
                # elif closeDateCoinList < buyDateOptCoin:
                #     diff = buyDateCoinList - closeDateOptCoin
                #     m = 2

                diff = buyDateCoinList - closeDateOptCoin
                m = 2
                if timedelta(hours=2) > diff > timedelta(seconds=1):
                    if m == 1:
                        el[1] = closeDateOptCoin
                        if buyDateOptCoin < buyDateCoinList:
                            el[0] = buyDateOptCoin
                    elif m == 2:
                        el[0] = buyDateOptCoin
                        if closeDateCoinList < closeDateOptCoin:
                            el[1] = closeDateOptCoin
                    elif m == 0:
                        print(f'Error with trade {num}')
                    # print(f'num of trade {num} For coin {coinName} diff = {diff} < 2 hour m =  {m}')
                    break
                elif diff > timedelta(hours=2, minutes=1):
                    if [optimisedCoins[num][1], optimisedCoins[num][2]] not in coinList[coinName]:
                        coinList[coinName].append([optimisedCoins[num][1], optimisedCoins[num][2]])
    # print(coinList)
    return coinList


def overlapCoinRange(range1, range2):
    Range = namedtuple('Range', ['start', 'end'])

    r1 = Range(start=range1[0], end=range1[1])
    r2 = Range(start=range2[0], end=range2[1])
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = int((earliest_end - latest_start).total_seconds() / 60)
    overlap = max(0, delta)
    if overlap == 0:
        return False  # ranges dont overlap
    elif overlap > 0:
        return True  # ranges overlap


def finalTransform(coinList):
    # for comb in itertools.combinations(coinList[coin], 2)
    coinListTransformed = {}
    coinListTransformed1 = {}
    for coin in coinList:
        coinListTransformed[coin] = []
        coinListTransformed1[coin] = []
    for coin in coinList:
        usedRanges = [0]
        i = 0
        if len(coinList[coin]) % 2 == 0:
            output = [coinList[coin][i:i + 2] for i in range(0, len(coinList[coin]), 2)]
            needToAddLastEl = False
        else:
            output = [coinList[coin][:-1][i:i + 2] for i in range(0, len(coinList[coin][:-1]), 2)]
            needToAddLastEl = True
        for comb in output:
            if overlapCoinRange(*comb):
                coinListTransformed[coin].append([min(comb[0][0], comb[1][0]), max(comb[0][1], comb[1][1])])
            else:
                coinListTransformed[coin].append(comb[0])
                coinListTransformed[coin].append(comb[1])

        if needToAddLastEl:
            coinListTransformed[coin].append(coinList[coin][-1])
    return coinListTransformed


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

        apiCallsManager(coinListTransformed) # 1000Xec
    else:
        print('system maintenance')
        return 1
