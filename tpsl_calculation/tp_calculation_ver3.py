from collections import OrderedDict
from datetime import datetime, timedelta
import numpy as np
import pytz
from scipy.signal import chirp, find_peaks, peak_widths
import matplotlib.pyplot as plt

from db_interaction.dataReceiver import receiveData

utc = pytz.UTC


def tradeCheck(priceActionData, openTime, closeTime, dateFormat):
    tradeDur = (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat))
    openTimeDT = utc.localize(datetime.strptime(openTime, dateFormat))
    closeTimeDT = utc.localize(datetime.strptime(closeTime, dateFormat))
    if priceActionData is not None and len(priceActionData) >= 8:
        if (closeTimeDT - openTimeDT) >= timedelta(seconds=31):
            return True


def dataPrepStratLevel(stratName, stratData, BuySellPrice, stratTPSLdata, dateFormat, tradeNumList, colNames):
    tradeData = stratData[1][stratName]
    TPSLdata = stratTPSLdata[stratName]
    return tradeData, BuySellPrice, TPSLdata, tradeNumList, colNames, dateFormat, stratName


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


def tpsl_StratLevel_manager_v3(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    optimalTPSLstrat = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    stratList = ["(strategy <d180s1 M+>) "]
    for stratName in stratList:
        overallPeaks = tpsl_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata,
                                                                   dateFormat, tradeNumList, colNames))
        plotProfits(overallPeaks)
    return optimalTPSLstrat


def tpsl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, tradeNumList,
                            colNames, dateFormat, stratName):
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
                #print(peaks)
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
    print(overallPeaks)
    x = list(zip(*overallPeaks))[1]
    for el in x:
        if el not in timeProfitDict:
            timeProfitDict[el] = 0
    for el in x:
        for elem in overallPeaks:
            if elem[1] == el:
                timeProfitDict[el] = timeProfitDict[el] + elem[2]

    timeProfitOrdered = dict(sorted(timeProfitDict.items()))
    x = list(timeProfitOrdered.keys())
    y = list(timeProfitOrdered.values())
    divCoef = 10
    x_chunked = [x[i:i + divCoef] for i in range(0, len(x), divCoef)]
    y_chunked = [y[i:i + divCoef] for i in range(0, len(y), divCoef)]
    print(x_chunked)
    print(y_chunked)
    for index, el in enumerate(x_chunked):
        x_chunked[index] = int(index)*divCoef
    for index, el in enumerate(y_chunked):
        y_chunked[index] = sum(y_chunked[index])

    x_chunked_np = np.array([int(elm) for elm in x_chunked])
    y_chunked_np = np.array([float(ele) for ele in y_chunked])

    peaks, _ = find_peaks(y_chunked_np, height=0)
    print(peaks)
    plt.plot(x_chunked_np, y_chunked_np)
    plt.plot([el*divCoef for el in peaks], y_chunked_np[peaks], "x")
    plt.show()
