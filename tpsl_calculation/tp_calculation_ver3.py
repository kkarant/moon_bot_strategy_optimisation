from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy.signal import find_peaks

from api_db_pipeline.db_interaction.db_interaction import dbReceiveKlines, connectionDB

utc = pytz.UTC


def tradeDataPrep(trade, colNames, dateFormat, BuySellPrice):
    coin = trade[1][colNames.index('Coin ')][:-1]  # coin name
    optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")
    openTime = trade[1][colNames.index('BuyDate ')][:-1]  # open time
    openTimeDT = datetime.strptime(openTime, dateFormat)
    closeTime = trade[1][colNames.index('CloseDate ')][:-1]  # close time
    closeTimeDT = datetime.strptime(closeTime, dateFormat)
    openPrice = BuySellPrice.loc[trade[0], 'BuyPrice ']
    closePrice = BuySellPrice.loc[trade[0], 'SellPrice ']
    profit = trade[1][colNames.index('Profit ')]  # profit
    return coin, openTimeDT, closeTimeDT, openPrice, closePrice, profit, optimisedName


def tradeCheck(priceActionData, openTimeDT, closeTimeDT):
    if priceActionData is not None and len(priceActionData) > 8:
        openTimePAD = priceActionData[0][1]
        closeTimePAD = priceActionData[-1][1]
        # print(f"==============================\n"
        #       f"openTimePAD = {openTimePAD},\n"
        #       f"openTimeDT = {openTimeDT},\n "
        #       f"closeTimePAD = {closeTimePAD}")
        if (closeTimeDT - openTimeDT) >= timedelta(seconds=15):
            if openTimePAD <= openTimeDT < closeTimePAD:
                return True


def unixToDatetime(unixString, dateFormat, localize):
    if localize:
        return utc.localize(datetime.strptime(datetime.fromtimestamp(int(unixString) / 1000.0)
                                              .strftime(dateFormat), dateFormat))
    else:
        return datetime.strptime(datetime.fromtimestamp(int(unixString) / 1000.0)
                                 .strftime(dateFormat), dateFormat)


def tp_TradeLevel_manager(tradeData, colNames, dateFormat, BuySellPrice):
    overallPeaks = []
    numOfTradesWithpeaks = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        coin, openTimeDT, closeTimeDT, openPrice, closePrice, profit, optimisedName = \
            tradeDataPrep(trade, colNames, dateFormat, BuySellPrice)
        optimisedName = str("_" + trade[1]["Coin "][:-1] + "USDT")
        priceActionData = dbReceiveKlines(optimisedName, openTimeDT, closeTimeDT, *connectionDB())

        if tradeCheck(priceActionData, openTimeDT, closeTimeDT):
            numOfNormalTrades += 1
            peaks = extremumsParser(priceActionData, openPrice)
            if len(peaks) > 0:
                peaks = extremumsNormalise(peaks)
                peaks = percentApply(peaks, openPrice)
                peaks = rangesLower(peaks)
            if len(peaks) > 0:
                numOfTradesWithpeaks += 1
                for el in peaks:
                    peakTime = el[1]
                    overallPeaks.append([el[0], (peakTime - openTimeDT).seconds, el[2]])

    # print(f"{int(numOfNormalTrades / len(tradeData) * 100)} % of trades is OK in TPcalc")
    # print(f"{int(numOfTradesWithpeaks / len(tradeData) * 100)} % of trades have peaks in TPcalc")

    return overallPeaks


def extremumsParser(priceActionData, openPrice):
    peaksValues = []
    priceData = np.array([float(elem[0]) for elem in priceActionData])

    dist = len(priceData) / 8

    peaks, _ = find_peaks(priceData, height=openPrice, distance=dist, width=1)
    if len(peaks) > 0:
        for elem in peaks:
            peaksValues.append(priceActionData[elem])
    return [list(el) for el in peaksValues]


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
        if float(el[2]) <= 4:
            del peaks[index]
    for index, el in enumerate(peaks):
        if float(el[2]) <= 4:
            del peaks[index]
    for index, el in enumerate(peaks):
        if float(el[2]) <= 4:
            del peaks[index]
    return peaks


def tp_calculation(overallPeaks, coeffs, coeffsNumTrades):
    numOfTrades = {}
    chunks = {}

    for index in range(0, len(coeffs)):
        chunks[(int(index * 10))] = 0
        numOfTrades[(int(index * 10))] = 0
    for elem in overallPeaks:
        for el in chunks.keys():
            if elem[1] in range(el, el + 10):
                chunks[el] = chunks[el] + elem[2]
                numOfTrades[el] = numOfTrades[el] + 1

    sorted_chunks = sorted(chunks.keys())
    for el in chunks.keys():
        if numOfTrades[el] != 0:
            if numOfTrades[el] < 5:
                chunks[el] = 0
            else:
                chunks[el] = chunks[el] / numOfTrades[el]
    x_chunked_np = np.array([int(el) for el in sorted_chunks])
    y_chunked_np = np.array([float(chunks[el]) for el in sorted_chunks])

    y_smooth = smooth(y_chunked_np, 5)
    peaksSavGol, _ = find_peaks(y_smooth)
    # peaksSavGol = np.delete(peaksSavGol, np.argwhere(y_chunked_np[peaksSavGol] < 3))
    if len(peaksSavGol) != 0:
        diffList = []
        diffDict = []

        diffNormal = max(y_smooth[peaksSavGol]) / 5
        for index, el in enumerate(peaksSavGol):
            if index != len(peaksSavGol) - 1:
                diff = y_smooth[peaksSavGol[index]] - y_smooth[peaksSavGol[index + 1]]
            else:
                diff = diffNormal + 1
            if -diffNormal < diff < diffNormal:
                diffList.append(el)
            else:
                diffList.append(el)
                diffDict.append(diffList)
                diffList = []

        diffDict = [x for x in diffDict if x]

        ranges_borders = []
        for index, el in enumerate(diffDict):
            if index != len(diffDict) - 1:
                ranges_borders.append((el[-1] + diffDict[index + 1][0]) / 2)
            else:
                ranges_borders.append(max(x_chunked_np / 10))

        # profitList = [sum(y_chunked_np[el]) / len(el) for el in diffDict]
        profitList = [sum(y_smooth[el]) / len(el) for el in diffDict]

        profitListNorm = []
        diffDictNorm = []
        for index, el in enumerate(profitList):
            if index == len(profitList) - 1:
                profitListNorm.append(el)
                diffDictNorm.append(diffDict[index])
            elif el > profitList[index + 1]:
                profitListNorm.append(el)
                diffDictNorm.append(diffDict[index])

        TPtimeRanges = []
        for index, el in enumerate(diffDictNorm):
            if index == 0:
                startTime = 0
            else:
                startTime = ranges_borders[index - 1] * 10
            endTime = ranges_borders[index] * 10
            TPtimeRanges.append([int(startTime), int(endTime), round(profitListNorm[index] / 20, 2)])


        plotprofit(x_chunked_np, y_smooth, peaksSavGol,
                   coeffsNumTrades, ranges_borders)

        return TPtimeRanges
    elif len(peaksSavGol) == 0:
        take = max(y_smooth)
        TPtimeRanges = [[0, len(coeffs)*10, take]]
        return TPtimeRanges


def plotprofit(x_chunked_np,  y_smooth, peaksSavGol, coeffsNumTrades, ranges_borders):
    plt.vlines(x=[el * 10 for el in [el for el in ranges_borders]],
               ymin=0, ymax=max(y_smooth), colors='red')
    plt.bar(x_chunked_np, [el / 30 for el in coeffsNumTrades], width=8, color='grey')
    plt.plot(x_chunked_np, y_smooth, color='green')
    plt.plot([el * 10 for el in peaksSavGol], y_smooth[peaksSavGol], "x", color='red')
    plt.title("Profit on 10s chunks")
    plt.show()


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
