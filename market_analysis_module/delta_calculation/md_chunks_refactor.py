from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import stats

from tpsl_calculation.tp_calculation_ver3 import smooth


def data_processing(df):
    cols = ['dBTC ', 'd24BTC ', 'dMarket ', 'dM24 ', 'dBTC5m ', 'Pump1H ', 'Dump1H ', 'd24h ', 'd3h ',
            'd1h ', 'd15m ', 'd5m ', 'd1m ', 'dBTC1m ']
    start = datetime(1999, 1, 1)
    dateFormat = "%Y-%m-%d %H:%M:%S"
    chunkNum = 0
    dataChunks = {}
    tradesCount = 0
    chunkProfit = 0
    PMcount = {"Plus": 0, "Minus": 0}
    soloChunkDict = soloChunkDictCreate(cols)

    for index, trade in df.iterrows():
        tradeStart = datetime.strptime(trade["BuyDate "][:-1], dateFormat)
        tradeProfit = float(trade["Profit "])
        tradeDict = market_data_collect(trade, cols)
        if start == datetime(1999, 1, 1):
            start = tradeStart
        # print((tradeStart - start).total_seconds())
        if start != datetime(1999, 1, 1) and -((tradeStart - start).total_seconds()) <= 300:
            chunkProfit, soloChunkDict = addValuesToChunk(tradeProfit, tradeDict, soloChunkDict, chunkProfit)
            tradesCount, PMcount = tradeStatCounter(tradeProfit, tradesCount, PMcount)
        elif start != datetime(1999, 1, 1) and -((tradeStart - start).total_seconds()) >= 300:
            start = tradeStart
            dataChunks[chunkNum] = [chunkProfit, soloChunkDict, tradesCount, PMcount]
            chunkNum += 1
            tradesCount = 0
            chunkProfit = 0
            PMcount = {"Plus": 0, "Minus": 0}
            soloChunkDict = soloChunkDictCreate(cols)
    visualisation_chunks(dataChunks)


def delta_calculation(dataChunks):
    deltalist = []
    for index in dataChunks.keys():
        if index == 0:
            deltalist.append(dataChunks[index][1]['dBTC '])
        elif index != 0 and dataChunks[index-1][1]['dBTC '] != 0:
            delta = (dataChunks[index][1]['dBTC '] - dataChunks[index-1][1]['dBTC ']) / dataChunks[index-1][1]['dBTC ']
            deltalist.append(delta)
        elif index != 0 and dataChunks[index - 1][1]['dBTC '] == 0:
            deltalist.append(deltalist[-1])
    return deltalist


def visualisation_chunks(dataChunks):
    y_dBTC = [dataChunks[index][1]['d5m '] / dataChunks[index][2]
              for index in dataChunks.keys() if dataChunks[index][2] != 0]
    y_profit = [dataChunks[index][0] / dataChunks[index][2]
                for index in dataChunks.keys() if dataChunks[index][2] != 0]
    y_dBTC_diff = np.diff(y_dBTC)
    y_dBTC_diff = np.insert(y_dBTC_diff, 0, y_dBTC[0])
    y_dBTC_diff = [el*10 for el in y_dBTC_diff]
    plt.plot(smooth(y_profit[:100], 5), color="blue")
    plt.plot(smooth(y_dBTC_diff, 5)[:100], color='r')
    plt.show()
    correlation, p_value = stats.pearsonr(y_profit, y_dBTC_diff)
    print(correlation)


def tradeStatCounter(tradeProfit, tradesCount, PMcount):
    tradesCount += 1
    if tradeProfit >=0:
        PMcount["Plus"] += 1
    elif tradeProfit <= 0:
        PMcount["Minus"] +=1

    return tradesCount, PMcount


def addValuesToChunk(tradeProfit, tradeDict, soloChunkDict, chunkProfit):
    for key in soloChunkDict.keys():
        soloChunkDict[key] += tradeDict[key]
    chunkProfit += tradeProfit
    return chunkProfit, soloChunkDict


def soloChunkDictCreate(cols):
    chunkDict = {}
    for el in cols:
        chunkDict[el] = 0
    return chunkDict


def market_data_collect(trade, cols):
    tradeDict = {}
    for el in cols:
        tradeDict[el] = trade[el]
    return tradeDict


def plus_minus_counter(df):
    counts = df['Profit '].value_counts().to_dict()
    plus = 0
    minus = 0
    for el in counts.keys():
        if float(el[:-2]) > 0:
            plus += counts[el]
        elif float(el[:-2]) < 0:
            minus += counts[el]
    print(f'plus = {plus}\n'
          f'minus = {minus}\n')