from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from scipy.signal import find_peaks

from tpsl_calculation.tp_calculation_ver3 import tradeDataPrep, tradeCheck


def sl_TradeLevel_manager(tradeData, BuySellPrice, TPSLdata, colNames, dateFormat):
    indexDict = {}
    for trade in tradeData:
        if trade[1][colNames.index('Coin ')][:-1] not in indexDict.keys():
            if trade[1][colNames.index('Coin ')][:-1] in TPSLdata.keys():
                indexDict[trade[1][colNames.index('Coin ')][:-1]] = 0
    for trade in tradeData:
        coin, indexTrade, openTime, closeTime, openPrice, closePrice, profit = \
            tradeDataPrep(trade, colNames, indexDict, BuySellPrice)

        if tradeCheck(TPSLdata[coin][indexTrade], openTime, closeTime, dateFormat):
            ...

# def lowParser():
#    pass
