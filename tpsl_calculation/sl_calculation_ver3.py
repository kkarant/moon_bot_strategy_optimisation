from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy.signal import find_peaks

from tpsl_calculation.tp_calculation_ver3 import tradeDataPrep, tradeCheck


def sl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, colNames, dateFormat):
    indexDict = {}
    numOfTradesWithpeaks = 0
    numOfNormalTrades = 0
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    for trade in tradeData:
        coin, indexTrade, openTime, closeTime, openPrice, closePrice, profit = \
            tradeDataPrep(trade, colNames, indexDict, BuySellPrice)

        if tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat):
            numOfNormalTrades += 1
            lowsValues, lows = lowParser(TPSLdata[coin][indexTrade], openPrice)
            lows_list = lows.tolist()
            #lowsValues_list = lowsValues.tolist()
            plt.plot(lows_list, [float(el[0]) for el in lowsValues], "x")  # x marks the peaks we found

            lows, lowsValues = lowNormalise(TPSLdata[coin][indexTrade], lowsValues, lows, openPrice)
            if len(lowsValues) > 0:
                plt.plot(lows, [float(el[0]) for el in lowsValues], "x", color='red')

            plt.show()


def lowParser(priceActionData, openPrice):
    lowsValues = []
    priceData = np.array([float(elem[0]) for elem in priceActionData])

    dist = len(priceData) / 8
    plt.plot(priceData)
    lows, _ = find_peaks(-priceData, distance=dist, width=1, height=(None, openPrice))
    # profit plot

    if len(lows) > 0:
        for elem in lows:
            lowsValues.append(priceActionData[elem])
    return lowsValues, lows


def lowNormalise(priceActionData, lowsValues, lows, openPrice):
    lows_list = lows.tolist()
    if len(lows_list) > 0:
        for index, el in enumerate(lows_list):
            if index != len(lows_list) - 1:
                for el_pad in range(el, lows_list[index + 1]):
                    profit = (float(priceActionData[el_pad][0]) - float(openPrice)) / float(openPrice) * 100 * 20
                    if profit >= 3.5:
                        # print("stop is too low")
                        del lows_list[index]
                        del lowsValues[index]
                        break

    return lows_list, lowsValues
