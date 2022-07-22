from collections import namedtuple
from datetime import timedelta, datetime

import pandas as pd


def unixToDateTime(unixVal):
    date = datetime.fromtimestamp(unixVal / 1000).strftime('%Y-%m-%d %H:%M:%S')
    dateObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return dateObj


def rightTimeDatesPrep(stratData):
    dateFormat = "%Y-%m-%d %H:%M:%S"
    coinList = {}
    optimisedCoins = {}
    i = 0
    #for stratName in stratData[1]:
    for trade in stratData[1]["(strategy <d180s1 M+>) "]:
            coinName = str(trade[1]['Coin '][:-1])
            buyDateConverted = datetime.strptime(trade[1]['BuyDate '][:-1], dateFormat)
            closeDateConverted = datetime.strptime(trade[1]['CloseDate '][:-1], dateFormat)

            tmpBuyDate = buyDateConverted - timedelta(hours=2)
            tmpBuyDate = datetime.strptime(str(tmpBuyDate)[:-2] + "00", dateFormat)
            tmpCloseDate = closeDateConverted + timedelta(minutes=1) - timedelta(hours=2)
            tmpCloseDate = datetime.strptime(str(tmpCloseDate)[:-2] + "00", dateFormat)
            startUnix = int(datetime.timestamp(tmpBuyDate) * 1000)
            closeUnix = int(datetime.timestamp(tmpCloseDate) * 1000)

            optimisedCoins[i] = [coinName, pd.Interval(startUnix, closeUnix)]
            if coinName not in coinList:
                coinList[coinName] = []

            i = i + 1
    return optimisedCoins, coinList


def apiCallsOptimization(optimisedCoins, coinList):
    m = 0
    for num in optimisedCoins:
        coinName = optimisedCoins[num][0]
        buyDateOptCoin = unixToDateTime(optimisedCoins[num][1].left)
        closeDateOptCoin = unixToDateTime(optimisedCoins[num][1].right)
        if not coinList[coinName]:
            coinList[coinName].append(optimisedCoins[num][1])
            continue
        elif len(coinList[coinName]) >= 1:
            for el in coinList[coinName]:
                buyDateCoinList = unixToDateTime(el.left)
                closeDateCoinList = unixToDateTime(el.right)
                diff = timedelta(hours=100)
                m = 2
                if optimisedCoins[num][1].overlaps(el):
                    coinList[coinName].remove(el)
                    coinList[coinName].append(pd.Interval(min(el.left, optimisedCoins[num][1].left),
                                                          max(el.right, optimisedCoins[num][1].right)))
                else:
                    diff = buyDateCoinList - closeDateOptCoin
                    if timedelta(minutes=15) >= diff > timedelta(seconds=1):
                        coinList[coinName].remove(el)
                        coinList[coinName].append(pd.Interval(min(el.left, optimisedCoins[num][1].left),
                                                              max(el.right, optimisedCoins[num][1].right)))
                        break
                    elif diff > timedelta(minutes=15):
                        if [optimisedCoins[num][1]] not in coinList[coinName]:
                            coinList[coinName].append(optimisedCoins[num][1])
    return coinList


def finalTransform(coinList):
    # for comb in itertools.combinations(coinList[coin], 2)
    coinListTransformed = {}
    coinListTransformed1 = {}
    for coin in coinList:
        coinListTransformed[coin] = []
        coinListTransformed1[coin] = []

    print(1)
    for i in range(0, 10):
        coinListTransformed, overlaps = overlappingDelete(coinList, coinListTransformed)
        print(overlaps)

    return coinListTransformed


def overlappingDelete(coinList, coinListTransformed):
    overlaps = 0
    for coin in coinList:
        if len(coinList[coin]) % 2 == 0:
            output = [coinList[coin][i:i + 2] for i in range(0, len(coinList[coin]), 2)]
            needToAddLastEl = False
        else:
            output = [coinList[coin][:-1][i:i + 2] for i in range(0, len(coinList[coin][:-1]), 2)]
            needToAddLastEl = True
        for comb in output:
            if comb[0].overlaps(comb[1]):
                coinListTransformed[coin].append([min(comb[0].left, comb[1].left), max(comb[0].right, comb[1].right)])
                overlaps = overlaps + 1
            else:
                coinListTransformed[coin].append(comb[0])
                coinListTransformed[coin].append(comb[1])

        if needToAddLastEl:
            coinListTransformed[coin].append(coinList[coin][-1])

    return coinListTransformed, overlaps
