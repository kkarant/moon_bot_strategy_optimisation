from collections import Counter
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from db_interaction.dataReceiver import receiveData
from tpsl_calculation.tp_calculation_ver3 import tp_TradeLevel_manager, plotProfits
from tpsl_calculation.sl_calculation_ver3 import sl_TradeLevel_manager
from strategy_statistics.strategyStatistics import averageTime


def dataPrepStratLevel(stratName, stratData, BuySellPrice, stratTPSLdata, dateFormat, colNames):
    tradeData = stratData[1][stratName]
    TPSLdata = stratTPSLdata[stratName]
    return tradeData, BuySellPrice, TPSLdata, colNames, dateFormat


def tpsl_StratLevel_manager_v3(stratData, colNames, BuySellPrice):
    TPSLdata, tradeNumList = receiveData(stratData)
    optimalTPSLstrat = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    stratList = ["(strategy <d180s1 M+>) "]
    for stratName in stratList:
        overallPeaks = tp_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata,
                                                                 dateFormat, colNames))
        histogram_time(strat_time_range(stratName, stratData, colNames), stratData)
        # plotProfits(overallPeaks)

        sl_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, BuySellPrice, TPSLdata,
                                                  dateFormat, colNames))
    return optimalTPSLstrat


def strat_time_range(stratName, strategyDict, colNames):
    list_trade_seconds = []
    openTimeCol = colNames.index('BuyDate ')
    closeTimeCol = colNames.index('CloseDate ')
    el = 0
    while el < (strategyDict[1][stratName]).__len__():
        openTime = strategyDict[1][stratName][el][1][openTimeCol][:-1]
        closeTime = strategyDict[1][stratName][el][1][closeTimeCol][:-1]
        openTimeConverted = datetime.strptime(openTime, "%Y-%m-%d %H:%M:%S")
        closeTimeConverted = datetime.strptime(closeTime, "%Y-%m-%d %H:%M:%S")

        time_interval = closeTimeConverted - openTimeConverted
        list_trade_seconds.append(time_interval.seconds)

        el = el + 1
    return list_trade_seconds


def histogram_time(list_trade_seconds, stratData):
    # list_trade_seconds_rounder = [int(round(x / 10.0) * 10.0) for x in list_trade_seconds]
    # df = pd.DataFrame({'freq': list_trade_seconds_rounder})
    # df.groupby('freq', as_index=False).size().plot(kind='bar')
    # plt.show()

    list_trade_seconds_rounder = [int(round(x / 10.0) * 10.0) for x in list_trade_seconds]
    freqs = Counter(list_trade_seconds_rounder)

    print(freqs)
    # df = pd.DataFrame.from_dict(freqs, orient='index')
    # df.plot(kind='bar')
    # plt.show()

    x = list(freqs.keys())
    y = list(freqs.values())
    x_sorted = sorted(x)
    y_sorted = []
    for el in x_sorted:
        y_sorted.append(freqs[el])
    plt.plot(x_sorted, y_sorted)
    plt.show()

    req_percent = 50
    percent = 0
    overall_trades = 0
    for stratName in stratData[1]:
        overall_trades = overall_trades + stratData[1][stratName].__len__()

    for el in x_sorted:
        max_len = el
        if percent < req_percent:
            percent = percent + ((freqs[el]/overall_trades)*100)
        elif percent >= req_percent:
            print(f"W cover trades from 0 to {max_len} s, percent of coverage is {percent}")
            break

