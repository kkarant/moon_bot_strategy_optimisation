from datetime import datetime, timedelta

import numpy as np
import pytz
from scipy.signal import find_peaks

from API_DB_pipeline.db_interaction.dataReceiver import receiveData

utc = pytz.UTC


def tradeCheck(priceActionData, openTime, closeTime, dateFormat):
    tradeDur = (datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat))
    openTimeDT = utc.localize(datetime.strptime(openTime, dateFormat))
    closeTimeDT = utc.localize(datetime.strptime(closeTime, dateFormat))
    if priceActionData is not None and len(priceActionData) >= 8:
        if (closeTimeDT - openTimeDT) >= timedelta(seconds=31):
            # if len(priceActionData) >= 1:
            #     lasttimedata = utc.localize(datetime.strptime(datetime.fromtimestamp(int(priceActionData[-1][1]) /
            #                                                                          1000).strftime(
            #         '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
            #     firsttimedata = utc.localize(datetime.strptime(datetime.fromtimestamp(int(priceActionData[0][1]) /
            #                                                                           1000).strftime(
            #         '%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
            #     dataDur = lasttimedata - firsttimedata
            #     # print(openTimeDT, closeTimeDT)
            #     # print(firsttimedata, lasttimedata)
            #
            #     if dataDur >= tradeDur:
            #         if firsttimedata <= openTimeDT and \
            #                 lasttimedata >= closeTimeDT:
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


def tpsl_StratLevel_manager_v2(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    optimalTPSLstrat = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    stratList = ["(strategy <d180s1 M+>) "]
    for stratName in stratList:
        tpsl_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata,
                                                    dateFormat, tradeNumList, colNames))
    return optimalTPSLstrat


def tpsl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, tradeNumList,
                            colNames, dateFormat, stratName):
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
                # print(peaks)
                peaks = extremumsNormalise(peaks)
                # print(peaks)
                ranges = extremumsRangeCalculation(peaks, openTime, closeTime, openPrice, dateFormat)
                # print(ranges)
                ranges = rangesOptimised(ranges)
                print("========================")
                print(ranges)
                ranges = rangesLower(ranges)
                print(ranges)
                if len(ranges) > 0:
                    numOfTradesWithpeaks += 1
            # threeMaxExtremumFinal = extremumsNormalise(threeMaxExtremumFinal)
            # extremumsRangeCalculation(threeMaxExtremumFinal, openTime, closeTime, dateFormat)

        indexDict[coin] = indexDict[coin] + 1
    print(f"{int(numOfTradesWithpeaks / len(tradeData)*100)} % of trades have peaks")


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


def extremumsRangeCalculation(peaks, openTime, closeTime, openPrice, dateFormat):
    ranges = []
    for index, el in enumerate(peaks):
        if index == 0:
            openRange = 0
        else:
            openRange = ranges[index - 1][1]

        if index < len(peaks) - 1:
            peaktime = datetime.strptime(datetime.utcfromtimestamp(int(el[1]) / 1000).strftime(dateFormat), dateFormat)
            nextpeaktime = datetime.strptime(datetime.utcfromtimestamp(int(peaks[index + 1][1])
                                                                       / 1000).strftime(dateFormat), dateFormat)
            rangeTime = ((nextpeaktime - peaktime) / 2)
            rangeTimeS = rangeTime.total_seconds() + openRange
        elif index == len(peaks) - 1:
            rangeTime = datetime.strptime(closeTime, dateFormat) - datetime.strptime(openTime, dateFormat)
            rangeTimeS = rangeTime.total_seconds()
        profit = (float(el[0]) - float(openPrice)) / float(openPrice) * 100 * 20
        ranges.append([int(openRange), int(rangeTimeS), el[0], round(profit, 2)])

    return ranges


def rangesOptimised(ranges):
    tradeLen = ranges[-1][1] - ranges[0][0]
    if len(ranges) > 1:
        for i in range(1, 5):
            for index, el in enumerate(ranges):
                averageP = sum([element[3] for element in ranges]) / len(ranges)
                if el[1] - el[0] < tradeLen / 10 and el[3] < averageP:
                    if index < len(ranges) - 2:
                        newEl = [min(ranges[index][0], ranges[index + 1][0]),
                                 max(ranges[index][1], ranges[index + 1][1]),
                                 round((float(ranges[index][2]) + float(ranges[index + 1][2])) / 2,
                                       len(str(ranges[index][2]))),
                                 round((float(ranges[index][3]) + float(ranges[index + 1][3])) / 2, 2)]
                        ranges[index] = newEl
                        del ranges[index + 1]
                    elif index == len(ranges) - 1:
                        newEl = [min(ranges[index][0], ranges[index - 1][0]),
                                 max(ranges[index][1], ranges[index - 1][1]),
                                 round((float(ranges[index][2]) + float(ranges[index - 1][2])) / 2,
                                       len(str(ranges[index][2]))),
                                 round((float(ranges[index][3]) + float(ranges[index - 1][3])) / 2, 2)]
                        ranges[index] = newEl
                        del ranges[index - 1]

    return ranges


def rangesLower(ranges):
    for index, el in enumerate(ranges):
        if float(el[3]) <= 2:
            del ranges[index]
    for index, el in enumerate(ranges):
        if float(el[3]) <= 2:
            del ranges[index]
    return ranges


def rangesLowerMethod1(ranges, lowestPercent):
    index = ranges.index(lowestPercent)
    if index < len(ranges) - 2:
        newEl = [min(ranges[index][0], ranges[index + 1][0]),
                 max(ranges[index][1], ranges[index + 1][1]),
                 round((float(ranges[index][2]) + float(ranges[index + 1][2])) / 2,
                       len(str(ranges[index][2]))),
                 round((float(ranges[index][3]) + float(ranges[index + 1][3])) / 2, 2)]
        ranges[index] = newEl
        del ranges[index + 1]
    elif index == len(ranges) - 1:
        newEl = [min(ranges[index][0], ranges[index - 1][0]),
                 max(ranges[index][1], ranges[index - 1][1]),
                 round((float(ranges[index][2]) + float(ranges[index - 1][2])) / 2,
                       len(str(ranges[index][2]))),
                 round((float(ranges[index][3]) + float(ranges[index - 1][3])) / 2, 2)]
    return ranges
