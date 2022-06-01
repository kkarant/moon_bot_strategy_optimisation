from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy.signal import find_peaks

utc = pytz.UTC


def tradeDataPrep(trade, colNames, indexDict, BuySellPrice):
    overallTradeNum = trade[0]
    coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
    indexTrade = indexDict[coin]  # num of trade in TPSLdata dict TPSLdata->coin-> indexTrade
    openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
    closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
    openPrice = BuySellPrice.loc[overallTradeNum, 'BuyPrice ']
    closePrice = BuySellPrice.loc[overallTradeNum, 'SellPrice ']
    profit = trade[1][colNames.index('Profit ')]  # profit
    return coin, indexTrade, openTime, closeTime, openPrice, closePrice, profit


def tradeCheck(priceActionData, openTime, closeTime, dateFormat):
    openTimeDT = utc.localize(datetime.strptime(openTime, dateFormat))
    closeTimeDT = utc.localize(datetime.strptime(closeTime, dateFormat))
    if priceActionData is not None and len(priceActionData) >= 8:
        if (closeTimeDT - openTimeDT) >= timedelta(seconds=31):
            return True


def tp_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, colNames, dateFormat):
    overallPeaks = []
    indexDict = {}
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    numOfTradesWithpeaks = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        coin, indexTrade, openTime, closeTime, openPrice, closePrice, profit = \
            tradeDataPrep(trade, colNames, indexDict, BuySellPrice)

        if tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat):
            numOfNormalTrades += 1
            peaks = extremumsParser(TPSLdata[coin][indexTrade], openPrice)
            if len(peaks) > 0:
                peaks = extremumsNormalise(peaks)
                peaks = percentApply(peaks, openPrice)
                peaks = rangesLower(peaks)
                # print(peaks)
            if len(peaks) > 0:
                numOfTradesWithpeaks += 1
                for el in peaks:
                    overallPeaks.append(el)
        indexDict[coin] = indexDict[coin] + 1
    print(f"{int(numOfTradesWithpeaks / len(tradeData) * 100)} % of trades have peaks")
    return overallPeaks


def extremumsParser(priceActionData, openPrice):
    peaksValues = []
    priceData = np.array([float(elem[0]) for elem in priceActionData])

    dist = len(priceData) / 8

    peaks, _ = find_peaks(priceData, height=openPrice, distance=dist, width=1)
    # print(peaks)
    # plt.plot(priceData)
    # plt.plot(openPrice, "--", color="gray")
    # plt.plot(peaks, priceData[peaks], "x")
    # plt.show()
    if len(peaks) > 0:
        for elem in peaks:
            # profit = (float(priceActionData[elem][0]) - float(openPrice)) / float(openPrice) * 100 * 20
            peaksValues.append(priceActionData[elem])
    return peaksValues


def extremumsNormalise(peaks):
    mode = 0
    finalPeaks = []
    while mode != 1:
        biggestEl = sorted(peaks, key=lambda a: a[0], reverse=True)[0]
        index = peaks.index(biggestEl)
        if len(peaks) == 1:
            mode = 1
            for el in peaks:
                finalPeaks.append(el)
        elif index == 0:
            mode = 3
            finalPeaks.append(biggestEl)
            del peaks[index]
        elif index > 0 or index < len(peaks) - 1:
            mode = 4
            finalPeaks.append(biggestEl)
            del peaks[0:index]
        elif index == len(peaks) - 1:
            mode = 5
            finalPeaks = [sum([float(element[0]) for element in peaks]) / len(peaks)]
    result = []
    [result.append(x) for x in finalPeaks if x not in result]
    # result = sorted(result, key=lambda a: a[0], reverse=True)[:3]
    return result


def percentApply(peaks, openPrice):
    if len(peaks) > 0:
        for elem in peaks:
            profit = (float(elem[0]) - float(openPrice)) / float(openPrice) * 100 * 20
            elem.append(round(profit, 2))
    return peaks


def rangesLower(peaks):
    for index, el in enumerate(peaks):
        if float(el[2]) <= 3.5:
            del peaks[index]
    for index, el in enumerate(peaks):
        if float(el[2]) <= 3.5:
            del peaks[index]
    for index, el in enumerate(peaks):
        if float(el[2]) <= 3.5:
            del peaks[index]
    return peaks


def plotProfits(overallPeaks):
    timeProfitDict = {}
    numOfEl = {}
    x = list(zip(*overallPeaks))[1]
    for el in x:
        if el not in timeProfitDict:
            numOfEl[el] = 0
            timeProfitDict[el] = 0
    for el in x:
        for elem in overallPeaks:
            if elem[1] == el:
                numOfEl[el] = numOfEl[el] + 1
                timeProfitDict[el] = timeProfitDict[el] + elem[2]

    timeProfitOrdered = dict(sorted(timeProfitDict.items()))
    numOfElSorted = dict(sorted(numOfEl.items()))

    x = list(timeProfitOrdered.keys())
    y = list(timeProfitOrdered.values())
    numOfElSorted_values = list(numOfElSorted.values())

    divCoef = 10
    x_chunked = [x[i:i + divCoef] for i in range(0, len(x), divCoef)]
    y_chunked = [y[i:i + divCoef] for i in range(0, len(y), divCoef)]
    numOfElSorted_chunked = [sum(numOfElSorted_values[i:i + divCoef])
                             for i in range(0, len(numOfElSorted_values), divCoef)]

    # y_chunked = [float(a) / int(b) for a in y_chunked_pre for b in numOfElSorted_chunked if int(b) > 0]
    for index, el in enumerate(x_chunked):
        x_chunked[index] = int(index) * divCoef
    for index, el in enumerate(y_chunked):
        y_chunked[index] = sum(y_chunked[index]) / numOfElSorted_chunked[index]

    x_chunked_np = np.array([int(elm) for elm in x_chunked])
    y_chunked_np = np.array([float(ele) for ele in y_chunked])

    peaks, _ = find_peaks(y_chunked_np, height=0)
    plt.plot(x_chunked_np, y_chunked_np)
    plt.plot([el * divCoef for el in peaks], y_chunked_np[peaks], "x")
    plt.show()
