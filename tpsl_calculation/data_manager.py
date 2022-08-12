from collections import Counter
from datetime import datetime

from tpsl_calculation.tp_calculation_ver3 import tp_TradeLevel_manager, tp_calculation
from tpsl_calculation.sl_calculation_ver3 import sl_TradeLevel_manager, sl_calculation


def dataPrepStratLevel(stratName, stratData, colNames, dateFormat, BuySellPrice):
    tradeData = stratData[1][stratName]
    return tradeData, colNames, dateFormat, BuySellPrice


def tpsl_StratLevel_manager_v3(stratData, colNames, BuySellPrice):
    optimalTPSLstrat = {}
    TP = {}
    dateFormat = "%Y-%m-%d %H:%M:%S"
    for stratName in stratData[1]:
        if len(stratData[1][stratName]) > 100:
            print(stratName)
            overallPeaks = tp_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, colNames, dateFormat,
                                                                     BuySellPrice))
            coeffs, coeffsNumTrades = analysis_time(*strat_time_range(stratName, stratData, colNames))
            TPtimeRanges = tp_calculation(overallPeaks, coeffs, coeffsNumTrades)
            print(TPtimeRanges)
            overallStops = sl_TradeLevel_manager(*dataPrepStratLevel(stratName, stratData, colNames, dateFormat,
                                                                     BuySellPrice), TPtimeRanges)
            SLtimeRanges = sl_calculation(overallStops, coeffs, coeffsNumTrades)
            print(SLtimeRanges)
            TP[stratName] = TPtimeRanges
    return TP


def strat_time_range(stratName, strategyDict, colNames):  # we return list with trade len(sec) for all trades in strat
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
    return list_trade_seconds, strategyDict[1][stratName].__len__()


def analysis_time(list_trade_seconds, strategyLen):
    list_trade_seconds_rounder = [int(round(x / 10.0) * 10.0) for x in list_trade_seconds]
    # round trade dur to closest 10
    freqs = Counter(list_trade_seconds_rounder)
    # count frequencies of trade lengths
    x = list(freqs.keys())  # all time that occur
    x_sorted = sorted(x)  # sorting of time values in increasing order
    y_sorted = []
    for el in x_sorted:
        y_sorted.append(freqs[el])  # we apply time frequencies to list in order like in x_sorted

    req_percent = 90  # percent of trades that we should cover in out overall time range
    percent = 0
    coeffs = []
    coeffsNumTrades = []
    for index, el in enumerate(x_sorted):
        max_len = el  # max len of our range
        if percent < req_percent:
            p_range = (y_sorted[index] / len(list_trade_seconds)) * 100  # percent of trades from strat in this range
            percent = percent + p_range  # sum percents
            coeffsNumTrades.append(round(strategyLen * p_range / 100))
            coeffs.append(p_range)  # coefficient of coverage of strat trades by this time range
        elif percent >= req_percent:  # if we fill our percent - end loop
            # print(f"cover trades from 0 to {max_len} s, index - {index}, "
            # f"percent of coverage is {percent}")
            break

    # plt.plot(x_sorted[:index_slice], y_sorted[:index_slice])
    # plt.show()
    return coeffs, coeffsNumTrades  # return coeffs for time ranges in increasing order
