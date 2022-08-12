import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from API_DB_pipeline.db_interaction.db_interaction import dbReceiveKlines, connectionDB
from tpsl_calculation.WWO_stop_calculation import WWO_combinations_generator
from tpsl_calculation.tp_calculation_ver3 import tradeDataPrep, tradeCheck, smooth


def plotLows(Wlows, WOlows, priceActionData, openPrice):
    priceActionData = np.array([float(elem[0]) for elem in priceActionData])
    plt.plot(np.array(range(0, len(priceActionData))), priceActionData)
    plt.axhline(y=openPrice, color='r', linestyle='-')
    plt.plot(Wlows, priceActionData[Wlows], "x", color='red')
    plt.plot(WOlows, priceActionData[WOlows], "x", color='black')
    plt.show()


def sl_TradeLevel_manager(tradeData, colNames, dateFormat, BuySellPrice, TPtimeRanges):
    overallStops = []
    numOfTradesWithlows = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        coin, openTimeDT, closeTimeDT, openPrice, closePrice, profit, optimisedName = \
            tradeDataPrep(trade, colNames, dateFormat, BuySellPrice)

        priceActionData = dbReceiveKlines(optimisedName, openTimeDT, closeTimeDT, *connectionDB())

        if tradeCheck(priceActionData, openTimeDT, closeTimeDT):
            numOfNormalTrades += 1
            if plusTradeCheck(priceActionData, openPrice):
                LowsPairsWithPeak, LowsWithoutPeaks, lows, peaks, numOfDeletedLows \
                    = lowsparser(priceActionData, openPrice)

                Wlows, WOlows, WpeaksValueIndex = WWOclassification(LowsPairsWithPeak, LowsWithoutPeaks, lows, peaks,
                                                                    priceActionData, openTimeDT, TPtimeRanges,
                                                                    openPrice)
                # plotLows(Wlows, WOlows, priceActionData, openPrice)
                if len(Wlows) > 0:
                    numOfTradesWithlows += 1
                stopTime = WWO_combinations_generator(Wlows, WOlows, priceActionData, openTimeDT,
                                                      TPtimeRanges, openPrice, lows, peaks, WpeaksValueIndex)
                if stopTime is not None:
                    if len(stopTime) > 0:
                        for el in stopTime:
                            overallStops.append(el)
            else:
                takeValue, takeReached = ifTradeReachTP(priceActionData, openPrice, TPtimeRanges, openTimeDT)
    # print(f"{int(numOfNormalTrades / len(tradeData) * 100)} % of trades is OK in SLcalc, {numOfNormalTrades}")

    return overallStops


def sl_calculation(overallStops, coeffs, coeffsNumTrades):
    numOfTrades = {}
    chunks = {}

    for index in range(0, len(coeffs)):
        chunks[(int(index * 10))] = 0
        numOfTrades[(int(index * 10))] = 0
    for elem in overallStops:
        for el in chunks.keys():
            if elem[1] in range(el, el + 10):
                chunks[el] = chunks[el] + elem[0]
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
    lowsSavGol, _ = find_peaks(-y_smooth)

    if len(lowsSavGol) != 0:
        diffList = []
        diffDict = []
        diffNormal = max(y_smooth[lowsSavGol]) / 5
        for index, el in enumerate(lowsSavGol):
            if index != len(lowsSavGol) - 1:
                diff = y_smooth[lowsSavGol[index]] - y_smooth[lowsSavGol[index + 1]]
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

        slListNorm = []
        diffDictNorm = []
        for index, el in enumerate(profitList):
            if index == len(profitList) - 1:
                slListNorm.append(el)
                diffDictNorm.append(diffDict[index])
            elif el > profitList[index + 1]:
                slListNorm.append(el)
                diffDictNorm.append(diffDict[index])

        SLtimeRanges = []
        for index, el in enumerate(diffDictNorm):
            if index == 0:
                startTime = 0
            else:
                startTime = ranges_borders[index - 1] * 10
            endTime = ranges_borders[index] * 10
            SLtimeRanges.append([int(startTime), int(endTime), round(slListNorm[index], 2)])

        plotstop(x_chunked_np, y_smooth, lowsSavGol,
                 coeffsNumTrades, ranges_borders)
        return SLtimeRanges
    elif len(lowsSavGol) == 0:
        stop = min(y_smooth)
        SLtimeRanges = [[0, len(coeffs)*10, stop]]
        return SLtimeRanges


def plotstop(x_chunked_np, y_smooth, lowsSavGol, coeffsNumTrades, ranges_borders):
    plt.vlines(x=[el * 10 for el in [el for el in ranges_borders]],
               ymin=0, ymax=max(y_smooth), colors='red')
    # plt.bar(x_chunked_np, [el / 30 for el in coeffsNumTrades], width=8, color='grey')
    plt.plot(x_chunked_np, y_smooth, color='green')
    plt.plot([el * 10 for el in lowsSavGol], y_smooth[lowsSavGol], "x", color='red')
    plt.title("Stop on 10s chunks")
    plt.show()


def plusTradeCheck(priceActionData, openPrice):
    StopPossible = False
    for el in priceActionData:
        if (float(el[0]) - float(openPrice)) / float(openPrice) * 100 < -0.1:
            StopPossible = True
        if StopPossible:
            return StopPossible
    return StopPossible


def ifTradeReachTP(priceActionData, openPrice, TPtimeRanges, openTimeDT):
    takeReached = False
    takeValue = 0
    currentPercent = TPtimeRanges[0][2]
    for el in priceActionData:
        currentTime = el[1] - openTimeDT
        for rangeTP in TPtimeRanges:
            if rangeTP[0] <= currentTime.total_seconds() <= rangeTP[1]:
                currentPercent = rangeTP[2]

        if (float(el[0]) - float(openPrice)) / float(openPrice) * 100 >= currentPercent:
            takeReached = True
            return takeValue, takeReached
    return takeValue, takeReached


def lowsparser(priceActionData, openPrice):
    priceActionData = np.array([float(elem[0]) for elem in priceActionData])
    numOfDeletedLows = 0
    dist = len(priceActionData) / 8
    peaks, _ = find_peaks(priceActionData, distance=dist, width=1)
    lows, _ = find_peaks(-priceActionData, distance=dist, width=1)

    for el in lows:
        if priceActionData[el] >= openPrice:
            lows = np.delete(lows, np.where(lows == el))
            numOfDeletedLows += 1

    LowsPairsWithPeak = lowsPairs(lows, peaks, priceActionData)
    if LowsPairsWithPeak is not None:
        LowsWithoutPeaks = lowsWithoutPeaks(lows, LowsPairsWithPeak)
    else:
        LowsWithoutPeaks = lows
    return LowsPairsWithPeak, LowsWithoutPeaks, lows, peaks, numOfDeletedLows


def lowsPairs(lows, peaks, priceActionData):
    LowsPairsWithPeak = []
    if lows.size != 0 and peaks.size != 0:
        for index, low in np.ndenumerate(lows):
            if index[0] != len(lows) - 1:
                suitable_peaks = [peak for peak in peaks if lows[index[0] + 1] > peak > low]
            else:
                suitable_peaks = [peak for peak in peaks if peak > low]
            if len(suitable_peaks) != 0:
                peak_prices = [float(priceActionData[el]) for el in suitable_peaks]
                peak = suitable_peaks[peak_prices.index(max(peak_prices))]
                LowsPairsWithPeak.append([low, peak])
        return LowsPairsWithPeak


def lowsWithoutPeaks(lows, LowsPairsWithPeak):
    lowsWithPeaks = [i[1] for i in LowsPairsWithPeak]
    return [i for i in lows if i not in lowsWithPeaks]


def WWOclassification(LowsPairs, LowsWithoutPeaks, lows, peaks, priceActionData, openTimeDT, TPtimeRanges, openPrice):
    Wlows = []
    WOlows = []
    LowPairsLows = []
    WpeaksValueIndex = {}
    peakAfterLowTime = 0
    peakAfterLowValue = 0
    if LowsPairs is not None:
        LowPairsLows = [el[0] for el in LowsPairs]
    for low in lows:
        if low in LowPairsLows:
            peakAfterLowValue = (float(priceActionData[LowsPairs[LowPairsLows.index(low)][1]][0]) -
                                 float(openPrice)) / float(openPrice) * 100
            peakAfterLowTime = (priceActionData[LowsPairs[LowPairsLows.index(low)][1]][1] - openTimeDT).total_seconds()
        elif LowsWithoutPeaks is not None and low in LowsWithoutPeaks:
            overallIndexLow = lows.tolist().index(low)
            if overallIndexLow != len(lows) - 1:
                peakAfterLow = max([float(el[0]) for el in priceActionData
                                    if lows[overallIndexLow + 1] > priceActionData.index(el) > low])
            else:
                peakAfterLow = max([float(el[0]) for el in priceActionData
                                    if priceActionData.index(el) > low])
                for el in priceActionData:
                    if float(el[0]) == peakAfterLow and priceActionData.index(el) > low:
                        peakAfterLowTime = (el[1] - openTimeDT).total_seconds()
            peakAfterLowValue = (peakAfterLow - float(openPrice)) / float(openPrice) * 100

        if peakAfterLowValue != 0 and peakAfterLowTime != 0:
            for el in TPtimeRanges:
                if peakAfterLowTime in range(el[0], el[1]):
                    if peakAfterLowValue >= el[2]:
                        Wlows.append(low)
                        WpeaksValueIndex[low] = round(peakAfterLowValue, 3)
                    else:
                        WOlows.append(low)

    return Wlows, WOlows, WpeaksValueIndex
